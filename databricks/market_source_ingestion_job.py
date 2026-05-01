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


DEFAULT_COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
DEFAULT_COINGECKO_MARKETS_PATH = "/coins/markets"

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


@dataclass(frozen=True)
class CoinGeckoFetchConfig:
    base_url: str = DEFAULT_COINGECKO_BASE_URL
    vs_currency: str = "usd"
    order: str = "market_cap_desc"
    per_page: int = 250
    pages: int = 1
    sparkline: bool = False
    price_change_percentage: str | None = "1h,24h,7d,30d"
    request_timeout_seconds: int = 30
    max_retries: int = 3
    retry_backoff_seconds: float = 1.0
    api_key: str | None = None
    api_key_header: str = "x-cg-demo-api-key"


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


def build_coingecko_markets_url(config: CoinGeckoFetchConfig, page: int) -> str:
    query: dict[str, str | int] = {
        "vs_currency": config.vs_currency,
        "order": config.order,
        "per_page": config.per_page,
        "page": page,
        "sparkline": str(config.sparkline).lower(),
    }
    if config.price_change_percentage:
        query["price_change_percentage"] = config.price_change_percentage
    return f"{config.base_url.rstrip('/')}{DEFAULT_COINGECKO_MARKETS_PATH}?{urllib.parse.urlencode(query)}"


def request_json(url: str, config: CoinGeckoFetchConfig) -> Any:
    headers = {"accept": "application/json"}
    if config.api_key:
        headers[config.api_key_header] = config.api_key
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=config.request_timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_coingecko_market_rows(config: CoinGeckoFetchConfig | None = None) -> list[dict[str, Any]]:
    active_config = config or load_coingecko_fetch_config_from_env()
    rows: list[dict[str, Any]] = []

    for page in range(1, active_config.pages + 1):
        url = build_coingecko_markets_url(active_config, page)
        page_rows = _request_json_with_retry(url, active_config)
        if not isinstance(page_rows, list):
            raise ValueError("CoinGecko markets response must be a JSON array.")
        rows.extend(dict(item) for item in page_rows)
        if len(page_rows) < active_config.per_page:
            break

    return rows


def load_coingecko_fetch_config_from_env(env: dict[str, str] | None = None) -> CoinGeckoFetchConfig:
    active_env = env if env is not None else os.environ
    return CoinGeckoFetchConfig(
        base_url=active_env.get("COINGECKO_API_BASE_URL", DEFAULT_COINGECKO_BASE_URL),
        vs_currency=active_env.get("COINGECKO_VS_CURRENCY", "usd"),
        order=active_env.get("COINGECKO_MARKET_ORDER", "market_cap_desc"),
        per_page=_coerce_int_env(active_env.get("COINGECKO_PER_PAGE"), 250),
        pages=_coerce_int_env(active_env.get("COINGECKO_PAGES"), 1),
        sparkline=_coerce_bool_env(active_env.get("COINGECKO_SPARKLINE"), False),
        price_change_percentage=active_env.get("COINGECKO_PRICE_CHANGE_PERCENTAGE", "1h,24h,7d,30d"),
        request_timeout_seconds=_coerce_int_env(active_env.get("COINGECKO_REQUEST_TIMEOUT_SECONDS"), 30),
        max_retries=_coerce_int_env(active_env.get("COINGECKO_MAX_RETRIES"), 3),
        retry_backoff_seconds=_coerce_float_env(active_env.get("COINGECKO_RETRY_BACKOFF_SECONDS"), 1.0),
        api_key=active_env.get("COINGECKO_API_KEY"),
        api_key_header=active_env.get("COINGECKO_API_KEY_HEADER", "x-cg-demo-api-key"),
    )


def _request_json_with_retry(url: str, config: CoinGeckoFetchConfig) -> Any:
    attempt = 0
    while True:
        try:
            return request_json(url, config)
        except urllib.error.HTTPError as exc:
            attempt += 1
            if exc.code not in {429, 500, 502, 503, 504} or attempt >= config.max_retries:
                body = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"CoinGecko request failed: {exc.code} {body}") from exc
            time.sleep(config.retry_backoff_seconds * attempt)
        except urllib.error.URLError as exc:
            attempt += 1
            if attempt >= config.max_retries:
                raise RuntimeError(f"CoinGecko request failed: {exc.reason}") from exc
            time.sleep(config.retry_backoff_seconds * attempt)


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
    fetch_config: CoinGeckoFetchConfig | None = None,
) -> IngestionResult:
    if payload_json or payload_path:
        rows = parse_payload(payload_json, payload_path=payload_path)
    else:
        rows = fetch_coingecko_market_rows(fetch_config)
    return write_market_rows(spark, rows, target_table=target_table)


def _coerce_required_float(value: Any) -> float:
    if value in {None, ""}:
        raise ValueError("Required numeric market field is missing.")
    return float(value)


def _coerce_required_int(value: Any) -> int:
    if value in {None, ""}:
        raise ValueError("Required integer market field is missing.")
    return int(value)


def _coerce_int_env(value: str | None, default: int) -> int:
    if value in {None, ""}:
        return default
    return int(value)


def _coerce_float_env(value: str | None, default: float) -> float:
    if value in {None, ""}:
        return default
    return float(value)


def _coerce_bool_env(value: str | None, default: bool) -> bool:
    if value in {None, ""}:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


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
