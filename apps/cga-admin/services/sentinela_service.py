from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_sentinela: Any = None
_LOG = logging.getLogger(__name__)


def _load() -> Any:
    global _sentinela
    if _sentinela is not None:
        return _sentinela
    try:
        spec = importlib.util.spec_from_file_location(
            "sentinela", _REPO_ROOT / "backend" / "sentinela.py"
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        sys.modules["sentinela"] = mod
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        _sentinela = mod
    except Exception:
        _LOG.error("Failed to load sentinela backend", exc_info=True)
    return _sentinela


def analyze_usage(events: list[dict[str, Any]]) -> dict[str, Any]:
    mod = _load()
    if not mod or not events:
        return {"alerts": [], "summary": {}, "total_events": 0}
    return mod.analyze_usage_events(events)


def analyze_bundle_runs(events: list[dict[str, Any]]) -> dict[str, Any]:
    mod = _load()
    if not mod or not events:
        return {"alerts": [], "success_rate": 1.0, "total_runs": 0}
    return mod.analyze_bundle_runs(events)


def evaluate_readiness(
    usage_events: list[dict[str, Any]],
    bundle_events: list[dict[str, Any]],
) -> dict[str, Any]:
    mod = _load()
    if not mod:
        return {"ready": False, "blockers": ["sentinela_backend_unavailable"], "score": 0}
    try:
        result = mod.evaluate_release_readiness(usage_events, bundle_runs=bundle_events)
        checks = list(result.get("checks") or [])
        passed = sum(1 for check in checks if _check_passed(check))
        total = len(checks)
        score = int(round((passed / total) * 100)) if total else 0
        blockers = list(result.get("blockers") or [])
        if _only_missing_telemetry(blockers) and _bundle_runs_healthy(bundle_events):
            result["warnings"] = blockers
            result["blockers"] = []
            result["ready"] = True
            result["operational_state"] = "monitoring_limited"
        result["score"] = score
        return result
    except Exception:
        _LOG.error("Sentinela readiness evaluation failed", exc_info=True)
        return {"ready": False, "blockers": ["sentinela_error"], "score": 0}


def _check_passed(check: dict[str, Any]) -> bool:
    if "passed" in check:
        return bool(check.get("passed"))
    return str(check.get("status", "")).lower() == "pass"


def _only_missing_telemetry(blockers: list[dict[str, Any] | str]) -> bool:
    if not blockers:
        return False
    kinds = {
        blocker.get("kind") if isinstance(blocker, dict) else str(blocker)
        for blocker in blockers
    }
    return kinds == {"missing_telemetry"}


def _bundle_runs_healthy(bundle_events: list[dict[str, Any]]) -> bool:
    if not bundle_events:
        return True
    healthy_states = {"SUCCESS", "SUCCEEDED", "COMPLETED"}
    return all(str(event.get("status", "")).upper() in healthy_states for event in bundle_events)
