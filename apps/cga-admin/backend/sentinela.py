from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


DEFAULT_ROUTE_THRESHOLDS: dict[str, dict[str, int | float]] = {
    "genie": {
        "max_latency_ms": 500,
        "max_cost_estimate": 0.02,
        "max_total_tokens": 1200,
    },
    "copilot": {
        "max_latency_ms": 1200,
        "max_cost_estimate": 0.05,
        "max_total_tokens": 4000,
    },
    "dashboard_api": {
        "max_latency_ms": 250,
        "max_cost_estimate": 0.005,
        "max_total_tokens": 800,
    },
    "internal_app": {
        "max_latency_ms": 800,
        "max_cost_estimate": 0.03,
        "max_total_tokens": 2500,
    },
}


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


@dataclass(frozen=True)
class ReadinessPolicy:
    max_latency_ms: int = 1000
    max_cost_estimate: float = 0.05
    max_total_tokens: int = 4000
    require_freshness: bool = True
    route_thresholds: dict[str, dict[str, int | float]] = field(default_factory=dict)


@dataclass(frozen=True)
class BundleRunEvent:
    job_name: str
    run_id: str | None
    status: str
    result_state: str | None
    update_time: str | None
    duration_ms: int | None


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


def analyze_bundle_runs(events: list[dict[str, Any]]) -> dict[str, Any]:
    alerts: list[dict[str, Any]] = []
    summary = {
        "runs": len(events),
        "successes": 0,
        "failures": 0,
        "running": 0,
        "cancelled": 0,
    }

    for event in events:
        status = str(event.get("status", "unknown")).lower()
        job_name = str(event.get("job_name", "unknown"))

        if status in {"success", "succeeded", "completed"}:
            summary["successes"] += 1
        elif status in {"running", "queued", "pending"}:
            summary["running"] += 1
        elif status in {"cancelled", "canceled"}:
            summary["cancelled"] += 1
            summary["failures"] += 1
            alerts.append(_bundle_alert("bundle_cancelled", job_name, event))
        else:
            summary["failures"] += 1
            alerts.append(_bundle_alert("bundle_failure", job_name, event))

    summary["alerts"] = len(alerts)
    return {"summary": summary, "alerts": alerts}


