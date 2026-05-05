from __future__ import annotations

import math
import os
import urllib.parse
import urllib.request
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

DEFAULT_CATALOG = os.environ.get("COINGECKO_CATALOG", "cgadev")
PSI_THRESHOLD = 0.2
CONSECUTIVE_DRIFT_RETRAIN_THRESHOLD = 3


@dataclass(frozen=True)
class DriftResult:
    psi_score: float
    alert_written: bool
    regime_distribution_24h: dict
    regime_distribution_7d_baseline: dict


def compute_regime_distribution(rows: list[dict[str, Any]]) -> dict[str, float]:
    if not rows:
        return {}
    counts: dict[str, int] = {}
    for row in rows:
        label = str(row.get("predicted_regime", "unknown"))
        counts[label] = counts.get(label, 0) + 1
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()}


def compute_psi(baseline: dict[str, float], current: dict[str, float]) -> float:
    all_labels = set(baseline) | set(current)
    psi = 0.0
    for label in all_labels:
        e = max(baseline.get(label, 0.001), 1e-9)
        a = max(current.get(label, 0.001), 1e-9)
        psi += (a - e) * math.log(a / e)
    return round(psi, 6)


def _dispatch_slack(message: str) -> None:
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook_url:
        return
    try:
        payload = json.dumps({"text": f":warning: *CoinGeckoAnalytical Drift Alert*\n{message}"}).encode()
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def main(spark: Any, catalog: str = DEFAULT_CATALOG) -> DriftResult:
    scores_table = f"{catalog}.market_gold.gold_ml_scores"
    alerts_table = f"{catalog}.ops_observability.ops_sentinela_alerts"

    # BUG-06 fix: use non-overlapping windows — 24h is current, 7d-1d is baseline
    rows_24h = [r.asDict() for r in spark.sql(
        f"SELECT predicted_regime FROM {scores_table} "
        f"WHERE scored_at >= CURRENT_TIMESTAMP() - INTERVAL 24 HOURS"
    ).collect()]

    rows_7d_baseline = [r.asDict() for r in spark.sql(
        f"SELECT predicted_regime FROM {scores_table} "
        f"WHERE scored_at >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS "
        f"AND scored_at < CURRENT_TIMESTAMP() - INTERVAL 1 DAY"
    ).collect()]

    dist_24h = compute_regime_distribution(rows_24h)
    dist_7d_baseline = compute_regime_distribution(rows_7d_baseline)
    psi = compute_psi(dist_7d_baseline, dist_24h) if dist_7d_baseline and dist_24h else 0.0
    alert_written = False

    if psi >= PSI_THRESHOLD:
        now_str = datetime.now(timezone.utc).isoformat()
        alert_message = (
            f"Regime PSI={psi:.3f} exceeds threshold {PSI_THRESHOLD} "
            f"(24h distribution vs 7d-1d baseline, non-overlapping windows). "
            f"dist_24h={dist_24h}, dist_baseline={dist_7d_baseline}"
        )
        # BUG-02 fix: use canonical DDL schema (kind, message, source, created_at)
        alert_row = {
            "kind": "model_drift",
            "message": alert_message,
            "source": "model_drift_monitoring_job",
            "created_at": now_str,
        }
        spark.createDataFrame([alert_row]).write.mode("append").format("delta").saveAsTable(alerts_table)
        alert_written = True

        # D1: dispatch external alert
        _dispatch_slack(alert_message)

        # M5: detect consecutive drift to trigger retrain signal
        try:
            recent_breach_count = spark.sql(
                f"SELECT COUNT(*) AS cnt FROM {alerts_table} "
                f"WHERE kind = 'model_drift' "
                f"AND created_at >= CURRENT_TIMESTAMP() - INTERVAL {CONSECUTIVE_DRIFT_RETRAIN_THRESHOLD} DAYS"
            ).collect()[0][0]
            if recent_breach_count >= CONSECUTIVE_DRIFT_RETRAIN_THRESHOLD:
                retrain_row = {
                    "kind": "retrain_trigger",
                    "message": (
                        f"Sustained regime drift detected: {recent_breach_count} PSI breaches "
                        f"in last {CONSECUTIVE_DRIFT_RETRAIN_THRESHOLD} days. "
                        "Manual or automated retraining recommended."
                    ),
                    "source": "model_drift_monitoring_job",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                spark.createDataFrame([retrain_row]).write.mode("append").format("delta").saveAsTable(alerts_table)
                _dispatch_slack(retrain_row["message"])
        except Exception:
            pass

    return DriftResult(
        psi_score=psi,
        alert_written=alert_written,
        regime_distribution_24h=dist_24h,
        regime_distribution_7d_baseline=dist_7d_baseline,
    )


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:
        raise RuntimeError("Run inside Databricks.") from exc
    _r = main(spark_session)
    print(json.dumps({"psi_score": _r.psi_score, "alert_written": _r.alert_written}))
