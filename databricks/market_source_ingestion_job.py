from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


REQUIRED_FIELDS = (
    "source_system",
    "source_record_id",
    "asset_id",
    "symbol",
    "name",
    "category",
    "observed_at",
    "ingested_at",
    "market_cap_usd",
    "price_usd",
    "volume_24h_usd",
    "circulating_supply",
    "market_cap_rank",
    "payload_version",
)

ALLOWED_SOURCE_SYSTEMS = {"coingecko_api", "internal_reference", "partner_feed"}


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
        raise ValueError("Market payload must be a JSON object or an array of JSON objects.")
    return [dict(item) for item in data]


def normalize_market_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)

    asset_id = row.get("asset_id") or row.get("id")
    symbol = row.get("symbol")
    observed_at = row.get("observed_at") or row.get("last_updated")

    if not asset_id:
        raise ValueError("Market row is missing asset_id/id.")
    if not symbol:
        raise ValueError("Market row is missing symbol.")
    if not observed_at:
        raise ValueError("Market row is missing observed_at/last_updated.")

    normalized["source_system"] = str(row.get("source_system") or "coingecko_api")
    normalized["asset_id"] = str(asset_id)
    normalized["symbol"] = str(symbol).upper()
    normalized["name"] = str(row.get("name") or "unmapped")
    normalized["category"] = str(row.get("category") or "unclassified")
    normalized["observed_at"] = str(observed_at)
    normalized["ingested_at"] = str(row.get("ingested_at") or _utc_now_isoformat())
    normalized["market_cap_usd"] = _coerce_required_float(
        row.get("market_cap_usd", row.get("market_cap"))
    )
    normalized["price_usd"] = _coerce_required_float(
        row.get("price_usd", row.get("current_price"))
    )
    normalized["volume_24h_usd"] = _coerce_required_float(
        row.get("volume_24h_usd", row.get("total_volume"))
    )
    normalized["circulating_supply"] = _coerce_required_float(row.get("circulating_supply"))
    normalized["market_cap_rank"] = _coerce_required_int(row.get("market_cap_rank"))
    normalized["payload_version"] = str(row.get("payload_version") or "coingecko_markets_v1")
    normalized["source_record_id"] = str(
        row.get("source_record_id") or f"{normalized['asset_id']}:{normalized['observed_at']}"
    )

    return validate_market_row(normalized)


def validate_market_row(row: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in row or row[field] in {None, ""}]
    if missing:
        raise ValueError(f"Missing required market fields: {', '.join(missing)}")

    source_system = str(row["source_system"])
    if source_system not in ALLOWED_SOURCE_SYSTEMS:
        raise ValueError(f"Unsupported source_system value: {source_system}")

    normalized = dict(row)
    normalized["source_system"] = source_system
    normalized["source_record_id"] = str(row["source_record_id"])
    normalized["asset_id"] = str(row["asset_id"])
    normalized["symbol"] = str(row["symbol"]).upper()
    normalized["name"] = str(row["name"])
    normalized["category"] = str(row["category"])
    normalized["observed_at"] = str(row["observed_at"])
    normalized["ingested_at"] = str(row["ingested_at"])
    normalized["market_cap_usd"] = _coerce_required_float(row["market_cap_usd"])
    normalized["price_usd"] = _coerce_required_float(row["price_usd"])
    normalized["volume_24h_usd"] = _coerce_required_float(row["volume_24h_usd"])
    normalized["circulating_supply"] = _coerce_required_float(row["circulating_supply"])
    normalized["market_cap_rank"] = _coerce_required_int(row["market_cap_rank"])
    normalized["payload_version"] = str(row["payload_version"])
    return normalized


def normalize_market_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [normalize_market_row(row) for row in rows]


def write_market_rows(
    spark: Any,
    rows: list[dict[str, Any]],
    target_table: str = "bronze_market_snapshots",
) -> IngestionResult:
    normalized_rows = normalize_market_rows(rows)
    if not normalized_rows:
        return IngestionResult(rows_written=0, target_table=target_table)

    dataframe = spark.createDataFrame(normalized_rows)
    dataframe.write.mode("append").format("delta").saveAsTable(target_table)
    return IngestionResult(rows_written=len(normalized_rows), target_table=target_table)


def main(
    spark: Any,
    payload_json: str | None = None,
    payload_path: str | None = None,
    target_table: str = "bronze_market_snapshots",
) -> IngestionResult:
    rows = parse_payload(payload_json, payload_path=payload_path)
    return write_market_rows(spark, rows, target_table=target_table)


def _coerce_required_float(value: Any) -> float:
    if value in {None, ""}:
        raise ValueError("Required numeric market field is missing.")
    return float(value)


def _coerce_required_int(value: Any) -> int:
    if value in {None, ""}:
        raise ValueError("Required integer market field is missing.")
    return int(value)


def _utc_now_isoformat() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_runtime_args(argv: list[str]) -> dict[str, str | None]:
    parsed: dict[str, str | None] = {
        "payload_json": None,
        "payload_path": None,
        "target_table": None,
    }
    index = 0
    while index < len(argv):
        current = argv[index]
        if current == "--payload-json" and index + 1 < len(argv):
            parsed["payload_json"] = argv[index + 1]
            index += 2
            continue
        if current == "--payload-path" and index + 1 < len(argv):
            parsed["payload_path"] = argv[index + 1]
            index += 2
            continue
        if current == "--target-table" and index + 1 < len(argv):
            parsed["target_table"] = argv[index + 1]
            index += 2
            continue
        index += 1
    return parsed


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
        widgets["target_table"] = "bronze_market_snapshots"

    runtime_args = parse_runtime_args(sys.argv[1:])

    result = main(
        spark_session,
        payload_json=widgets["payload_json"] or runtime_args["payload_json"],
        payload_path=widgets["payload_path"] or runtime_args["payload_path"],
        target_table=widgets["target_table"] or runtime_args["target_table"] or "bronze_market_snapshots",
    )
    print(json.dumps({"rows_written": result.rows_written, "target_table": result.target_table}))
