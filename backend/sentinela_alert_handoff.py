from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any


def normalize_alert(alert: dict[str, Any], source: str = "sentinela") -> dict[str, Any]:
    payload = dict(alert)
    payload.setdefault("source", source)
    payload.setdefault("created_at", dt.datetime.now(dt.UTC).isoformat())
    return payload


def build_alert_handoff_rows(alerts: list[dict[str, Any]], source: str = "sentinela") -> list[dict[str, Any]]:
    return [normalize_alert(alert, source=source) for alert in alerts]


def write_alert_handoff_file(
    path: str | Path,
    alerts: list[dict[str, Any]],
    source: str = "sentinela",
) -> Path:
    rows = build_alert_handoff_rows(alerts, source=source)
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")
    return target_path
