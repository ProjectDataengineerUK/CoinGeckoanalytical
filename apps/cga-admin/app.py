from __future__ import annotations

import sys
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="CGA Admin",
    suppress_callback_exceptions=True,
)
server = app.server

from pages import sentinela, pipeline_health, cost_monitor, access_mgmt, audit_trail  # noqa: E402
from state import admin_state  # noqa: E402

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

_NAV_ITEMS = [
    ("sentinela",      "◉",  "Sentinela",      "Alertas e observabilidade"),
    ("pipeline",       "⚙️", "Pipeline Health", "Status de ingestão"),
    ("cost",           "💰", "Custo & Tokens",  "LLMOps telemetria"),
    ("access",         "🔐", "Acessos",          "Tenants e grupos"),
    ("audit",          "🔍", "Audit Trail",     "Rastreabilidade"),
]

_SIDEBAR = html.Div(
    [
        html.Div(
            [
                html.Div("CGA Admin", style={"fontWeight": "700", "fontSize": "15px", "color": "white"}),
                html.Div("Ops & Governance", style={"fontSize": "11px", "color": "#94A3B8"}),
            ],
            style={"padding": "16px 12px 12px"},
        ),
        html.Hr(style={"borderColor": "#334155", "margin": "0 12px 8px"}),
        dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Span(icon + " ", style={"marginRight": "6px"}),
                        html.Div(
                            [
                                html.Div(label, style={"fontSize": "13px", "fontWeight": "600"}),
                                html.Div(sub, style={"fontSize": "10px", "color": "#94A3B8"}),
                            ]
                        ),
                    ],
                    id=f"nav-{page_id}",
                    href=f"/{page_id}",
                    active="exact",
                    style={"padding": "10px 12px", "borderRadius": "6px", "margin": "2px 6px"},
                )
                for page_id, icon, label, sub in _NAV_ITEMS
            ],
            vertical=True,
            pills=True,
            style={"flexDirection": "column"},
        ),
        html.Div(
            dbc.Badge("cga-admin", color="secondary", pill=True, style={"fontSize": "10px"}),
            style={"position": "absolute", "bottom": "16px", "left": "12px"},
        ),
    ],
    style={
        "width": "220px",
        "minWidth": "220px",
        "backgroundColor": "#1E293B",
        "height": "100vh",
        "position": "fixed",
        "top": 0,
        "left": 0,
        "overflowY": "auto",
    },
)

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

app.layout = html.Div(
    [
        *admin_state.all_stores(),
        dcc.Location(id="url", refresh=False),
        _SIDEBAR,
        html.Div(
            id="page-content",
            style={
                "marginLeft": "220px",
                "padding": "0",
                "minHeight": "100vh",
                "backgroundColor": "#F8FAFC",
            },
        ),
    ]
)

# ---------------------------------------------------------------------------
# Page routing callback
# ---------------------------------------------------------------------------

_PAGE_MAP = {
    "/sentinela": sentinela.layout,
    "/pipeline": pipeline_health.layout,
    "/cost": cost_monitor.layout,
    "/access": access_mgmt.layout,
    "/audit": audit_trail.layout,
    "/": sentinela.layout,
    "": sentinela.layout,
}


@callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname: str):
    page_fn = _PAGE_MAP.get(pathname or "/", sentinela.layout)
    return page_fn()


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8051)
