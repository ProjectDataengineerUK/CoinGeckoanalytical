from __future__ import annotations

import datetime as dt
import importlib.util
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def _load_mosaic_client() -> Any | None:
    name = "mosaic_copilot_client"
    if name in sys.modules:
        return sys.modules[name]
    candidate = Path(__file__).resolve().parent / "mosaic_copilot_client.py"
    if not candidate.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, candidate)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_tier_router() -> Any | None:
    name = "model_tier_router"
    if name in sys.modules:
        return sys.modules[name]
    candidate = Path(__file__).resolve().parent / "model_tier_router.py"
    if not candidate.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, candidate)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_orchestrator() -> Any | None:
    name = "copilot_orchestrator"
    if name in sys.modules:
        return sys.modules[name]
    candidate = Path(__file__).resolve().parent / "copilot_orchestrator.py"
    if not candidate.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, candidate)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_dbsql_client() -> Any | None:
    name = "databricks_sql_client"
    if name in sys.modules:
        return sys.modules[name]
    candidate = Path(__file__).resolve().parent / "databricks_sql_client.py"
    if not candidate.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, candidate)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@dataclass(frozen=True)
class RouteDecision:
    surface: str
    reason: str
    signals: tuple[str, ...] = ()


@dataclass(frozen=True)
class CopilotRequest:
    request_id: str
    tenant_id: str
    user_id: str | None
    conversation_id: str
    message_text: str
    conversation_summary: str | None
    retrieval_scope: str
    selected_assets: list[str]
    time_range: dict[str, str] | None
    policy_context: dict[str, Any]
    locale: str


@dataclass(frozen=True)
class ResponseEnvelope:
    request_id: str
    surface_type: str
    title: str
    body: str
    citations: list[str] = field(default_factory=list)
    freshness: dict[str, str | None] = field(default_factory=dict)
    confidence: dict[str, Any] = field(default_factory=dict)
    actions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    routing: dict[str, Any] = field(default_factory=dict)
    schema_version: str = "copilot.response.v1"


@dataclass(frozen=True)
class TelemetryEnvelope:
    event_time: str
    request_id: str
    tenant_id: str
    user_id: str | None
    route_selected: str
    model_or_engine: str
    model_tier: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    latency_ms: int
    cost_estimate: float | None
    freshness_watermark: str | None
    response_status: str
    response_surface_type: str
    response_title: str
    schema_version: str = "copilot.telemetry.v1"


_STUB_WARNING = "mvp_stub_response"

STRUCTURED_ROUTE_SIGNALS = (
    "rank",
    "ranking",
    "top",
    "compare",
    "comparison",
    "versus",
    "vs",
    "dominan",
    "market cap",
    "highest",
    "lowest",
    "volume",
    "price change",
    "table",
    "across",
    "by asset",
)

NARRATIVE_ROUTE_SIGNALS = (
    "explain",
    "summarize",
    "summary",
    "what is happening",
    "context",
    "insight",
    "trend",
    "story",
)


def classify_route(request: CopilotRequest | str) -> RouteDecision:
    message_text = request.message_text if isinstance(request, CopilotRequest) else request
    lowered = message_text.lower().strip()
    structured_signals = tuple(
        signal for signal in STRUCTURED_ROUTE_SIGNALS if signal in lowered
    )
    narrative_signals = tuple(signal for signal in NARRATIVE_ROUTE_SIGNALS if signal in lowered)

    if structured_signals:
        return RouteDecision(
            surface="genie",
            reason="structured_analytics_request",
            signals=structured_signals,
        )
    if narrative_signals:
        return RouteDecision(
            surface="copilot",
            reason="narrative_market_request",
            signals=narrative_signals,
        )
    return RouteDecision(
        surface="copilot",
        reason="default_copilot_path",
        signals=(),
    )


def route_request(message_text: str) -> str:
    return classify_route(message_text).surface


def serialize_response_envelope(response: ResponseEnvelope | dict[str, Any]) -> dict[str, Any]:
    payload = asdict(response) if isinstance(response, ResponseEnvelope) else dict(response)
    payload["citations"] = list(payload.get("citations") or [])
    payload["actions"] = list(payload.get("actions") or [])
    payload["warnings"] = list(payload.get("warnings") or [])
    payload["freshness"] = dict(payload.get("freshness") or {})
    payload["confidence"] = dict(payload.get("confidence") or {})
    payload["routing"] = dict(payload.get("routing") or {})
    payload.setdefault("schema_version", "copilot.response.v1")
    return payload


