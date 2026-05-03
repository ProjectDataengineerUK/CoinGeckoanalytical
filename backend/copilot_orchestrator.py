from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# SQL context templates — each agent fetches from its own Gold domain
# ---------------------------------------------------------------------------

_MARKET_SQL = """
  SELECT asset_id, symbol, name, price_usd, price_change_pct_24h,
         market_cap_usd, volume_24h_usd, market_cap_rank
  FROM {catalog}.market_gold.gold_market_rankings
  ORDER BY market_cap_rank ASC LIMIT 12
"""

_MACRO_SQL = """
  SELECT series_name, value, observation_date, regime_label
  FROM {catalog}.market_gold.gold_macro_regime
  ORDER BY observation_date DESC LIMIT 8
"""

_DEFI_SQL = """
  SELECT protocol_name, chain, category, tvl_usd, fees_usd, revenue_usd, mcap_tvl_ratio
  FROM {catalog}.market_gold.gold_defi_protocols
  ORDER BY tvl_usd DESC NULLS LAST LIMIT 10
"""

_ENRICHED_SQL = """
  SELECT asset_id, dev_activity_score, commits_30d, stars, contributors_count
  FROM {catalog}.market_gold.gold_enriched_rankings
  ORDER BY dev_activity_score DESC NULLS LAST LIMIT 10
"""

# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AgentResult:
    agent_name: str
    answer_text: str
    sources: tuple[str, ...]
    token_count: int
    latency_ms: int
    execution_status: str  # "completed" | "failed" | "no_data"


@dataclass(frozen=True)
class OrchestratorResult:
    answer_text: str
    agent_results: tuple[AgentResult, ...]
    total_tokens: int
    total_latency_ms: int
    sources: tuple[str, ...]
    execution_status: str


# ---------------------------------------------------------------------------
# Context fetchers — thin wrappers around DBSQL
# ---------------------------------------------------------------------------

def _fetch_context(dbsql_client: Any, sql: str, catalog: str) -> list[dict[str, Any]]:
    try:
        rows = dbsql_client.run_query(sql.format(catalog=catalog))
        return rows if isinstance(rows, list) else []
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Individual domain agents
# ---------------------------------------------------------------------------

_AGENT_STANDARD_TIER = "standard"
_AGENT_COMPLEX_TIER = "complex"


def _call_agent(
    mosaic_client: Any,
    mosaic_config: Any,
    agent_name: str,
    system_prompt: str,
    question: str,
    context_data: list[dict[str, Any]],
    tier: str = _AGENT_STANDARD_TIER,
) -> AgentResult:
    started = time.monotonic()
    context_json = json.dumps(context_data, default=str) if context_data else "[]"
    full_question = (
        f"Context data:\n{context_json}\n\nUser question: {question}"
    )
    history = [{"role": "system", "content": system_prompt}]
    try:
        answer = mosaic_client.ask_mosaic(
            mosaic_config, full_question, conversation_history=history, tier=tier
        )
        latency = int((time.monotonic() - started) * 1000)
        if answer.execution_status == "completed":
            return AgentResult(
                agent_name=agent_name,
                answer_text=answer.answer_text,
                sources=(_source_for(agent_name),),
                token_count=answer.token_count_hint,
                latency_ms=latency,
                execution_status="completed",
            )
        return AgentResult(
            agent_name=agent_name, answer_text="", sources=(),
            token_count=0, latency_ms=latency, execution_status="no_data",
        )
    except Exception:
        latency = int((time.monotonic() - started) * 1000)
        return AgentResult(
            agent_name=agent_name, answer_text="", sources=(),
            token_count=0, latency_ms=latency, execution_status="failed",
        )


def _source_for(agent_name: str) -> str:
    return {
        "market_agent": "unity_catalog.market_gold.gold_market_rankings",
        "macro_agent": "unity_catalog.market_gold.gold_macro_regime",
        "defi_agent": "unity_catalog.market_gold.gold_defi_protocols",
        "enriched_agent": "unity_catalog.market_gold.gold_enriched_rankings",
        "synth_agent": "copilot_orchestrator.synthesis",
    }.get(agent_name, agent_name)


def run_market_agent(
    mosaic_client: Any, mosaic_config: Any, question: str,
    context: list[dict[str, Any]],
) -> AgentResult:
    system = (
        "You are a crypto market analyst. You have access to live Gold-tier market data. "
        "Answer only about price, market cap, volume, and momentum. "
        "Be concise — 3-5 sentences max. Cite specific asset values from the data provided."
    )
    return _call_agent(mosaic_client, mosaic_config, "market_agent", system, question, context)


def run_macro_agent(
    mosaic_client: Any, mosaic_config: Any, question: str,
    context: list[dict[str, Any]],
) -> AgentResult:
    system = (
        "You are a macro economist specializing in crypto market conditions. "
        "You have access to FRED macro indicators (rates, money supply, inflation, USD strength). "
        "Comment on the current macro regime and its implications for crypto assets. "
        "Be concise — 3-5 sentences max."
    )
    return _call_agent(mosaic_client, mosaic_config, "macro_agent", system, question, context)


