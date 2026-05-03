from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import Input, Output, callback, html

from state.app_state import STORE_FRESHNESS, STORE_GENIE

FRESHNESS_BAR_ID = "freshness-bar"


def layout() -> html.Div:
    return html.Div(id=FRESHNESS_BAR_ID, style={"marginBottom": "8px"})


@callback(
    Output(FRESHNESS_BAR_ID, "children"),
    Input(STORE_GENIE, "data"),
    Input(STORE_FRESHNESS, "data"),
)
def update_freshness(genie_state: dict, freshness_state: dict):
    genie_status = (genie_state or {}).get("status", "idle")
    genie_ms = (genie_state or {}).get("latency_ms", 0)
    market_wm = (freshness_state or {}).get("market")

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
            dbc.Badge("◈ Genie inativo", color="secondary", pill=True, className="me-2", style={"fontSize": "11px"})
        )
    else:
        badges.append(
            dbc.Badge(f"◈ Genie: {genie_status}", color="warning", pill=True, className="me-2", style={"fontSize": "11px"})
        )

    if market_wm:
        badges.append(
            dbc.Badge(f"🕐 Dados: {market_wm}", color="info", pill=True, className="me-2", style={"fontSize": "11px"})
        )
    else:
        badges.append(
            dbc.Badge("🕐 Freshness: pendente", color="light", text_color="dark", pill=True, className="me-2", style={"fontSize": "11px"})
        )

    badges.append(
        dbc.Badge("Unity Catalog · Gold", color="dark", pill=True, style={"fontSize": "11px"})
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
        },
    )
