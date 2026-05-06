from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path
from typing import Any

# Allow importing backend modules from the repo root
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_dbsql_mod: Any = None
_dbsql_config: Any = None


def _catalog() -> str:
    return os.environ.get("COINGECKO_CATALOG", "cgadev")


def _schema() -> str:
    return os.environ.get("COINGECKO_SCHEMA", "ai_serving")


def _table(name: str) -> str:
    return f"`{_catalog()}`.`{_schema()}`.`{name}`"


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

        if spec is None or spec.loader is None:
            print("[SQL SERVICE] Não foi possível carregar databricks_sql_client.py", flush=True)
            return False

        mod = importlib.util.module_from_spec(spec)
        sys.modules["databricks_sql_client"] = mod
        spec.loader.exec_module(mod)

        _dbsql_mod = mod
        _dbsql_config = mod.load_config_from_env()

        if _dbsql_config is None:
            print("[SQL SERVICE] Config SQL ausente ou inválida.", flush=True)
            return False

        print("[SQL SERVICE] Databricks SQL config carregada.", flush=True)
        return True

    except Exception as exc:
        print("[SQL SERVICE] Erro ao carregar SQL client:", repr(exc), flush=True)
        traceback.print_exc()
        return False


def run_query(sql: str) -> list[dict[str, Any]]:
    if not _load():
        print("[SQL SERVICE] _load() falhou. Query não executada.", flush=True)
        return []

    try:
        print("[SQL SERVICE] Executando SQL:", sql, flush=True)
        rows = _dbsql_mod.execute_statement(_dbsql_config, sql)
        print("[SQL SERVICE] Linhas retornadas:", len(rows or []), flush=True)
        return rows or []

    except Exception as exc:
        print("[SQL SERVICE] Erro ao executar query:", repr(exc), flush=True)
        traceback.print_exc()
        return []


def fetch_market_rankings(limit: int = 12) -> list[dict[str, Any]]:
    sql = f"""
        SELECT
            asset_id,
            symbol,
            name,
            price_usd,
            CAST(NULL AS DOUBLE) AS price_change_pct_24h,
            market_cap_usd,
            volume_24h_usd,
            market_cap_rank,
            observed_at
        FROM {_table("mv_market_rankings")}
        ORDER BY market_cap_rank ASC
        LIMIT {int(limit)}
    """
    return run_query(sql)


def fetch_top_movers(limit: int = 10) -> list[dict[str, Any]]:
    primary_sql = f"""
        SELECT
            asset_id,
            symbol,
            name,
            price_change_pct_24h,
            price_change_pct_7d,
            volume_24h_usd,
            market_cap_usd
        FROM {_table("mv_top_movers")}
        ORDER BY ABS(price_change_pct_24h) DESC NULLS LAST
        LIMIT {int(limit)}
    """
    rows = run_query(primary_sql)
    if rows:
        return rows

    fallback_sql = f"""
        SELECT
            asset_id,
            symbol,
            asset_id AS name,
            price_change_pct_24h,
            price_change_pct_7d,
            volume_24h_usd,
            market_cap_usd
        FROM {_table("mv_cross_asset_compare")}
        ORDER BY ABS(price_change_pct_24h) DESC NULLS LAST
        LIMIT {int(limit)}
    """
    return run_query(fallback_sql)


def fetch_defi_protocols(limit: int = 10) -> list[dict[str, Any]]:
    sql = f"""
        SELECT
            protocol_slug,
            name AS protocol_name,
            tvl_usd,
            fees_24h_usd,
            revenue_24h_usd,
            mcap_tvl_ratio,
            enriched_at
        FROM {_table("mv_defi_protocols")}
        WHERE quality_status = 'pass'
        ORDER BY tvl_usd DESC NULLS LAST
        LIMIT {int(limit)}
    """
    return run_query(sql)


def fetch_macro_regime(limit: int = 8) -> list[dict[str, Any]]:
    sql = f"""
        SELECT
            series_name,
            latest_date AS observation_date,
            current_value AS value,
            regime_label,
            change_30d_pct
        FROM {_table("mv_macro_regime")}
        WHERE quality_status = 'pass'
        ORDER BY latest_date DESC, series_name ASC
        LIMIT {int(limit)}
    """
    return run_query(sql)


def fetch_market_freshness() -> str | None:
    """
    Retorna a data mais recente dos dados disponíveis.

    Antes estava usando:
        cgadev.market_gold.gold_market_rankings
        MAX(ingested_at)

    Mas o Genie está usando:
        cgadev.ai_serving.mv_market_rankings
        observed_at

    Então usamos MAX(observed_at).
    """
    rows = run_query(
        f"""
        SELECT MAX(observed_at) AS wm
        FROM {_table("mv_market_rankings")}
        """
    )

    if not rows:
        print("[SQL SERVICE] Freshness: query não retornou linhas.", flush=True)
        return None

    wm = rows[0].get("wm")

    if wm is None:
        print("[SQL SERVICE] Freshness: wm veio None.", flush=True)
        return None

    return str(wm)
