from __future__ import annotations

import os
import sys
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

# ---------------------------------------------------------------------------
# Path setup — backend modules importable from repo root
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

# ---------------------------------------------------------------------------
# App init
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="CoinGecko Analytical",
    suppress_callback_exceptions=True,
)
server = app.server  # Exposed for WSGI servers used by Databricks Apps

# ---------------------------------------------------------------------------
# Import components after path setup
# ---------------------------------------------------------------------------
from components import chart_dashboard, copilot_panel, freshness_bar, genie_panel  # noqa: E402
from state import app_state  # noqa: E402

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
_NAV = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="", height="28px")),
                        dbc.Col(
                            dbc.NavbarBrand(
                                "CoinGecko Analytical",
                                style={"fontWeight": "700", "fontSize": "16px"},
                            )
                        ),
                    ],
                    align="center",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
            dbc.Nav(
                [
                    dbc.NavItem(
                        dbc.Badge(
                            "cga-analytics",
                            color="primary",
                            pill=True,
                            style={"fontSize": "11px"},
                        )
                    ),
                ],
                className="ms-auto",
                navbar=True,
            ),
        ],
        fluid=True,
    ),
    color="dark",
    dark=True,
    style={"padding": "8px 0"},
)

_FRESHNESS = dbc.Container(freshness_bar.layout(), fluid=True, style={"paddingTop": "8px"})

# Three-column main layout:
#   Left  (3 cols): Genie conversational panel — chart state controller
#   Center (6 cols): Chart dashboard — subscribes to Genie state
#   Right  (3 cols): Copilot panel — narrative analysis
_MAIN = dbc.Container(
    dbc.Row(
        [
            dbc.Col(
                genie_panel.layout(),
                width=3,
                style={
                    "height": "calc(100vh - 110px)",
                    "overflowY": "auto",
                    "padding": "0",
                },
            ),
            dbc.Col(
                chart_dashboard.layout(),
                width=6,
                style={
                    "height": "calc(100vh - 110px)",
                    "overflowY": "auto",
                    "borderLeft": "1px solid #E5E7EB",
                    "borderRight": "1px solid #E5E7EB",
                    "padding": "0",
                },
            ),
            dbc.Col(
                copilot_panel.layout(),
                width=3,
                style={
                    "height": "calc(100vh - 110px)",
                    "overflowY": "auto",
                    "padding": "0",
                },
            ),
        ],
        style={"height": "100%", "margin": "0"},
    ),
    fluid=True,
    style={"padding": "0"},
)

app.layout = html.Div(
    [
        *app_state.all_stores(),  # client-side state stores
        _NAV,
        _FRESHNESS,
        _MAIN,
    ],
    style={"backgroundColor": "#FFFFFF", "minHeight": "100vh"},
)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(
        debug=False,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", os.environ.get("DATABRICKS_APP_PORT", "8050"))),
    )
