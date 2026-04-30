from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UsageEvent:
    event_time: str
    request_id: str
    tenant_id: str
    user_id: str | None
    route_selected: str
    model_or_engine: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    latency_ms: int
    cost_estimate: float | None
    freshness_watermark: str | None
    response_status: str


def analyze_usage_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    alerts: list[dict[str, Any]] = []
    summary = {
        "events": len(events),
        "errors": 0,
        "partials": 0,
        "refusals": 0,
        "max_latency_ms": 0,
        "total_cost_estimate": 0.0,
    }

    for event in events:
        latency_ms = int(event.get("latency_ms", 0) or 0)
        cost_estimate = float(event.get("cost_estimate") or 0.0)
        route_selected = str(event.get("route_selected", "unknown"))
        status = str(event.get("response_status", "unknown"))
        freshness = event.get("freshness_watermark")

        summary["max_latency_ms"] = max(summary["max_latency_ms"], latency_ms)
        summary["total_cost_estimate"] += cost_estimate

        if status == "error":
            summary["errors"] += 1
            alerts.append(_alert("error_spike", route_selected, event))
        elif status == "partial":
            summary["partials"] += 1
        elif status == "refused":
            summary["refusals"] += 1

        if latency_ms >= 1000:
            alerts.append(_alert("latency_breach", route_selected, event))
        if cost_estimate >= 0.05:
            alerts.append(_alert("cost_anomaly", route_selected, event))
        if freshness in {None, "", "unknown", "pending"}:
            alerts.append(_alert("freshness_gap", route_selected, event))
        if route_selected == "copilot" and (event.get("total_tokens") or 0) >= 4000:
            alerts.append(_alert("token_spike", route_selected, event))

    summary["alerts"] = len(alerts)
    return {"summary": summary, "alerts": alerts}


def _alert(kind: str, route_selected: str, event: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": kind,
        "request_id": event.get("request_id"),
        "tenant_id": event.get("tenant_id"),
        "route_selected": route_selected,
        "message": _alert_message(kind),
    }


def _alert_message(kind: str) -> str:
    messages = {
        "error_spike": "Response errors detected for this route.",
        "latency_breach": "Latency exceeded the operational threshold.",
        "cost_anomaly": "Estimated cost exceeded the target threshold.",
        "freshness_gap": "Freshness metadata is missing or stale.",
        "token_spike": "Token usage is above the expected copilot bound.",
    }
    return messages[kind]
