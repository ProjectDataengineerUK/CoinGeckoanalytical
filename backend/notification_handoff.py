from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any


def normalize_notification(
    notification: dict[str, Any],
    source: str = "coingeckoanalytical",
) -> dict[str, Any]:
    payload = dict(notification)
    payload.setdefault("source", source)
    payload.setdefault("created_at", dt.datetime.now(dt.UTC).isoformat())
    return payload


def build_notification_handoff_rows(
    notifications: list[dict[str, Any]],
    source: str = "coingeckoanalytical",
) -> list[dict[str, Any]]:
    return [normalize_notification(notification, source=source) for notification in notifications]


def write_notification_handoff_file(
    path: str | Path,
    notifications: list[dict[str, Any]],
    source: str = "coingeckoanalytical",
) -> Path:
    rows = build_notification_handoff_rows(notifications, source=source)
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")
    return target_path