def evaluate_release_readiness(
    events: list[dict[str, Any]],
    policy: ReadinessPolicy | dict[str, Any] | None = None,
    bundle_runs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    readiness_policy = _coerce_readiness_policy(policy)
    analysis = analyze_usage_events(events)
    summary = analysis["summary"]

    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    combined_alerts = list(analysis["alerts"])
    bundle_summary = None

    checks.append(_check_telemetry_present(summary["events"] > 0))
    if not summary["events"]:
        blockers.append(
            _blocker(
                "missing_telemetry",
                None,
                None,
                "No telemetry events were provided.",
            )
        )

    checks.append(_check_summary_metric("error_free", summary["errors"] == 0, summary["errors"]))
    if summary["errors"] > 0:
        blockers.extend(
            _blockers_from_alerts(
                [alert for alert in analysis["alerts"] if alert["kind"] == "error_spike"]
            )
        )

    route_checks = _evaluate_route_thresholds(events, readiness_policy)
    checks.extend(route_checks["checks"])
    blockers.extend(route_checks["blockers"])

    checks.append(_check_summary_metric("alert_free", summary["alerts"] == 0, summary["alerts"]))

    if bundle_runs is not None:
        bundle_analysis = analyze_bundle_runs(bundle_runs)
        bundle_summary = bundle_analysis["summary"]
        combined_alerts.extend(bundle_analysis["alerts"])
        checks.append(
            _check_summary_metric("bundle_runs_failure_free", bundle_summary["failures"] == 0, bundle_summary["failures"])
        )
        if bundle_summary["failures"] > 0:
            blockers.extend(
                _blockers_from_bundle_alerts(bundle_analysis["alerts"])
            )

    return {
        "ready": not blockers,
        "summary": summary,
        "checks": checks,
        "blockers": blockers,
        "alerts": combined_alerts,
        "policy": _policy_payload(readiness_policy),
        "bundle_summary": bundle_summary,
    }


def _alert(kind: str, route_selected: str, event: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": kind,
        "request_id": event.get("request_id"),
        "tenant_id": event.get("tenant_id"),
        "route_selected": route_selected,
        "message": _alert_message(kind),
    }


def _bundle_alert(kind: str, job_name: str, event: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": kind,
        "job_name": job_name,
        "run_id": event.get("run_id"),
        "message": _bundle_alert_message(kind, job_name),
    }


def _coerce_readiness_policy(policy: ReadinessPolicy | dict[str, Any] | None) -> ReadinessPolicy:
    if policy is None:
        return ReadinessPolicy()
    if isinstance(policy, ReadinessPolicy):
        return policy
    return ReadinessPolicy(
        max_latency_ms=int(policy.get("max_latency_ms", 1000) or 1000),
        max_cost_estimate=float(policy.get("max_cost_estimate", 0.05) or 0.05),
        max_total_tokens=int(policy.get("max_total_tokens", 4000) or 4000),
        require_freshness=bool(policy.get("require_freshness", True)),
        route_thresholds=dict(policy.get("route_thresholds") or {}),
    )


def _policy_payload(policy: ReadinessPolicy) -> dict[str, Any]:
    return {
        "max_latency_ms": policy.max_latency_ms,
        "max_cost_estimate": policy.max_cost_estimate,
        "max_total_tokens": policy.max_total_tokens,
        "require_freshness": policy.require_freshness,
        "route_thresholds": policy.route_thresholds,
    }


def _route_thresholds_for(policy: ReadinessPolicy, route_selected: str) -> dict[str, int | float]:
    thresholds = dict(DEFAULT_ROUTE_THRESHOLDS.get(route_selected, {}))
    thresholds.update(policy.route_thresholds.get(route_selected, {}))
    thresholds.setdefault("max_latency_ms", policy.max_latency_ms)
    thresholds.setdefault("max_cost_estimate", policy.max_cost_estimate)
    thresholds.setdefault("max_total_tokens", policy.max_total_tokens)
    return thresholds


def _evaluate_route_thresholds(
    events: list[dict[str, Any]],
    policy: ReadinessPolicy,
) -> dict[str, list[dict[str, Any]]]:
    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []

    for event in events:
        route_selected = str(event.get("route_selected", "unknown"))
        thresholds = _route_thresholds_for(policy, route_selected)
        latency_ms = int(event.get("latency_ms", 0) or 0)
        cost_estimate = float(event.get("cost_estimate") or 0.0)
        total_tokens = int(event.get("total_tokens", 0) or 0)
        freshness = event.get("freshness_watermark")
        status = str(event.get("response_status", "unknown"))

        latency_ok = latency_ms < int(thresholds["max_latency_ms"])
        cost_ok = cost_estimate < float(thresholds["max_cost_estimate"])
        tokens_ok = total_tokens < int(thresholds["max_total_tokens"])
        freshness_ok = not policy.require_freshness or freshness not in {None, "", "unknown", "pending"}
        status_ok = status != "error"

        checks.append(
            {
                "name": f"{route_selected}_latency_within_threshold",
                "status": "pass" if latency_ok else "fail",
                "value": latency_ms,
                "threshold": thresholds["max_latency_ms"],
            }
        )
        checks.append(
            {
                "name": f"{route_selected}_cost_within_threshold",
                "status": "pass" if cost_ok else "fail",
                "value": cost_estimate,
                "threshold": thresholds["max_cost_estimate"],
            }
        )
        checks.append(
            {
                "name": f"{route_selected}_tokens_within_threshold",
                "status": "pass" if tokens_ok else "fail",
                "value": total_tokens,
                "threshold": thresholds["max_total_tokens"],
            }
        )
        checks.append(
            {
                "name": f"{route_selected}_freshness_valid",
                "status": "pass" if freshness_ok else "fail",
                "value": freshness,
                "threshold": "required" if policy.require_freshness else "optional",
            }
        )
        checks.append(
            {
                "name": f"{route_selected}_status_ok",
                "status": "pass" if status_ok else "fail",
                "value": status,
                "threshold": "success",
            }
        )

        if not latency_ok:
            blockers.append(
                _blocker(
                    "latency_breach",
                    route_selected,
                    event,
                    "Route latency exceeded readiness threshold.",
                )
            )
        if not cost_ok:
            blockers.append(
                _blocker(
                    "cost_anomaly",
                    route_selected,
                    event,
                    "Route cost exceeded readiness threshold.",
                )
            )
        if not tokens_ok:
            blockers.append(
                _blocker(
                    "token_spike",
                    route_selected,
                    event,
                    "Route token usage exceeded readiness threshold.",
                )
            )
        if not freshness_ok:
            blockers.append(
                _blocker(
                    "freshness_gap",
                    route_selected,
                    event,
                    "Freshness metadata is missing or stale.",
                )
            )
        if not status_ok:
            blockers.append(
                _blocker(
                    "error_spike",
                    route_selected,
                    event,
                    "Route returned an error status.",
                )
            )

    return {"checks": checks, "blockers": blockers}


def _check_telemetry_present(passed: bool) -> dict[str, Any]:
    return {
        "name": "telemetry_present",
        "status": "pass" if passed else "fail",
        "threshold": "at_least_one_event",
        "value": int(passed),
    }


def _check_summary_metric(name: str, passed: bool, value: int) -> dict[str, Any]:
    return {
        "name": name,
        "status": "pass" if passed else "fail",
        "threshold": 0,
        "value": value,
    }


def _blocker(
    kind: str,
    route_selected: str | None,
    event: dict[str, Any] | None,
    message: str,
) -> dict[str, Any]:
    return {
        "kind": kind,
        "request_id": None if event is None else event.get("request_id"),
        "tenant_id": None if event is None else event.get("tenant_id"),
        "route_selected": route_selected,
        "message": message,
        "escalation": _escalation_for(kind),
    }


def _blockers_from_alerts(alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        _blocker(alert["kind"], alert.get("route_selected"), alert, alert["message"])
        for alert in alerts
    ]


def _blockers_from_bundle_alerts(alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "kind": alert["kind"],
            "job_name": alert.get("job_name"),
            "run_id": alert.get("run_id"),
            "message": alert["message"],
            "escalation": _escalation_for(alert["kind"]),
        }
        for alert in alerts
    ]


def _escalation_for(kind: str) -> str:
    escalation_map = {
        "error_spike": "page_oncall",
        "latency_breach": "investigate_performance",
        "cost_anomaly": "review_budget",
        "freshness_gap": "block_release",
        "token_spike": "review_model_usage",
        "missing_telemetry": "block_release",
        "bundle_failure": "page_oncall",
        "bundle_cancelled": "page_oncall",
    }
    return escalation_map.get(kind, "review")


def _alert_message(kind: str) -> str:
    messages = {
        "error_spike": "Response errors detected for this route.",
        "latency_breach": "Latency exceeded the operational threshold.",
        "cost_anomaly": "Estimated cost exceeded the target threshold.",
        "freshness_gap": "Freshness metadata is missing or stale.",
        "token_spike": "Token usage is above the expected copilot bound.",
    }
    return messages[kind]


def _bundle_alert_message(kind: str, job_name: str) -> str:
    messages = {
        "bundle_failure": f"Databricks bundle job {job_name} failed.",
        "bundle_cancelled": f"Databricks bundle job {job_name} was cancelled.",
    }
    return messages[kind]
