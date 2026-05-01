from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

_TOKEN_CACHE: dict[str, tuple[str, float]] = {}

MAX_POLL_ATTEMPTS = 30
POLL_INTERVAL_SECONDS = 1.0

_FLOAT_TYPES = {"DECIMAL", "DOUBLE", "FLOAT"}
_INT_TYPES = {"INT", "BIGINT", "SMALLINT", "TINYINT", "LONG"}


@dataclass(frozen=True)
class DatabricksSQLConfig:
    host: str
    warehouse_id: str
    client_id: str
    client_secret: str
    catalog: str = "cgadev"
    timeout_seconds: int = 30


def load_config_from_env(env: dict[str, str] | None = None) -> DatabricksSQLConfig | None:
    source = env if env is not None else os.environ
    host = source.get("DATABRICKS_HOST", "").rstrip("/")
    warehouse_id = source.get("DATABRICKS_SQL_WAREHOUSE_ID", "")
    if not host or not warehouse_id:
        return None
    return DatabricksSQLConfig(
        host=host,
        warehouse_id=warehouse_id,
        client_id=source.get("DATABRICKS_CLIENT_ID", ""),
        client_secret=source.get("DATABRICKS_CLIENT_SECRET", ""),
        catalog=source.get("COINGECKO_CATALOG", "cgadev"),
    )


def _get_oauth_token(config: DatabricksSQLConfig) -> str:
    cache_key = f"{config.host}:{config.client_id}"
    now = time.monotonic()
    if cache_key in _TOKEN_CACHE:
        token, expires_at = _TOKEN_CACHE[cache_key]
        if now < expires_at:
            return token

    url = f"{config.host}/oidc/v1/token"
    body = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "scope": "all-apis",
        }
    ).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=config.timeout_seconds) as resp:
        data: dict[str, Any] = json.loads(resp.read())

    token = str(data["access_token"])
    ttl = int(data.get("expires_in", 3600))
    _TOKEN_CACHE[cache_key] = (token, now + min(ttl, 3300))
    return token


def _post_json(url: str, body: dict[str, Any], token: str, timeout: int) -> dict[str, Any]:
    payload = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _get_json(url: str, token: str, timeout: int) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _cast_value(raw: Any, type_name: str) -> Any:
    if raw is None:
        return None
    upper = type_name.upper()
    if upper in _FLOAT_TYPES:
        return float(raw)
    if upper in _INT_TYPES:
        return int(raw)
    return str(raw)


def _rows_from_response(data: dict[str, Any]) -> list[dict[str, Any]]:
    columns = data.get("manifest", {}).get("schema", {}).get("columns", [])
    data_array = (data.get("result") or {}).get("data_array") or []
    if not columns or not data_array:
        return []
    col_names = [c["name"] for c in columns]
    col_types = [c.get("type_name", "STRING") for c in columns]
    return [
        {col_names[i]: _cast_value(row[i], col_types[i]) for i in range(len(col_names))}
        for row in data_array
    ]


def execute_statement(config: DatabricksSQLConfig, sql: str) -> list[dict[str, Any]]:
    token = _get_oauth_token(config)
    submit_url = f"{config.host}/api/2.0/sql/statements"
    body = {
        "warehouse_id": config.warehouse_id,
        "statement": sql,
        "catalog": config.catalog,
        "wait_timeout": f"{config.timeout_seconds}s",
        "on_wait_timeout": "CONTINUE",
        "disposition": "INLINE",
    }
    result = _post_json(submit_url, body, token, config.timeout_seconds)

    state = result.get("status", {}).get("state", "")
    statement_id = result.get("statement_id", "")

    for _ in range(MAX_POLL_ATTEMPTS):
        if state not in {"PENDING", "RUNNING"}:
            break
        time.sleep(POLL_INTERVAL_SECONDS)
        poll_url = f"{config.host}/api/2.0/sql/statements/{statement_id}"
        result = _get_json(poll_url, token, config.timeout_seconds)
        state = result.get("status", {}).get("state", "")

    if state == "SUCCEEDED":
        return _rows_from_response(result)
    if state == "FAILED":
        error_msg = result.get("status", {}).get("error", {}).get("message", "unknown error")
        raise RuntimeError(f"SQL statement failed: {error_msg}")
    raise RuntimeError(f"SQL statement ended in unexpected state: {state}")


