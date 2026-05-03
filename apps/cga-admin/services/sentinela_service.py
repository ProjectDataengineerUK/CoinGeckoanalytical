from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_sentinela: Any = None


def _load() -> Any:
    global _sentinela
    if _sentinela is not None:
        return _sentinela
    try:
        spec = importlib.util.spec_from_file_location(
            "sentinela", _REPO_ROOT / "backend" / "sentinela.py"
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        _sentinela = mod
    except Exception:
        pass
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
        return {"ready": False, "blockers": [], "score": 0}
    try:
        return mod.evaluate_release_readiness(usage_events, bundle_events)
    except Exception:
        return {"ready": False, "blockers": ["sentinela_error"], "score": 0}
