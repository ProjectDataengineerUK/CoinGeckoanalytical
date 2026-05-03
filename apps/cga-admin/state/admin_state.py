from __future__ import annotations

from dash import dcc

STORE_PAGE = "admin-page-store"          # {"page": "sentinela"}
STORE_ALERTS = "admin-alerts-store"      # [{kind, severity, message, ...}]
STORE_REFRESH = "admin-refresh-store"    # {"ts": "..."}  — auto-refresh trigger


def page_store() -> dcc.Store:
    return dcc.Store(id=STORE_PAGE, storage_type="session", data={"page": "sentinela"})


def alerts_store() -> dcc.Store:
    return dcc.Store(id=STORE_ALERTS, storage_type="memory", data=[])


def refresh_store() -> dcc.Store:
    return dcc.Store(id=STORE_REFRESH, storage_type="memory", data={"ts": ""})


def all_stores() -> list[dcc.Store]:
    return [page_store(), alerts_store(), refresh_store()]
