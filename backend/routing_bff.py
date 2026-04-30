from __future__ import annotations

import datetime as dt
import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _load_module(name: str, filename: str) -> Any:
    module_path = Path(__file__).resolve().parent / filename
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


dashboard_market_overview = _load_module("dashboard_market_overview", "dashboard_market_overview.py")
copilot_mvp = _load_module("copilot_mvp", "copilot_mvp.py")

ALLOWED_CHANNELS = {"web_dashboard", "web_chat", "api"}
ALLOWED_REQUEST_HINTS = {"analytics_nlq", "copilot", "dashboard_query", "auto"}


@dataclass(frozen=True)
class FrontendRoutingRequest:
    tenant_id: str
    session_id: str
    request_id: str
    locale: str
    channel: str
    request_type_hint: str
    message_text: str
    user_id: str | None = None
    selected_assets: list[str] = field(default_factory=list)
    time_range: dict[str, str] | None = None
    ui_context: dict[str, Any] | None = None


def validate_frontend_request(payload: dict[str, Any]) -> FrontendRoutingRequest:
    required = (
        "tenant_id",
        "session_id",
        "request_id",
        "locale",
        "channel",
        "request_type_hint",
        "message_text",
    )
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValueError(f"Missing required request fields: {', '.join(missing)}")

    if payload["channel"] not in ALLOWED_CHANNELS:
        raise ValueError(f"Unsupported channel: {payload['channel']}")
    if payload["request_type_hint"] not in ALLOWED_REQUEST_HINTS:
        raise ValueError(f"Unsupported request_type_hint: {payload['request_type_hint']}")

    return FrontendRoutingRequest(
        tenant_id=str(payload["tenant_id"]),
        user_id=payload.get("user_id"),
        session_id=str(payload["session_id"]),
        request_id=str(payload["request_id"]),
        locale=str(payload["locale"]),
        channel=str(payload["channel"]),
        request_type_hint=str(payload["request_type_hint"]),
        message_text=str(payload["message_text"]),
        selected_assets=list(payload.get("selected_assets") or []),
        time_range=dict(payload["time_range"]) if payload.get("time_range") else None,
        ui_context=dict(payload["ui_context"]) if payload.get("ui_context") else None,
    )


def _demo_market_overview_rows(request: FrontendRoutingRequest) -> dict[str, list[dict[str, Any]]]:
    observed_at = dt.datetime(2026, 4, 30, 12, 0, tzinfo=dt.UTC)
    assets = request.selected_assets or ["btc", "eth", "sol"]
    ranking_rows = [
        {
            "asset_id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "market_cap_rank": 1,
            "market_cap_usd": 1_850_000_000_000,
            "price_usd": 95_000,
            "observed_at": observed_at,
        },
        {
            "asset_id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "market_cap_rank": 2,
            "market_cap_usd": 420_000_000_000,
            "price_usd": 3_200,
            "observed_at": observed_at,
        },
        {
            "asset_id": "solana",
            "symbol": "sol",
            "name": "Solana",
            "market_cap_rank": 5,
            "market_cap_usd": 80_000_000_000,
            "price_usd": 180,
            "observed_at": observed_at,
        },
    ]
    mover_rows = [
        {
            "asset_id": "solana",
            "symbol": "sol",
            "move_direction_24h": "positive",
            "price_change_pct_24h": 9.4,
            "move_band_24h": "medium",
            "observed_at": observed_at,
        },
        {
            "asset_id": "bitcoin",
            "symbol": "btc",
            "move_direction_24h": "positive",
            "price_change_pct_24h": 3.1,
            "move_band_24h": "low",
            "observed_at": observed_at,
        },
    ]
    dominance_rows = [
        {
            "dominance_group": "btc",
            "dominance_pct": 52.8,
            "market_cap_usd": 1_850_000_000_000,
            "observed_at": observed_at,
        },
        {
            "dominance_group": "eth",
            "dominance_pct": 12.4,
            "market_cap_usd": 420_000_000_000,
            "observed_at": observed_at,
        },
    ]
    comparison_rows = [
        {
            "asset_id": asset,
            "symbol": asset,
            "correlation_bucket": "large_cap" if asset in {"btc", "eth"} else "mid_cap",
            "price_change_pct_24h": 4.1 if asset == "eth" else 2.7,
            "price_change_pct_7d": 7.9 if asset == "eth" else 6.2,
            "observed_at": observed_at,
        }
        for asset in assets[:3]
    ]
    return {
        "rankings": ranking_rows,
        "movers": mover_rows,
        "dominance": dominance_rows,
        "comparisons": comparison_rows,
    }


def _build_dashboard_response(request: FrontendRoutingRequest) -> dict[str, Any]:
    datasets = _demo_market_overview_rows(request)
    dashboard_request = dashboard_market_overview.DashboardRequest(
        request_id=request.request_id,
        tenant_id=request.tenant_id,
        user_id=request.user_id,
        session_id=request.session_id,
        locale=request.locale,
        selected_assets=request.selected_assets,
        time_range=request.time_range,
    )
    response = dashboard_market_overview.build_market_overview_payload(
        request=dashboard_request,
        rankings=datasets["rankings"],
        movers=datasets["movers"],
        dominance=datasets["dominance"],
        comparisons=datasets["comparisons"],
    )
    response["routing"]["channel"] = request.channel
    response["routing"]["request_type_hint"] = request.request_type_hint
    return response


def _build_copilot_or_genie_response(request: FrontendRoutingRequest) -> dict[str, Any]:
    copilot_request = copilot_mvp.CopilotRequest(
        request_id=request.request_id,
        tenant_id=request.tenant_id,
        user_id=request.user_id,
        conversation_id=request.session_id,
        message_text=request.message_text,
        conversation_summary=None,
        retrieval_scope="market_overview_intelligence",
        selected_assets=request.selected_assets,
        time_range=request.time_range,
        policy_context={"locale": request.locale, "channel": request.channel},
        locale=request.locale,
    )
    response = copilot_mvp.build_copilot_response(copilot_request)
    response["routing"]["channel"] = request.channel
    response["routing"]["request_type_hint"] = request.request_type_hint
    return response


def route_frontend_request(payload: dict[str, Any]) -> dict[str, Any]:
    request = validate_frontend_request(payload)
    if request.request_type_hint == "dashboard_query":
        return _build_dashboard_response(request)
    if request.request_type_hint in {"analytics_nlq", "copilot"}:
        return _build_copilot_or_genie_response(request)

    if request.channel == "web_dashboard" and request.message_text.lower().strip() in {
        "market overview",
        "visao geral do mercado",
    }:
        return _build_dashboard_response(request)

    return _build_copilot_or_genie_response(request)
