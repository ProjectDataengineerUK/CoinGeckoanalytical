from __future__ import annotations

import traceback

import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

from state.app_state import STORE_FRESHNESS, STORE_GENIE

FRESHNESS_BAR_ID = "freshness-bar"
FRESHNESS_INTERVAL_ID = "freshness-interval"


def layout() -> html.Div:
    return html.Div(
        [
            dcc.Interval(
                id=FRESHNESS_INTERVAL_ID,
                interval=60_000,
                n_intervals=0,
            ),
            html.Div(id=FRESHNESS_BAR_ID),
        ],
        style={"marginBottom": "8px"},
    )


@callback(
    Output(STORE_FRESHNESS, "data"),
    Input(FRESHNESS_INTERVAL_ID, "n_intervals"),
)
def poll_freshness(n: int) -> dict:
    from services import sql_service

    print("[FRESHNESS] callback acionado. n_intervals =", n, flush=True)

    try:
        wm = sql_service.fetch_market_freshness()

        print("[FRESHNESS] market freshness =", wm, flush=True)

        if not wm:
            return {
                "market": None,
                "status": "empty",
                "error": None,
            }

        return {
            "market": wm,
            "status": "completed",
            "error": None,
        }

    except Exception as exc:
        print("[FRESHNESS] ERROR:", repr(exc), flush=True)
        traceback.print_exc()

        return {
            "market": None,
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
        }


@callback(
    Output(FRESHNESS_BAR_ID, "children"),
    Input(STORE_GENIE, "data"),
    Input(STORE_FRESHNESS, "data"),
)
def update_freshness(genie_state: dict | None, freshness_state: dict | None):
    genie_state = genie_state or {}
    freshness_state = freshness_state or {}

    genie_status = genie_state.get("status", "idle")
    genie_ms = genie_state.get("latency_ms", 0)

    market_wm = freshness_state.get("market")
    freshness_status = freshness_state.get("status", "pending")
    freshness_error = freshness_state.get("error")

    badges = []

    if genie_status == "completed":
        badges.append(
            dbc.Badge(
                f"◈ Genie ativo · {genie_ms} ms",
                color="success",
                pill=True,
                className="me-2",
                style={"fontSize": "11px"},
            )
        )
    elif genie_status == "idle":
        badges.append(
            dbc.Badge(
                "◈ Genie inativo",
                color="secondary",
                pill=True,
                className="me-2",
                style={"fontSize": "11px"},
            )
        )
    elif genie_status == "error":
        badges.append(
            dbc.Badge(
                "◈ Genie erro",
                color="danger",
                pill=True,
                className="me-2",
                style={"fontSize": "11px"},
            )
        )
    else:
        badges.append(
            dbc.Badge(
                f"◈ Genie: {genie_status}",
                color="warning",
                pill=True,
                className="me-2",
                style={"fontSize": "11px"},
            )
        )

    if market_wm:
        badges.append(
            dbc.Badge(
                f"🕐 Dados: {market_wm}",
                color="info",
                pill=True,
                className="me-2",
                style={"fontSize": "11px"},
            )
        )
    elif freshness_status == "error":
        badges.append(
            dbc.Badge(
                f"🕐 Freshness erro: {freshness_error}",
                color="danger",
                pill=True,
                className="me-2",
                style={
                    "fontSize": "11px",
                    "maxWidth": "520px",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "whiteSpace": "nowrap",
                },
            )
        )
    elif freshness_status == "empty":
        badges.append(
            dbc.Badge(
                "🕐 Freshness: sem dados",
                color="warning",
                pill=True,
                className="me-2",
                style={"fontSize": "11px"},
            )
        )
    else:
        badges.append(
            dbc.Badge(
                "🕐 Freshness: pendente",
                color="light",
                text_color="dark",
                pill=True,
                className="me-2",
                style={"fontSize": "11px"},
            )
        )

    badges.append(
        dbc.Badge(
            "Unity Catalog · Gold",
            color="dark",
            pill=True,
            style={"fontSize": "11px"},
        )
    )

    return html.Div(
        badges,
        style={
            "display": "flex",
            "alignItems": "center",
            "padding": "6px 12px",
            "backgroundColor": "#F8FAFC",
            "border": "1px solid #E2E8F0",
            "borderRadius": "6px",
            "gap": "4px",
            "flexWrap": "wrap",
        },
    )