from __future__ import annotations

import importlib.util
import logging
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_mvp_mod: Any = None


@dataclass(frozen=True)
class CopilotResult:
    body: str
    model_tier: str
    latency_ms: int
    cost_estimate: float | None
    citations: list[str]
    warnings: list[str]
    orchestrated: bool


def _load() -> Any | None:
    global _mvp_mod
    if _mvp_mod is not None:
        return _mvp_mod
    try:
        spec = importlib.util.spec_from_file_location(
            "copilot_mvp",
            _REPO_ROOT / "backend" / "copilot_mvp.py",
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        _mvp_mod = mod
    except Exception:
        pass
    return _mvp_mod


def ask(
    message: str,
    selected_assets: list[str] | None = None,
    tenant_id: str = "default",
    user_id: str | None = None,
) -> CopilotResult:
    mod = _load()
    if mod is None:
        return CopilotResult(
            body="Copilot indisponível — verifique a configuração do ambiente.",
            model_tier="unavailable",
            latency_ms=0,
            cost_estimate=None,
            citations=[],
            warnings=["copilot_unavailable"],
            orchestrated=False,
        )
    import time
    started = time.monotonic()
    request = mod.CopilotRequest(
        request_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        user_id=user_id,
        conversation_id=str(uuid.uuid4()),
        message_text=message,
        conversation_summary=None,
        retrieval_scope="market_gold",
        selected_assets=selected_assets or [],
        time_range=None,
        policy_context={},
        locale="pt-BR",
    )
    try:
        response = mod.build_copilot_response(request)
        routing = response.get("routing") or {}
        latency = int((time.monotonic() - started) * 1000)
        return CopilotResult(
            body=response.get("body", ""),
            model_tier=routing.get("model_tier") or "standard",
            latency_ms=routing.get("latency_ms") or latency,
            cost_estimate=routing.get("cost_estimate"),
            citations=response.get("citations") or [],
            warnings=response.get("warnings") or [],
            orchestrated=bool(routing.get("orchestrated")),
        )
    except Exception:
        _log.error("Copilot request failed", exc_info=True)
        return CopilotResult(
            body="Serviço temporariamente indisponível. Tente novamente.",
            model_tier="error",
            latency_ms=0,
            cost_estimate=None,
            citations=[],
            warnings=["copilot_error"],
            orchestrated=False,
        )
