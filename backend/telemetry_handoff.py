from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend import copilot_mvp


def build_usage_handoff_row(
    request: copilot_mvp.CopilotRequest,
    response: dict[str, Any],
    latency_ms: int = 120,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    total_tokens: int | None = None,
    cost_estimate: float | None = None,
) -> dict[str, Any]:
    return copilot_mvp.build_databricks_usage_row(
        request,
        response,
        latency_ms=latency_ms,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        cost_estimate=cost_estimate,
    )


def write_usage_handoff_file(
    path: str | Path,
    request: copilot_mvp.CopilotRequest,
    response: dict[str, Any],
    latency_ms: int = 120,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    total_tokens: int | None = None,
    cost_estimate: float | None = None,
) -> Path:
    row = build_usage_handoff_row(
        request,
        response,
        latency_ms=latency_ms,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        cost_estimate=cost_estimate,
    )
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps([row], indent=2, sort_keys=True), encoding="utf-8")
    return target_path
