from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

DEFAULT_DEFILLAMA_PROTOCOLS_URL = "https://api.llama.fi/protocols"
DEFAULT_TARGET_TABLE = "cgadev.market_bronze.bronze_defillama_protocols"

REQUIRED_FIELDS = (
    "source_system",
    "source_record_id",
    "protocol_slug",
    "protocol_name",
    "tvl_usd",
    "observed_at",
    "ingested_at",
    "payload_version",
)


@dataclass(frozen=True)
class IngestionResult:
    rows_written: int
    target_table: str


def fetch_protocols(url: str = DEFAULT_DEFILLAMA_PROTOCOLS_URL, max_retries: int = 3) -> list[dict[str, Any]]:
    attempt = 0
    while True:
        try:
            request = urllib.request.Request(url, headers={"accept": "application/json"}, method="GET")
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data if isinstance(data, list) else []
        except urllib.error.HTTPError as exc:
            attempt += 1
            if exc.code not in {429, 500, 502, 503, 504} or attempt >= max_retries:
                body = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"DefiLlama request failed: {exc.code} {body}") from exc
            time.sleep(attempt * 2.0)
        except urllib.error.URLError as exc:
            attempt += 1
            if attempt >= max_retries:
                raise RuntimeError(f"DefiLlama request failed: {exc.reason}") from exc
            time.sleep(attempt * 2.0)


def normalize_protocol_row(raw: dict[str, Any]) -> dict[str, Any] | None:
    slug = raw.get("slug") or raw.get("name", "").lower().replace(" ", "-")
    if not slug:
        return None

    tvl = raw.get("tvl")
    if tvl is None:
        return None

    try:
        tvl_float = float(tvl)
    except (TypeError, ValueError):
        return None

    fees_24h = _safe_float(raw.get("fees") or (raw.get("feesHistory") or [None])[-1])
    revenue_24h = _safe_float(raw.get("revenue") or (raw.get("revenueHistory") or [None])[-1])

    mcap = _safe_float(raw.get("mcap"))
    mcap_tvl = round(mcap / tvl_float, 6) if mcap and tvl_float > 0 else None

    now = _utc_now_isoformat()
    return {
        "source_system": "defillama",
        "source_record_id": slug,
        "protocol_slug": slug,
        "protocol_name": str(raw.get("name") or slug),
        "chain": str(raw.get("chain") or raw.get("chains", ["unknown"])[0] if raw.get("chains") else "unknown"),
        "category": str(raw.get("category") or "unclassified"),
        "tvl_usd": tvl_float,
        "fees_24h_usd": fees_24h,
        "revenue_24h_usd": revenue_24h,
        "mcap_tvl_ratio": mcap_tvl,
        "observed_at": str(raw.get("last_updated") or now),
        "ingested_at": now,
        "payload_version": "defillama_protocols_v1",
    }


def normalize_protocol_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for row in rows:
        result = normalize_protocol_row(row)
        if result is not None:
            normalized.append(result)
    return normalized


def write_protocol_rows(
    spark: Any,
    rows: list[dict[str, Any]],
    target_table: str = DEFAULT_TARGET_TABLE,
) -> IngestionResult:
    normalized = normalize_protocol_rows(rows)
    if not normalized:
        return IngestionResult(rows_written=0, target_table=target_table)

    df = spark.createDataFrame(normalized)
    df = df.dropDuplicates(["source_system", "source_record_id"])
    df.write.mode("append").format("delta").saveAsTable(target_table)
    return IngestionResult(rows_written=df.count(), target_table=target_table)


def main(
    spark: Any,
    target_table: str = DEFAULT_TARGET_TABLE,
    protocols_url: str = DEFAULT_DEFILLAMA_PROTOCOLS_URL,
    skip_live: bool = False,
) -> IngestionResult:
    if skip_live:
        print("Skipping DefiLlama fetch: --skip-live flag active.")
        return IngestionResult(rows_written=0, target_table=target_table)
    rows = fetch_protocols(protocols_url)
    return write_protocol_rows(spark, rows, target_table=target_table)


def parse_runtime_args(argv: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {"target_table": None, "skip_live": False}
    index = 0
    while index < len(argv):
        if argv[index] == "--target-table" and index + 1 < len(argv):
            parsed["target_table"] = argv[index + 1]
            index += 2
            continue
        if argv[index] == "--skip-live":
            parsed["skip_live"] = True
            index += 1
            continue
        index += 1
    return parsed


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _utc_now_isoformat() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    widgets: dict[str, Any] = {}
    try:
        widgets["target_table"] = dbutils.widgets.get("target_table")  # type: ignore[name-defined]
    except Exception:
        widgets["target_table"] = DEFAULT_TARGET_TABLE

    runtime_args = parse_runtime_args(sys.argv[1:])
    target = widgets["target_table"] or runtime_args["target_table"] or DEFAULT_TARGET_TABLE

    result = main(spark_session, target_table=target, skip_live=runtime_args["skip_live"])
    print(json.dumps({"rows_written": result.rows_written, "target_table": result.target_table}))
