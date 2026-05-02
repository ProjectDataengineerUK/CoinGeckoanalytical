from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = ("job_name", "status")
ALLOWED_STATUS_VALUES = {"SUCCESS", "FAILED", "CANCELLED", "RUNNING", "QUEUED", "PENDING"}


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
        raise ValueError("Bundle run payload must be a JSON object or array of JSON objects.")
    return [dict(item) for item in data]


def validate_bundle_run_row(row: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in row or row[field] in {None, ""}]
    if missing:
        raise ValueError(f"Missing required bundle run fields: {', '.join(missing)}")

    status = str(row["status"])
    if status not in ALLOWED_STATUS_VALUES:
        raise ValueError(f"Unsupported bundle run status value: {status}")

    normalized = dict(row)
    normalized["job_name"] = str(row["job_name"])
    normalized["status"] = status
    normalized["run_id"] = row.get("run_id")
    normalized["result_state"] = row.get("result_state")
    normalized["update_time"] = row.get("update_time")
    normalized["duration_ms"] = _coerce_optional_int(row.get("duration_ms"))
    return normalized


def normalize_bundle_run_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [validate_bundle_run_row(row) for row in rows]


def write_bundle_run_rows(
    spark: Any,
    rows: list[dict[str, Any]],
    target_table: str = "ops_bundle_runs",
) -> IngestionResult:
    normalized_rows = normalize_bundle_run_rows(rows)
    if not normalized_rows:
        return IngestionResult(rows_written=0, target_table=target_table)

    dataframe = spark.createDataFrame(normalized_rows)
    dataframe.write.mode("append").format("delta").saveAsTable(target_table)
    return IngestionResult(rows_written=len(normalized_rows), target_table=target_table)


def main(
    spark: Any,
    payload_json: str | None = None,
    payload_path: str | None = None,
    target_table: str = "ops_bundle_runs",
) -> IngestionResult:
    rows = parse_payload(payload_json, payload_path=payload_path)
    return write_bundle_run_rows(spark, rows, target_table=target_table)


def _coerce_optional_int(value: Any) -> int | None:
    if value in {None, ""}:
        return None
    return int(value)


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
        widgets["target_table"] = "ops_bundle_runs"

    result = main(
        spark_session,
        payload_json=widgets["payload_json"],
        payload_path=widgets["payload_path"],
        target_table=widgets["target_table"] or "ops_bundle_runs",
    )
    print(json.dumps({"rows_written": result.rows_written, "target_table": result.target_table}))
