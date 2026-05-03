from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_OPS_SCHEMA = "ops_observability"


def _qual(name: str) -> str:
    cat = os.environ.get("COINGECKO_OPS_CATALOG") or os.environ.get("COINGECKO_CATALOG", "cgadev")
    return f"{cat}.{DEFAULT_OPS_SCHEMA}.{name}"


REQUIRED_FIELDS = ("kind", "message")
ALLOWED_KINDS = {
    "error_spike",
    "latency_breach",
    "cost_anomaly",
    "freshness_gap",
    "token_spike",
    "bundle_failure",
    "bundle_cancelled",
}


@dataclass(frozen=True)
class IngestionResult:
    rows_written: int
    target_table: str


def parse_payload(payload_json: str | None, payload_path: str | None = None) -> list[dict[str, Any]]:
    if payload_json:
        data = json.loads(payload_json)
    elif payload_path:
        data = json.loads(Path(payload_path).read_text(encoding="utf-8"))
    else:
        data = []

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("Alert payload must be a JSON object or array of JSON objects.")
    return [dict(item) for item in data]


def validate_alert_row(row: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in row or row[field] in {None, ""}]
    if missing:
        raise ValueError(f"Missing required alert fields: {', '.join(missing)}")

    kind = str(row["kind"])
    if kind not in ALLOWED_KINDS:
        raise ValueError(f"Unsupported alert kind value: {kind}")

    normalized = dict(row)
    normalized["kind"] = kind
    normalized["message"] = str(row["message"])
    normalized["request_id"] = row.get("request_id")
    normalized["tenant_id"] = row.get("tenant_id")
    normalized["route_selected"] = row.get("route_selected")
    normalized["job_name"] = row.get("job_name")
    normalized["run_id"] = row.get("run_id")
    normalized["escalation"] = row.get("escalation")
    normalized["source"] = row.get("source") or "sentinela"
    normalized["created_at"] = row.get("created_at")
    return normalized


def normalize_alert_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [validate_alert_row(row) for row in rows]


def write_alert_rows(
    spark: Any,
    rows: list[dict[str, Any]],
    target_table: str | None = None,
) -> IngestionResult:
    if target_table is None:
        target_table = _qual("ops_sentinela_alerts")
    normalized_rows = normalize_alert_rows(rows)
    if not normalized_rows:
        return IngestionResult(rows_written=0, target_table=target_table)

    dataframe = spark.createDataFrame(normalized_rows)
    dataframe.write.mode("append").format("delta").saveAsTable(target_table)
    return IngestionResult(rows_written=len(normalized_rows), target_table=target_table)


def main(
    spark: Any,
    payload_json: str | None = None,
    payload_path: str | None = None,
    target_table: str | None = None,
) -> IngestionResult:
    rows = parse_payload(payload_json, payload_path=payload_path)
    return write_alert_rows(spark, rows, target_table=target_table)


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:  # pragma: no cover - Databricks runtime entrypoint only
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    widgets = {}
    try:
        widgets["payload_json"] = dbutils.widgets.get("payload_json")  # type: ignore[name-defined]
    except Exception:  # pragma: no cover - Databricks widget fallback
        widgets["payload_json"] = None
    try:
        widgets["payload_path"] = dbutils.widgets.get("payload_path")  # type: ignore[name-defined]
    except Exception:  # pragma: no cover - Databricks widget fallback
        widgets["payload_path"] = None
    try:
        widgets["target_table"] = dbutils.widgets.get("target_table")  # type: ignore[name-defined]
    except Exception:  # pragma: no cover - Databricks widget fallback
        widgets["target_table"] = None

    result = main(
        spark_session,
        payload_json=widgets["payload_json"],
        payload_path=widgets["payload_path"],
        target_table=widgets["target_table"] or None,
    )
    print(json.dumps({"rows_written": result.rows_written, "target_table": result.target_table}))
