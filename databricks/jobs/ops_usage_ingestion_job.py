from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

DEFAULT_OPS_SCHEMA = "ops_observability"


def _qual(name: str) -> str:
    cat = os.environ.get("COINGECKO_OPS_CATALOG") or os.environ.get("COINGECKO_CATALOG", "cgadev")
    return f"{cat}.{DEFAULT_OPS_SCHEMA}.{name}"


REQUIRED_FIELDS = (
    "event_time",
    "request_id",
    "tenant_id",
    "route_selected",
    "model_or_engine",
    "latency_ms",
    "response_status",
)

ALLOWED_ROUTE_VALUES = {"genie", "copilot", "dashboard_api", "internal_app"}
ALLOWED_STATUS_VALUES = {"success", "partial", "refused", "error"}


@dataclass(frozen=True)
class IngestionResult:
    rows_written: int
    target_table: str


def parse_payload(payload_json: str | None, payload_path: str | None = None) -> list[dict[str, Any]]:
    if payload_json:
        data = json.loads(payload_json)
    elif payload_path:
        with open(payload_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    else:
        data = []

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("Telemetry payload must be a JSON object or an array of JSON objects.")
    return [dict(item) for item in data]


def validate_usage_row(row: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in row or row[field] in {None, ""}]
    if missing:
        raise ValueError(f"Missing required telemetry fields: {', '.join(missing)}")

    route_selected = str(row["route_selected"])
    if route_selected not in ALLOWED_ROUTE_VALUES:
        raise ValueError(f"Unsupported route_selected value: {route_selected}")

    response_status = str(row["response_status"])
    if response_status not in ALLOWED_STATUS_VALUES:
        raise ValueError(f"Unsupported response_status value: {response_status}")

    normalized = dict(row)
    normalized["route_selected"] = route_selected
    normalized["response_status"] = response_status
    normalized["latency_ms"] = int(row["latency_ms"])
    normalized["prompt_tokens"] = _coerce_optional_int(row.get("prompt_tokens"))
    normalized["completion_tokens"] = _coerce_optional_int(row.get("completion_tokens"))
    normalized["total_tokens"] = _coerce_optional_int(row.get("total_tokens"))
    normalized["cost_estimate"] = _coerce_optional_float(row.get("cost_estimate"))
    normalized["user_id"] = row.get("user_id")
    normalized["freshness_watermark"] = row.get("freshness_watermark")
    return normalized


def normalize_usage_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [validate_usage_row(row) for row in rows]


def write_usage_rows(
    spark: Any,
    rows: list[dict[str, Any]],
    target_table: str | None = None,
) -> IngestionResult:
    if target_table is None:
        target_table = _qual("ops_usage_events")
    normalized_rows = normalize_usage_rows(rows)
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
    return write_usage_rows(spark, rows, target_table=target_table)


def _coerce_optional_int(value: Any) -> int | None:
    if value in {None, ""}:
        return None
    return int(value)


def _coerce_optional_float(value: Any) -> float | None:
    if value in {None, ""}:
        return None
    return float(value)


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