def run_defi_agent(
    mosaic_client: Any, mosaic_config: Any, question: str,
    context: list[dict[str, Any]],
) -> AgentResult:
    system = (
        "You are a DeFi analyst. You have access to DefiLlama protocol data (TVL, fees, revenue) "
        "and on-chain developer activity from GitHub. "
        "Comment on DeFi ecosystem health and developer momentum. "
        "Be concise — 3-5 sentences max."
    )
    return _call_agent(mosaic_client, mosaic_config, "defi_agent", system, question, context)


def run_synth_agent(
    mosaic_client: Any, mosaic_config: Any, question: str,
    market_result: AgentResult, macro_result: AgentResult, defi_result: AgentResult,
) -> AgentResult:
    system = (
        "You are a senior crypto market strategist. Three domain experts have analyzed the same question "
        "from different angles. Synthesize their insights into one coherent, grounded answer. "
        "Structure: (1) market context, (2) macro environment, (3) DeFi/on-chain signal, "
        "(4) synthesis and recommendation. Be direct. Cite data points from the expert analyses."
    )
    combined = (
        f"[Market analyst says]\n{market_result.answer_text or 'No market data available.'}\n\n"
        f"[Macro analyst says]\n{macro_result.answer_text or 'No macro data available.'}\n\n"
        f"[DeFi analyst says]\n{defi_result.answer_text or 'No DeFi data available.'}\n\n"
        f"Original user question: {question}"
    )
    started = time.monotonic()
    history = [{"role": "system", "content": system}]
    try:
        answer = mosaic_client.ask_mosaic(
            mosaic_config, combined, conversation_history=history, tier=_AGENT_COMPLEX_TIER
        )
        latency = int((time.monotonic() - started) * 1000)
        if answer.execution_status == "completed":
            all_sources = (
                market_result.sources + macro_result.sources + defi_result.sources
                + ("copilot_orchestrator.synthesis",)
            )
            return AgentResult(
                agent_name="synth_agent",
                answer_text=answer.answer_text,
                sources=all_sources,
                token_count=answer.token_count_hint,
                latency_ms=latency,
                execution_status="completed",
            )
    except Exception:
        pass
    latency = int((time.monotonic() - started) * 1000)
    return AgentResult(
        agent_name="synth_agent", answer_text="", sources=(),
        token_count=0, latency_ms=latency, execution_status="failed",
    )


# ---------------------------------------------------------------------------
# Orchestrator entry point
# ---------------------------------------------------------------------------

def orchestrate(
    question: str,
    mosaic_client: Any,
    mosaic_config: Any,
    dbsql_client: Any | None = None,
    catalog: str = "cgadev",
    selected_assets: list[str] | None = None,
) -> OrchestratorResult:
    started = time.monotonic()

    # 1. Fetch domain context (graceful degradation when DBSQL unavailable)
    if dbsql_client is not None:
        market_ctx = _fetch_context(dbsql_client, _MARKET_SQL, catalog)
        macro_ctx = _fetch_context(dbsql_client, _MACRO_SQL, catalog)
        defi_ctx = _fetch_context(dbsql_client, _DEFI_SQL, catalog)
    else:
        market_ctx = macro_ctx = defi_ctx = []

    # 2. Run domain agents (sequentially — parallel execution requires threading/async)
    market_r = run_market_agent(mosaic_client, mosaic_config, question, market_ctx)
    macro_r = run_macro_agent(mosaic_client, mosaic_config, question, macro_ctx)
    defi_r = run_defi_agent(mosaic_client, mosaic_config, question, defi_ctx)

    # 3. Synthesize only when at least one domain agent succeeded
    completed = [r for r in (market_r, macro_r, defi_r) if r.execution_status == "completed"]
    if not completed:
        total_ms = int((time.monotonic() - started) * 1000)
        return OrchestratorResult(
            answer_text="",
            agent_results=(market_r, macro_r, defi_r),
            total_tokens=0,
            total_latency_ms=total_ms,
            sources=(),
            execution_status="failed",
        )

    synth_r = run_synth_agent(mosaic_client, mosaic_config, question, market_r, macro_r, defi_r)

    all_agents = (market_r, macro_r, defi_r, synth_r)
    total_tokens = sum(r.token_count for r in all_agents)
    total_ms = int((time.monotonic() - started) * 1000)
    all_sources: tuple[str, ...] = sum((r.sources for r in all_agents), ())

    return OrchestratorResult(
        answer_text=synth_r.answer_text or next(
            (r.answer_text for r in completed), ""
        ),
        agent_results=all_agents,
        total_tokens=total_tokens,
        total_latency_ms=total_ms,
        sources=tuple(dict.fromkeys(all_sources)),  # deduplicated, order-preserving
        execution_status=synth_r.execution_status,
    )