def serialize_telemetry_envelope(
    telemetry: TelemetryEnvelope | dict[str, Any],
) -> dict[str, Any]:
    payload = asdict(telemetry) if isinstance(telemetry, TelemetryEnvelope) else dict(telemetry)
    payload.setdefault("schema_version", "copilot.telemetry.v1")
    return payload


class _DbsqlAdapter:
    """Adapts (module, config) pair to the run_query() interface expected by the orchestrator."""

    def __init__(self, mod: Any, config: Any) -> None:
        self._mod = mod
        self._config = config

    def run_query(self, sql: str) -> list[dict[str, Any]]:
        return self._mod.execute_statement(self._config, sql)


def build_copilot_response(request: CopilotRequest) -> dict[str, Any]:
    decision = classify_route(request)
    if decision.surface == "genie":
        return serialize_response_envelope(
            ResponseEnvelope(
                request_id=request.request_id,
                surface_type="analytics_answer",
                title="Consulta analitica governada",
                body=(
                    "Esta pergunta segue para Genie porque foi identificada como "
                    "consulta estruturada e comparativa."
                ),
                freshness={"watermark": None, "status": "pending"},
                confidence={"label": "medium", "score": 0.72},
                actions=["route_to_genie", "return_structured_result"],
                warnings=[],
                routing={
                    "surface": decision.surface,
                    "reason": decision.reason,
                    "signals": list(decision.signals),
                },
            )
        )

    _mosaic = _load_mosaic_client()
    _tier_router = _load_tier_router()
    mosaic_config = _mosaic.load_config_from_env() if _mosaic is not None else None

    tier_classification = None
    if _tier_router is not None:
        tier_classification = _tier_router.classify_model_tier(
            request.message_text,
            asset_count=len(request.selected_assets),
        )

    tier = tier_classification.tier.value if tier_classification is not None else "standard"

    # Multi-agent orchestrator path for complex cross-domain questions
    if tier == "complex" and _mosaic is not None and mosaic_config is not None:
        _orchestrator = _load_orchestrator()
        if _orchestrator is not None:
            _dbsql_mod = _load_dbsql_client()
            dbsql_adapter = None
            dbsql_catalog = "cgadev"
            if _dbsql_mod is not None:
                _dbsql_config = _dbsql_mod.load_config_from_env()
                if _dbsql_config is not None:
                    dbsql_adapter = _DbsqlAdapter(_dbsql_mod, _dbsql_config)
                    dbsql_catalog = _dbsql_config.catalog
            try:
                orch_result = _orchestrator.orchestrate(
                    request.message_text,
                    _mosaic,
                    mosaic_config,
                    dbsql_client=dbsql_adapter,
                    catalog=dbsql_catalog,
                    selected_assets=request.selected_assets or [],
                )
                if orch_result.execution_status == "completed":
                    cost = None
                    if _tier_router is not None and tier_classification is not None and orch_result.total_tokens:
                        cost = _tier_router.estimate_cost_usd(
                            tier_classification.tier, orch_result.total_tokens
                        )
                    return serialize_response_envelope(
                        ResponseEnvelope(
                            request_id=request.request_id,
                            surface_type="copilot_answer",
                            title="Copilot de mercado — analise multi-agente",
                            body=orch_result.answer_text,
                            citations=list(orch_result.sources),
                            freshness={"watermark": "live", "status": "fresh"},
                            confidence={"label": "multi_agent_grounded", "score": 0.92},
                            actions=["follow_up_question", "open_analytics_view"],
                            warnings=[],
                            routing={
                                "surface": decision.surface,
                                "reason": decision.reason,
                                "signals": list(decision.signals),
                                "latency_ms": orch_result.total_latency_ms,
                                "model_tier": tier,
                                "tier_reason": tier_classification.reason if tier_classification else "complex_orchestrated",
                                "cost_estimate": cost,
                                "agent_count": len(orch_result.agent_results),
                                "orchestrated": True,
                            },
                        )
                    )
            except Exception as _orch_exc:
                import logging as _log
                _log.getLogger(__name__).warning("Orchestration failed: %s", _orch_exc, exc_info=True)

    if mosaic_config is not None:
        try:
            answer = _mosaic.ask_mosaic(
                mosaic_config, request.message_text, tier=tier
            )
            if answer.execution_status == "completed":
                cost = None
                if _tier_router is not None and answer.token_count_hint:
                    cost = _tier_router.estimate_cost_usd(
                        tier_classification.tier, answer.token_count_hint
                    )
                return serialize_response_envelope(
                    ResponseEnvelope(
                        request_id=request.request_id,
                        surface_type="copilot_answer",
                        title="Copilot de mercado",
                        body=answer.answer_text,
                        citations=["unity_catalog.gold_market_views", "mosaic_ai_vector_search"],
                        freshness={"watermark": "live", "status": "fresh"},
                        confidence={"label": "model_grounded", "score": 0.85},
                        actions=["follow_up_question", "open_analytics_view"],
                        warnings=[],
                        routing={
                            "surface": decision.surface,
                            "reason": decision.reason,
                            "signals": list(decision.signals),
                            "latency_ms": answer.latency_ms,
                            "model_id": answer.model_id,
                            "token_count_hint": answer.token_count_hint,
                            "model_tier": tier,
                            "tier_reason": tier_classification.reason if tier_classification else "standard_market_analysis",
                            "cost_estimate": cost,
                        },
                    )
                )
        except Exception as _mosaic_exc:
            import logging as _log
            _log.getLogger(__name__).warning("Mosaic fallback failed: %s", _mosaic_exc, exc_info=True)

    response_text = (
        "Resposta de copilot MVP: use o agente para analise narrativa, com "
        "provenance, frescor e policy context."
    )
    return serialize_response_envelope(
        ResponseEnvelope(
            request_id=request.request_id,
            surface_type="copilot_answer",
            title="Copilot de mercado",
            body=response_text,
            citations=["unity_catalog.gold_market_views", "mosaic_ai_vector_search"],
            freshness={"watermark": "pending", "status": "unknown"},
            confidence={"label": "provisional", "score": 0.64},
            actions=["follow_up_question", "open_analytics_view"],
            warnings=[_STUB_WARNING],
            routing={
                "surface": decision.surface,
                "reason": decision.reason,
                "signals": list(decision.signals),
            },
        )
    )