def fetch_market_rankings(config: DatabricksSQLConfig, limit: int = 100) -> list[dict[str, Any]]:
    sql = (
        f"SELECT asset_id, symbol, name, category, observed_at, market_cap_usd, price_usd, "
        f"volume_24h_usd, circulating_supply, market_cap_rank, freshness_tier, quality_status "
        f"FROM {config.catalog}.market_gold.gold_market_rankings "
        f"WHERE quality_status = 'pass' "
        f"ORDER BY market_cap_rank ASC "
        f"LIMIT {limit}"
    )
    return execute_statement(config, sql)


def fetch_top_movers(config: DatabricksSQLConfig, limit: int = 10) -> list[dict[str, Any]]:
    sql = (
        f"SELECT asset_id, symbol, name, observed_at, window_id, price_change_pct_1h, "
        f"price_change_pct_24h, price_change_pct_7d, volume_24h_usd, market_cap_usd, "
        f"move_direction_24h, move_band_24h, quality_status "
        f"FROM {config.catalog}.market_gold.gold_top_movers "
        f"WHERE quality_status = 'pass' "
        f"AND observed_at = (SELECT MAX(observed_at) FROM {config.catalog}.market_gold.gold_top_movers WHERE quality_status = 'pass') "
        f"ORDER BY ABS(price_change_pct_24h) DESC "
        f"LIMIT {limit}"
    )
    return execute_statement(config, sql)


def fetch_market_dominance(config: DatabricksSQLConfig) -> list[dict[str, Any]]:
    sql = (
        f"SELECT observed_at, dominance_group, market_cap_usd, dominance_pct, dominance_band, quality_status "
        f"FROM {config.catalog}.market_gold.gold_market_dominance "
        f"WHERE quality_status = 'pass' "
        f"AND observed_at = (SELECT MAX(observed_at) FROM {config.catalog}.market_gold.gold_market_dominance WHERE quality_status = 'pass') "
        f"ORDER BY dominance_pct DESC"
    )
    return execute_statement(config, sql)


def fetch_cross_asset_comparison(
    config: DatabricksSQLConfig,
    asset_ids: list[str] | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    base = (
        f"SELECT asset_id, symbol, observed_at, price_usd, market_cap_usd, volume_24h_usd, "
        f"price_change_pct_24h, price_change_pct_7d, correlation_bucket, quality_status "
        f"FROM {config.catalog}.market_gold.gold_cross_asset_comparison "
        f"WHERE quality_status = 'pass' "
        f"AND observed_at = (SELECT MAX(observed_at) FROM {config.catalog}.market_gold.gold_cross_asset_comparison WHERE quality_status = 'pass')"
    )
    if asset_ids:
        ids_literal = ", ".join(f"'{a}'" for a in asset_ids)
        base += f" AND asset_id IN ({ids_literal})"
    sql = base + f" ORDER BY market_cap_usd DESC LIMIT {limit}"
    return execute_statement(config, sql)


def fetch_market_overview_datasets(
    config: DatabricksSQLConfig,
    selected_assets: list[str] | None = None,
    time_range: dict[str, str] | None = None,  # noqa: ARG001 — reserved for V2
) -> dict[str, list[dict[str, Any]]]:
    return {
        "rankings": fetch_market_rankings(config),
        "movers": fetch_top_movers(config),
        "dominance": fetch_market_dominance(config),
        "comparisons": fetch_cross_asset_comparison(config, asset_ids=selected_assets or []),
    }
