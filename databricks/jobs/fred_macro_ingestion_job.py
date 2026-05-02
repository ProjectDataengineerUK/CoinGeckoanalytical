from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

DEFAULT_TARGET_TABLE = "cgadev.market_bronze.bronze_fred_macro"
FRED_API_BASE = "https://api.stlouisfed.org/fred/series/observations"

FRED_SERIES = {
    "DGS10":    "10yr_treasury_yield",
    "M2SL":     "m2_money_supply",
    "CPIAUCSL": "cpi_inflation",
    "DTWEXBGS": "usd_trade_index",
}


@dataclass(frozen=True)
class IngestionResult:
    rows_written: int
    target_table: str


def build_fred_url(series_id: str, api_key: str, limit: int = 30) -> str:
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    }
    return f"{FRED_API_BASE}?{urllib.parse.urlencode(params)}"


def fetch_series(series_id: str, api_key: str, max_retries: int = 3) -> list[dict[str, Any]]:
    url = build_fred_url(series_id, api_key)
    attempt = 0
    while True:
        try:
            request = urllib.request.Request(url, headers={"accept": "application/json"}, method="GET")
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("observations", [])
        except urllib.error.HTTPError as exc:
            attempt += 1
            if exc.code in {400, 403, 404} or attempt >= max_retries:
                body = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"FRED request failed for {series_id}: {exc.code} {body}") from exc
            time.sleep(attempt * 2.0)
        except urllib.error.URLError as exc:
            attempt += 1
            if attempt >= max_retries:
                raise RuntimeError(f"FRED request failed for {series_id}: {exc.reason}") from exc
            time.sleep(attempt * 2.0)


def normalize_observation(
    series_id: str,
    series_name: str,
    observation: dict[str, Any],
) -> dict[str, Any] | None:
    date = observation.get("date", "")
    raw_value = observation.get("value", ".")
    if not date or raw_value == ".":
        return None
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return None

    now = _utc_now_isoformat()
    return {
        "source_system": "fred",
        "source_record_id": f"{series_id}:{date}",
        "series_id": series_id,
        "series_name": series_name,
        "observation_date": date,
        "value": value,
        "observed_at": now,
        "ingested_at": now,
        "payload_version": "fred_observations_v1",
    }


def fetch_all_series(api_key: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for series_id, series_name in FRED_SERIES.items():
        observations = fetch_series(series_id, api_key)
        for obs in observations:
            row = normalize_observation(series_id, series_name, obs)
            if row is not None:
                rows.append(row)
    return rows


def write_macro_rows(
    spark: Any,
    rows: list[dict[str, Any]],
    target_table: str = DEFAULT_TARGET_TABLE,
) -> IngestionResult:
    if not rows:
        return IngestionResult(rows_written=0, target_table=target_table)
    df = spark.createDataFrame(rows)
    df = df.dropDuplicates(["source_system", "source_record_id"])
    df.write.mode("append").format("delta").saveAsTable(target_table)
    return IngestionResult(rows_written=df.count(), target_table=target_table)


def main(
    spark: Any,
    target_table: str = DEFAULT_TARGET_TABLE,
    api_key: str | None = None,
    skip_live: bool = False,
) -> IngestionResult:
    if skip_live or not api_key:
        print("Skipping FRED fetch: api_key not set or --skip-live flag active.")
        return IngestionResult(rows_written=0, target_table=target_table)
    rows = fetch_all_series(api_key)
    return write_macro_rows(spark, rows, target_table=target_table)


def parse_runtime_args(argv: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {"target_table": None, "skip_live": False}
    index = 0
    while index < len(argv):
        if argv[index] == "--target-table" and index + 1 < len(argv):
            parsed["target_table"] = argv[index + 1]
            index += 2
        elif argv[index] == "--skip-live":
            parsed["skip_live"] = True
            index += 1
        else:
            index += 1
    return parsed


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
    skip_live = runtime_args["skip_live"]

    fred_api_key = os.environ.get("FRED_API_KEY")
    if not fred_api_key:
        try:
            fred_api_key = dbutils.secrets.get("fred", "api_key")  # type: ignore[name-defined]
        except Exception:
            fred_api_key = None

    result = main(spark_session, target_table=target, api_key=fred_api_key, skip_live=skip_live)
    print(json.dumps({"rows_written": result.rows_written, "target_table": result.target_table}))
