from __future__ import annotations

import datetime as dt
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class DashboardRequest:
    request_id: str
    tenant_id: str
    user_id: str | None
    session_id: str
    locale: str
    selected_assets: list[str] = field(default_factory=list)
    time_range: dict[str, str] | None = None


@dataclass(frozen=True)
class DashboardResponseEnvelope:
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
    payload: dict[str, Any] = field(default_factory=dict)
    schema_version: str = "coingecko.response.v1"


def _isoformat(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return value.isoformat()
    return str(value)


def _latest_watermark(*datasets: list[dict[str, Any]]) -> str | None:
    latest: str | None = None
    for dataset in datasets:
        for row in dataset:
            current = _isoformat(row.get("observed_at"))
            if current is not None and (latest is None or current > latest):
                latest = current
    return latest


def _asset_label(row: dict[str, Any]) -> str:
    return str(row.get("symbol") or row.get("asset_id") or "UNKNOWN").upper()


def serialize_response_envelope(
    response: DashboardResponseEnvelope | dict[str, Any],
) -> dict[str, Any]:
    payload = asdict(response) if isinstance(response, DashboardResponseEnvelope) else dict(response)
    payload["citations"] = list(payload.get("citations") or [])
    payload["actions"] = list(payload.get("actions") or [])
    payload["warnings"] = list(payload.get("warnings") or [])
    payload["freshness"] = dict(payload.get("freshness") or {})
    payload["confidence"] = dict(payload.get("confidence") or {})
    payload["routing"] = dict(payload.get("routing") or {})
    payload["payload"] = dict(payload.get("payload") or {})
    payload.setdefault("schema_version", "coingecko.response.v1")
    return payload


def build_market_overview_payload(
    request: DashboardRequest,
    rankings: list[dict[str, Any]],
    movers: list[dict[str, Any]],
    dominance: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
) -> dict[str, Any]:
    top_ranked = rankings[:5]
    top_movers = movers[:3]
    dominance_rows = dominance[:4]
    comparison_rows = comparisons[:3]
    watermark = _latest_watermark(rankings, movers, dominance, comparisons)
    warnings: list[str] = []
    if not rankings:
        warnings.append("market_rankings_unavailable")
    if watermark is None:
        warnings.append("freshness_watermark_missing")

    payload = {
        "route_id": "dashboard.market-overview",
        "locale": request.locale,
        "hero_metrics": {
            "tracked_assets": len(rankings),
            "top_movers_visible": len(top_movers),
            "dominance_groups_visible": len(dominance_rows),
        },
        "sections": {
            "market_rankings": [
                {
                    "asset": _asset_label(row),
                    "name": row.get("name"),
                    "market_cap_rank": row.get("market_cap_rank"),
                    "market_cap_usd": row.get("market_cap_usd"),
                    "price_usd": row.get("price_usd"),
                }
                for row in top_ranked
            ],
            "top_movers": [
                {
                    "asset": _asset_label(row),
                    "direction": row.get("move_direction_24h"),
                    "price_change_pct_24h": row.get("price_change_pct_24h"),
                    "move_band_24h": row.get("move_band_24h"),
                }
                for row in top_movers
            ],
            "dominance": [
                {
                    "group": row.get("dominance_group"),
                    "dominance_pct": row.get("dominance_pct"),
                    "market_cap_usd": row.get("market_cap_usd"),
                }
                for row in dominance_rows
            ],
            "comparisons": [
                {
                    "asset": _asset_label(row),
                    "correlation_bucket": row.get("correlation_bucket"),
                    "price_change_pct_24h": row.get("price_change_pct_24h"),
                    "price_change_pct_7d": row.get("price_change_pct_7d"),
                }
                for row in comparison_rows
            ],
        },
    }

    return serialize_response_envelope(
        DashboardResponseEnvelope(
            request_id=request.request_id,
            surface_type="dashboard_payload",
            title="Visao geral do mercado",
            body=(
                "Painel governado com rankings, movers, dominancia e comparacoes "
                "para a rota dashboard.market-overview."
            ),
            citations=[
                "gold_market_rankings",
                "gold_top_movers",
                "gold_market_dominance",
                "gold_cross_asset_comparison",
            ],
            freshness={"watermark": watermark, "status": "ready" if watermark else "unknown"},
            confidence={"label": "governed", "score": 0.9},
            actions=["open_asset_detail", "ask_genie_question", "open_copilot_context"],
            warnings=warnings,
            routing={
                "surface": "dashboard",
                "route_id": "dashboard.market-overview",
                "reason": "governed_market_overview_route",
            },
            payload=payload,
        )
    )


def build_usage_row(
    request: DashboardRequest,
    response: dict[str, Any],
    latency_ms: int = 120,
    cost_estimate: float | None = None,
) -> dict[str, Any]:
    return {
        "event_time": dt.datetime.now(dt.UTC).isoformat(),
        "request_id": request.request_id,
        "tenant_id": request.tenant_id,
        "user_id": request.user_id,
        "route_selected": "dashboard.market-overview",
        "model_or_engine": "dashboard-api",
        "prompt_tokens": None,
        "completion_tokens": None,
        "total_tokens": None,
        "latency_ms": latency_ms,
        "cost_estimate": cost_estimate,
        "freshness_watermark": response.get("freshness", {}).get("watermark"),
        "response_status": "success",
    }
