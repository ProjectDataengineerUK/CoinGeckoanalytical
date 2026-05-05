from __future__ import annotations

import os
import sys
from pathlib import Path

# Databricks Apps installs packages into .venv but launches via system python3.
# Prepend venv site-packages so third-party imports resolve.
_venv_lib = Path(__file__).parent / ".venv" / "lib"
for _sp in sorted(_venv_lib.glob("python*/site-packages")):
    if str(_sp) not in sys.path:
        sys.path.insert(0, str(_sp))


def _load_app_secrets() -> None:
    import base64
    import json
    import urllib.parse
    import urllib.request

    raw_host = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
    client_id = os.environ.get("DATABRICKS_CLIENT_ID", "")
    client_secret = os.environ.get("DATABRICKS_CLIENT_SECRET", "")

    if not (raw_host and client_id and client_secret):
        return

    host = raw_host if raw_host.startswith("https://") else f"https://{raw_host}"

    # SEC-06: validate host is a known Databricks domain before sending credentials
    from urllib.parse import urlparse as _urlparse

    _hostname = _urlparse(host).hostname or ""
    _ALLOWED_SUFFIXES = (
        ".azuredatabricks.net",
        ".gcp.databricks.com",
        ".databricks.com",
    )

    if not any(_hostname.endswith(s) for s in _ALLOWED_SUFFIXES):
        print(
            f"[cga-analytics] secrets bootstrap: untrusted host {_hostname!r} — skipped",
            file=sys.stderr,
            flush=True,
        )
        return

    needed = {
        k: v
        for k, v in {
            "DATABRICKS_SQL_WAREHOUSE_ID": (
                "cga-app-config",
                "sql_warehouse_id",
            ),
            "DATABRICKS_GENIE_SPACE_ID": (
                "cga-app-config",
                "genie_space_id",
            ),
        }.items()
        if not os.environ.get(k)
    }

    if not needed:
        return

    try:
        body = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "all-apis",
            }
        ).encode()

        req = urllib.request.Request(
            f"{host}/oidc/v1/token",
            data=body,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            token = json.loads(resp.read())["access_token"]

    except Exception as exc:
        print(
            f"[cga-analytics] secrets bootstrap: token error — {type(exc).__name__}",
            file=sys.stderr,
            flush=True,
        )
        return

    for env_var, (scope, key) in needed.items():
        try:
            params = urllib.parse.urlencode(
                {
                    "scope": scope,
                    "key": key,
                }
            )

            req = urllib.request.Request(
                f"{host}/api/2.0/secrets/get?{params}",
                headers={"Authorization": f"Bearer {token}"},
                method="GET",
            )

            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = json.loads(resp.read()).get("value", "")

            if raw:
                os.environ[env_var] = base64.b64decode(raw).decode("utf-8").strip()

        except Exception as exc:
            print(
                f"[cga-analytics] secrets bootstrap: {scope}/{key} error — {type(exc).__name__}",
                file=sys.stderr,
                flush=True,
            )


_load_app_secrets()

# ---------------------------------------------------------------------------
# Normalize environment variables
# ---------------------------------------------------------------------------
if os.environ.get("DATABRICKS_GENIE_SPACE_ID") and not os.environ.get("GENIE_SPACE_ID"):
    os.environ["GENIE_SPACE_ID"] = os.environ["DATABRICKS_GENIE_SPACE_ID"]

if os.environ.get("GENIE_SPACE_ID") and not os.environ.get("DATABRICKS_GENIE_SPACE_ID"):
    os.environ["DATABRICKS_GENIE_SPACE_ID"] = os.environ["GENIE_SPACE_ID"]

if os.environ.get("DATABRICKS_SQL_WAREHOUSE_ID") and not os.environ.get("SQL_WAREHOUSE_ID"):
    os.environ["SQL_WAREHOUSE_ID"] = os.environ["DATABRICKS_SQL_WAREHOUSE_ID"]

if os.environ.get("SQL_WAREHOUSE_ID") and not os.environ.get("DATABRICKS_SQL_WAREHOUSE_ID"):
    os.environ["DATABRICKS_SQL_WAREHOUSE_ID"] = os.environ["SQL_WAREHOUSE_ID"]

print(
    "[cga-analytics] DATABRICKS_GENIE_SPACE_ID =",
    os.environ.get("DATABRICKS_GENIE_SPACE_ID"),
    flush=True,
)
print(
    "[cga-analytics] GENIE_SPACE_ID =",
    os.environ.get("GENIE_SPACE_ID"),
    flush=True,
)
print(
    "[cga-analytics] DATABRICKS_SQL_WAREHOUSE_ID =",
    os.environ.get("DATABRICKS_SQL_WAREHOUSE_ID"),
    flush=True,
)
print(
    "[cga-analytics] SQL_WAREHOUSE_ID =",
    os.environ.get("SQL_WAREHOUSE_ID"),
    flush=True,
)

import dash
import dash_bootstrap_components as dbc
from dash import html

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
                                style={
                                    "fontWeight": "700",
                                    "fontSize": "16px",
                                },
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

_FRESHNESS = dbc.Container(
    freshness_bar.layout(),
    fluid=True,
    style={"paddingTop": "8px"},
)

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
        style={
            "height": "100%",
            "margin": "0",
        },
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
    style={
        "backgroundColor": "#FFFFFF",
        "minHeight": "100vh",
    },
)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(
        debug=False,
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                os.environ.get("DATABRICKS_APP_PORT", "8050"),
            )
        ),
    )