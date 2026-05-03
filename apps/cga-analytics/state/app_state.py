from __future__ import annotations

from dash import dcc

# ---------------------------------------------------------------------------
# Shared client-side state stores
# Persisted in browser via dcc.Store — all callbacks read/write these.
# ---------------------------------------------------------------------------

STORE_GENIE = "genie-state"          # {sql, answer_text, latency_ms, status}
STORE_ASSETS = "assets-state"        # {selected: ["bitcoin", ...]}
STORE_COPILOT = "copilot-history"    # [{role, text, tier, ts}, ...]
STORE_FRESHNESS = "freshness-state"  # {market: "...", genie: "..."}


def genie_store() -> dcc.Store:
    return dcc.Store(
        id=STORE_GENIE,
        storage_type="session",
        data={"sql": None, "answer_text": "", "latency_ms": 0, "status": "idle"},
    )


def assets_store() -> dcc.Store:
    return dcc.Store(id=STORE_ASSETS, storage_type="session", data={"selected": []})


def copilot_store() -> dcc.Store:
    return dcc.Store(id=STORE_COPILOT, storage_type="session", data=[])


def freshness_store() -> dcc.Store:
    return dcc.Store(
        id=STORE_FRESHNESS,
        storage_type="session",
        data={"market": None, "genie": None},
    )


def all_stores() -> list[dcc.Store]:
    return [genie_store(), assets_store(), copilot_store(), freshness_store()]
