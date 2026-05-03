from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# Allow importing backend modules from the repo root
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_dbsql_mod: Any = None
_dbsql_config: Any = None


def _load() -> bool:
    global _dbsql_mod, _dbsql_config
    if _dbsql_mod is not None:
        return _dbsql_config is not None
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "databricks_sql_client",
            _REPO_ROOT / "backend" / "databricks_sql_client.py",
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        _dbsql_mod = mod
        _dbsql_config = mod.load_config_from_env()
    except Exception:
        pass
    return _dbsql_config is not None


def run_query(sql: str) -> list[dict[str, Any]]:
    if not _load():
        return []
    try:
        return _dbsql_mod.execute_statement(_dbsql_config, sql)
    except Exception:
        return []


def fetch_market_rankings(limit: int = 12) -> list[dict[str, Any]]:
    catalog = os.environ.get("COINGECKO_CATALOG", "cgadev")
    sql = (
        f"SELECT asset_id, symbol, name, price_usd, price_change_pct_24h, "
        f"market_cap_usd, volume_24h_usd, market_cap_rank "
        f"FROM {catalog}.market_gold.gold_market_rankings "
        f"ORDER BY market_cap_rank ASC LIMIT {limit}"
    )
    return run_query(sql)


def fetch_top_movers(limit: int = 10) -> list[dict[str, Any]]:
    catalog = os.environ.get("COINGECKO_CATALOG", "cgadev")
    sql = (
        f"SELECT asset_id, symbol, name, price_change_pct_24h, "
        f"price_change_pct_7d, volume_24h_usd, market_cap_usd "
        f"FROM {catalog}.market_gold.gold_top_movers "
        f"WHERE quality_status = 'pass' "
        f"ORDER BY ABS(price_change_pct_24h) DESC LIMIT {limit}"
    )
    return run_query(sql)


def fetch_defi_protocols(limit: int = 10) -> list[dict[str, Any]]:
    catalog = os.environ.get("COINGECKO_CATALOG", "cgadev")
    sql = (
        f"SELECT protocol_name, chain, category, tvl_usd, fees_24h_usd, revenue_24h_usd "
        f"FROM {catalog}.market_gold.gold_defi_protocols "
        f"ORDER BY tvl_usd DESC NULLS LAST LIMIT {limit}"
    )
    return run_query(sql)


def fetch_macro_regime(limit: int = 8) -> list[dict[str, Any]]:
    catalog = os.environ.get("COINGECKO_CATALOG", "cgadev")
    sql = (
        f"SELECT series_name, value, observation_date, regime_label "
        f"FROM {catalog}.market_gold.gold_macro_regime "
        f"ORDER BY observation_date DESC LIMIT {limit}"
    )
    return run_query(sql)
