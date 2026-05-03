from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_mod: Any = None
_cfg: Any = None


def _load() -> bool:
    global _mod, _cfg
    if _mod is not None:
        return _cfg is not None
    try:
        spec = importlib.util.spec_from_file_location(
            "databricks_sql_client",
            _REPO_ROOT / "backend" / "databricks_sql_client.py",
        )
        m = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(m)  # type: ignore[union-attr]
        _mod = m
        _cfg = m.load_config_from_env()
    except Exception:
        pass
    return _cfg is not None


def _ops_catalog() -> str:
    return os.environ.get("COINGECKO_OPS_CATALOG") or os.environ.get("COINGECKO_CATALOG", "cgadev")


def run(sql: str) -> list[dict[str, Any]]:
    if not _load():
        return []
    try:
        return _mod.execute_statement(_cfg, sql)
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Usage events (token/cost telemetry)
# ---------------------------------------------------------------------------

def fetch_usage_events(limit: int = 200) -> list[dict[str, Any]]:
    cat = _ops_catalog()
    return run(
        f"SELECT event_time, tenant_id, user_id, route_selected, model_or_engine, "
        f"model_tier, total_tokens, latency_ms, cost_estimate, response_status "
        f"FROM {cat}.ops.ops_usage_events "
        f"ORDER BY event_time DESC LIMIT {limit}"
    )


def fetch_cost_by_tier() -> list[dict[str, Any]]:
    cat = _ops_catalog()
    return run(
        f"SELECT model_tier, "
        f"COUNT(*) AS requests, "
        f"SUM(total_tokens) AS total_tokens, "
        f"SUM(cost_estimate) AS total_cost_usd, "
        f"AVG(latency_ms) AS avg_latency_ms "
        f"FROM {cat}.ops.ops_usage_events "
        f"GROUP BY model_tier ORDER BY total_cost_usd DESC"
    )


def fetch_daily_spend(days: int = 14) -> list[dict[str, Any]]:
    cat = _ops_catalog()
    return run(
        f"SELECT DATE(event_time) AS day, model_tier, "
        f"SUM(cost_estimate) AS cost_usd, SUM(total_tokens) AS tokens "
        f"FROM {cat}.ops.ops_usage_events "
        f"WHERE event_time >= CURRENT_DATE - INTERVAL {days} DAYS "
        f"GROUP BY day, model_tier ORDER BY day ASC"
    )


def fetch_cost_by_tenant() -> list[dict[str, Any]]:
    cat = _ops_catalog()
    return run(
        f"SELECT tenant_id, model_tier, COUNT(*) AS requests, "
        f"SUM(cost_estimate) AS total_cost_usd, SUM(total_tokens) AS total_tokens "
        f"FROM {cat}.ops.ops_usage_events "
        f"GROUP BY tenant_id, model_tier ORDER BY total_cost_usd DESC LIMIT 20"
    )


# ---------------------------------------------------------------------------
# Sentinela alerts
# ---------------------------------------------------------------------------

def fetch_alerts(limit: int = 100) -> list[dict[str, Any]]:
    cat = _ops_catalog()
    return run(
        f"SELECT alert_time, kind, severity, route_selected, message, "
        f"tenant_id, request_id "
        f"FROM {cat}.ops.ops_sentinela_alerts "
        f"ORDER BY alert_time DESC LIMIT {limit}"
    )


def fetch_alert_counts() -> list[dict[str, Any]]:
    cat = _ops_catalog()
    return run(
        f"SELECT severity, COUNT(*) AS count "
        f"FROM {cat}.ops.ops_sentinela_alerts "
        f"WHERE alert_time >= CURRENT_DATE - INTERVAL 7 DAYS "
        f"GROUP BY severity"
    )


# ---------------------------------------------------------------------------
# Pipeline / bundle runs
# ---------------------------------------------------------------------------

def fetch_bundle_runs(limit: int = 50) -> list[dict[str, Any]]:
    cat = _ops_catalog()
    return run(
        f"SELECT ingested_at, job_name, status, run_id, rows_written, error_message "
        f"FROM {cat}.ops.ops_bundle_runs "
        f"ORDER BY ingested_at DESC LIMIT {limit}"
    )


def fetch_pipeline_summary() -> list[dict[str, Any]]:
    cat = _ops_catalog()
    return run(
        f"SELECT job_name, "
        f"MAX(ingested_at) AS last_run, "
        f"COUNT(*) AS total_runs, "
        f"SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_count, "
        f"SUM(CASE WHEN status != 'SUCCESS' THEN 1 ELSE 0 END) AS failure_count "
        f"FROM {cat}.ops.ops_bundle_runs "
        f"GROUP BY job_name ORDER BY last_run DESC"
    )


# ---------------------------------------------------------------------------
# Freshness / quality
# ---------------------------------------------------------------------------

def fetch_freshness_status() -> list[dict[str, Any]]:
    cat = os.environ.get("COINGECKO_CATALOG", "cgadev")
    return run(
        f"SELECT source_system, MAX(ingested_at) AS last_ingestion, "
        f"COUNT(*) AS total_records "
        f"FROM {cat}.market_bronze.bronze_market_snapshots "
        f"GROUP BY source_system "
        f"UNION ALL "
        f"SELECT 'defillama', MAX(ingested_at), COUNT(*) "
        f"FROM {cat}.market_bronze.bronze_defillama_protocols "
        f"UNION ALL "
        f"SELECT 'github', MAX(ingested_at), COUNT(*) "
        f"FROM {cat}.market_bronze.bronze_github_activity "
        f"UNION ALL "
        f"SELECT 'fred', MAX(ingested_at), COUNT(*) "
        f"FROM {cat}.market_bronze.bronze_fred_macro"
    )


# ---------------------------------------------------------------------------
# Audit trail
# ---------------------------------------------------------------------------

def fetch_audit_trail(limit: int = 100) -> list[dict[str, Any]]:
    cat = _ops_catalog()
    return run(
        f"SELECT event_time, request_id, tenant_id, user_id, route_selected, "
        f"model_or_engine, model_tier, total_tokens, latency_ms, cost_estimate, "
        f"response_status, freshness_watermark "
        f"FROM {cat}.ops.ops_usage_events "
        f"ORDER BY event_time DESC LIMIT {limit}"
    )