def build_usage_event(request: CopilotRequest, response: dict[str, Any], latency_ms: int = 120) -> dict[str, Any]:
    routing = response.get("routing") or {}
    telemetry = TelemetryEnvelope(
        event_time=dt.datetime.now(dt.UTC).isoformat(),
        request_id=request.request_id,
        tenant_id=request.tenant_id,
        user_id=request.user_id,
        route_selected=route_request(request.message_text),
        model_or_engine=routing.get("model_id") or "mosaic-ai-agent-framework",
        model_tier=routing.get("model_tier") or "standard",
        prompt_tokens=None,
        completion_tokens=None,
        total_tokens=None,
        latency_ms=latency_ms,
        cost_estimate=routing.get("cost_estimate"),
        freshness_watermark=response["freshness"]["watermark"],
        response_status="success",
        response_surface_type=response["surface_type"],
        response_title=response["title"],
    )
    return serialize_telemetry_envelope(telemetry)


def build_databricks_usage_row(
    request: CopilotRequest,
    response: dict[str, Any],
    latency_ms: int = 120,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    total_tokens: int | None = None,
    cost_estimate: float | None = None,
) -> dict[str, Any]:
    telemetry = build_usage_event(request, response, latency_ms=latency_ms)
    return {
        "event_time": telemetry["event_time"],
        "request_id": telemetry["request_id"],
        "tenant_id": telemetry["tenant_id"],
        "user_id": telemetry["user_id"],
        "route_selected": telemetry["route_selected"],
        "model_or_engine": telemetry["model_or_engine"],
        "model_tier": telemetry["model_tier"],
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "latency_ms": telemetry["latency_ms"],
        "cost_estimate": cost_estimate,
        "freshness_watermark": telemetry["freshness_watermark"],
        "response_status": telemetry["response_status"],
    }
