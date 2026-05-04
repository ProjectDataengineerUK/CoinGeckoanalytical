from __future__ import annotations

import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

DEFAULT_CATALOG = os.environ.get("COINGECKO_CATALOG", "cgadev")
PSI_THRESHOLD = 0.2


@dataclass(frozen=True)
class DriftResult:
    psi_score: float
    alert_written: bool
    regime_distribution_24h: dict
    regime_distribution_7d: dict


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


def main(spark: Any, catalog: str = DEFAULT_CATALOG) -> DriftResult:
    scores_table = f"{catalog}.market_gold.gold_ml_scores"
    alerts_table = f"{catalog}.ops_observability.ops_sentinela_alerts"

    rows_24h = [r.asDict() for r in spark.sql(
        f"SELECT predicted_regime FROM {scores_table} "
        f"WHERE scored_at >= CURRENT_TIMESTAMP() - INTERVAL 24 HOURS"
    ).collect()]

    rows_7d = [r.asDict() for r in spark.sql(
        f"SELECT predicted_regime FROM {scores_table} "
        f"WHERE scored_at >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS"
    ).collect()]

    dist_24h = compute_regime_distribution(rows_24h)
    dist_7d = compute_regime_distribution(rows_7d)
    psi = compute_psi(dist_7d, dist_24h) if dist_7d and dist_24h else 0.0
    alert_written = False

    if psi >= PSI_THRESHOLD:
        alert_row = {
            "alert_id": f"model_drift_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "alert_type": "model_drift",
            "severity": "warning",
            "message": f"Regime PSI={psi:.3f} exceeds threshold {PSI_THRESHOLD}",
            "context_json": str({"dist_24h": dist_24h, "dist_7d": dist_7d}),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        spark.createDataFrame([alert_row]).write.mode("append").format("delta").saveAsTable(alerts_table)
        alert_written = True

    return DriftResult(psi_score=psi, alert_written=alert_written,
                       regime_distribution_24h=dist_24h, regime_distribution_7d=dist_7d)


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:
        raise RuntimeError("Run inside Databricks.") from exc
    _r = main(spark_session)
    import json
    print(json.dumps({"psi_score": _r.psi_score, "alert_written": _r.alert_written}))
