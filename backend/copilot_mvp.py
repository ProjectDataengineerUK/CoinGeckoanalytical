from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any


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


def route_request(message_text: str) -> str:
    lowered = message_text.lower()
    if any(
        token in lowered
        for token in [
            "rank",
            "ranking",
            "top",
            "compare",
            "comparison",
            "dominan",
            "market cap",
            "highest",
            "lowest",
            "volume",
            "price change",
        ]
    ):
        return "genie"
    return "copilot"


def build_copilot_response(request: CopilotRequest) -> dict[str, Any]:
    route_selected = route_request(request.message_text)
    if route_selected == "genie":
        return {
            "request_id": request.request_id,
            "surface_type": "analytics_answer",
            "title": "Consulta analitica governada",
            "body": "A pergunta deve seguir para Genie por ser uma consulta estruturada.",
            "citations": [],
            "freshness": {"watermark": None, "status": "pending"},
            "confidence": {"label": "medium", "score": 0.72},
            "actions": ["route_to_genie"],
            "warnings": [],
        }

    response_text = (
        "Resposta de copilot MVP: use o agente para analise narrativa, "
        "com provenance, frescor e policy context."
    )
    return {
        "request_id": request.request_id,
        "surface_type": "copilot_answer",
        "title": "Copilot de mercado",
        "body": response_text,
        "citations": ["unity_catalog.gold_market_views", "mosaic_ai_vector_search"],
        "freshness": {"watermark": "pending", "status": "unknown"},
        "confidence": {"label": "provisional", "score": 0.64},
        "actions": ["follow_up_question", "open_analytics_view"],
        "warnings": ["mvp_stub_response"],
    }


def build_usage_event(request: CopilotRequest, response: dict[str, Any], latency_ms: int = 120) -> dict[str, Any]:
    return {
        "event_time": dt.datetime.now(dt.UTC).isoformat(),
        "request_id": request.request_id,
        "tenant_id": request.tenant_id,
        "user_id": request.user_id,
        "route_selected": "copilot" if response["surface_type"] == "copilot_answer" else "genie",
        "model_or_engine": "mosaic-ai-agent-framework",
        "prompt_tokens": None,
        "completion_tokens": None,
        "total_tokens": None,
        "latency_ms": latency_ms,
        "cost_estimate": None,
        "freshness_watermark": response["freshness"]["watermark"],
        "response_status": "success",
    }
