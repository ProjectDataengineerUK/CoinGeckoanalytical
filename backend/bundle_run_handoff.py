from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_bundle_run_handoff_row(
    job_name: str,
    status: str,
    run_id: str | None = None,
    result_state: str | None = None,
    update_time: str | None = None,
    duration_ms: int | None = None,
) -> dict[str, Any]:
    return {
        "job_name": job_name,
        "run_id": run_id,
        "status": status,
        "result_state": result_state,
        "update_time": update_time,
        "duration_ms": duration_ms,
    }


def write_bundle_run_handoff_file(
    path: str | Path,
    job_name: str,
    status: str,
    run_id: str | None = None,
    result_state: str | None = None,
    update_time: str | None = None,
    duration_ms: int | None = None,
) -> Path:
    row = build_bundle_run_handoff_row(
        job_name=job_name,
        status=status,
        run_id=run_id,
        result_state=result_state,
        update_time=update_time,
        duration_ms=duration_ms,
    )
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps([row], indent=2, sort_keys=True), encoding="utf-8")
    return target_path
