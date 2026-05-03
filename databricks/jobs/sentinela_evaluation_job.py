from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

DEFAULT_OPS_SCHEMA = "ops_observability"
DEFAULT_LOOKBACK_HOURS = 1

THRESHOLD_ERROR_RATE_PCT = 10.0
THRESHOLD_P95_LATENCY_MS = 5000
THRESHOLD_HOURLY_COST_USD = 1.0


def _qual(name: str) -> str:
    cat = os.environ.get("COINGECKO_OPS_CATALOG") or os.environ.get("COINGECKO_CATALOG", "cgadev")
    return f"{cat}.{DEFAULT_OPS_SCHEMA}.{name}"


@dataclass(frozen=True)
class EvaluationResult:
    alerts_written: int
    usage_rows_read: int
    bundle_rows_read: int
    target_table: str


def _alert(kind: str, message: str, **kwargs: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "kind": kind,
        "message": message,
        "source": "sentinela_evaluation_job",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    row.update(kwargs)
    return row


def evaluate_usage_events(
    rows: list[dict[str, Any]],
    threshold_error_rate_pct: float = THRESHOLD_ERROR_RATE_PCT,
    threshold_p95_latency_ms: int = THRESHOLD_P95_LATENCY_MS,
    threshold_hourly_cost_usd: float = THRESHOLD_HOURLY_COST_USD,
) -> list[dict[str, Any]]:
    if not rows:
        return []

    alerts: list[dict[str, Any]] = []
    total = len(rows)
    errors = sum(1 for r in rows if r.get("response_status") not in {"success", "partial"})
    error_rate = (errors / total) * 100.0 if total else 0.0

    if error_rate > threshold_error_rate_pct:
        alerts.append(_alert(
            "error_spike",
            f"Error rate {error_rate:.1f}% exceeds threshold {threshold_error_rate_pct}% "
            f"({errors}/{total} requests in window).",
        ))

    latencies = sorted(r["latency_ms"] for r in rows if isinstance(r.get("latency_ms"), int))
    if latencies:
        p95_idx = max(0, int(len(latencies) * 0.95) - 1)
        p95 = latencies[p95_idx]
        if p95 > threshold_p95_latency_ms:
            alerts.append(_alert(
                "latency_breach",
                f"P95 latency {p95}ms exceeds threshold {threshold_p95_latency_ms}ms.",
            ))

    total_cost = sum(float(r["cost_estimate"]) for r in rows if r.get("cost_estimate") is not None)
    if total_cost > threshold_hourly_cost_usd:
        alerts.append(_alert(
            "cost_anomaly",
            f"Hourly cost ${total_cost:.4f} exceeds threshold ${threshold_hourly_cost_usd:.2f}.",
        ))

    return alerts


def evaluate_bundle_runs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []

    alerts: list[dict[str, Any]] = []
    for row in rows:
        status = str(row.get("status", "")).upper()
        job_name = str(row.get("job_name", "unknown"))
        run_id = row.get("run_id")
        if status == "FAILED":
            alerts.append(_alert(
                "bundle_failure",
                f"Job {job_name} run {run_id} failed.",
                job_name=job_name,
                run_id=run_id,
            ))
        elif status == "CANCELLED":
            alerts.append(_alert(
                "bundle_cancelled",
                f"Job {job_name} run {run_id} was cancelled.",
                job_name=job_name,
                run_id=run_id,
            ))

    return alerts


def write_alerts(spark: Any, alerts: list[dict[str, Any]], target_table: str | None = None) -> int:
    if not alerts:
        return 0
    if target_table is None:
        target_table = _qual("ops_sentinela_alerts")
    df = spark.createDataFrame(alerts)
    df.write.mode("append").format("delta").saveAsTable(target_table)
    return len(alerts)


def main(
    spark: Any,
    lookback_hours: int = DEFAULT_LOOKBACK_HOURS,
    alert_table: str | None = None,
) -> EvaluationResult:
    catalog = os.environ.get("COINGECKO_OPS_CATALOG") or os.environ.get("COINGECKO_CATALOG", "cgadev")
    usage_table = f"{catalog}.{DEFAULT_OPS_SCHEMA}.ops_usage_events"
    bundle_table = f"{catalog}.{DEFAULT_OPS_SCHEMA}.ops_bundle_runs"

    try:
        usage_rows: list[dict[str, Any]] = (
            spark.sql(
                f"SELECT response_status, latency_ms, cost_estimate "
                f"FROM {usage_table} "
                f"WHERE event_time >= CURRENT_TIMESTAMP - INTERVAL {lookback_hours} HOURS"
            )
            .toPandas()
            .to_dict(orient="records")
        )
    except Exception:
        usage_rows = []

    try:
        bundle_rows: list[dict[str, Any]] = (
            spark.sql(
                f"SELECT job_name, status, run_id "
                f"FROM {bundle_table} "
                f"WHERE ingested_at >= CURRENT_TIMESTAMP - INTERVAL {lookback_hours} HOURS"
            )
            .toPandas()
            .to_dict(orient="records")
        )
    except Exception:
        bundle_rows = []

    alerts = evaluate_usage_events(usage_rows) + evaluate_bundle_runs(bundle_rows)
    written = write_alerts(spark, alerts, target_table=alert_table)

    return EvaluationResult(
        alerts_written=written,
        usage_rows_read=len(usage_rows),
        bundle_rows_read=len(bundle_rows),
        target_table=alert_table or _qual("ops_sentinela_alerts"),
    )


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:  # pragma: no cover
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    widgets: dict[str, Any] = {}
    try:
        widgets["lookback_hours"] = int(dbutils.widgets.get("lookback_hours"))  # type: ignore[name-defined]
    except Exception:  # pragma: no cover
        widgets["lookback_hours"] = DEFAULT_LOOKBACK_HOURS

    result = main(spark_session, lookback_hours=widgets["lookback_hours"])
    print(json.dumps({
        "alerts_written": result.alerts_written,
        "usage_rows_read": result.usage_rows_read,
        "bundle_rows_read": result.bundle_rows_read,
        "target_table": result.target_table,
    }))
