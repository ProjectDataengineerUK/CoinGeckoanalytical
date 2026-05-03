from __future__ import annotations

import datetime

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

from state.app_state import STORE_ASSETS, STORE_COPILOT

# ---------------------------------------------------------------------------
# Component IDs
# ---------------------------------------------------------------------------

COPILOT_INPUT_ID = "copilot-input"
COPILOT_SEND_ID = "copilot-send"
COPILOT_HISTORY_DIV_ID = "copilot-history-div"
COPILOT_TIER_BADGE_ID = "copilot-tier-badge"

_TIER_COLORS = {"light": "info", "standard": "primary", "complex": "danger", "error": "warning"}
_TIER_LABELS = {
    "light": "⚡ Light — Gemma 12B",
    "standard": "🔷 Standard — GPT-OSS 120B",
    "complex": "🧠 Complex — Qwen3 80B (multi-agente)",
    "error": "⚠ Erro",
}


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def layout() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.Span("🤖", style={"fontSize": "18px"}),
                    html.Span(
                        " Copilot de Mercado",
                        style={"fontWeight": "700", "fontSize": "14px", "marginLeft": "6px"},
                    ),
                ],
                style={"marginBottom": "10px"},
            ),
            # Chat history
            html.Div(
                id=COPILOT_HISTORY_DIV_ID,
                style={
                    "height": "420px",
                    "overflowY": "auto",
                    "marginBottom": "10px",
                    "padding": "8px",
                    "backgroundColor": "#F9FAFB",
                    "borderRadius": "6px",
                    "border": "1px solid #E5E7EB",
                },
                children=[
                    _assistant_bubble(
                        "Olá! Sou o Copilot de mercado. Faço análise narrativa com dados Gold "
                        "em tempo real. Para consultas estruturadas (rankings, filtros, comparações), "
                        "use o painel Genie à esquerda.",
                        tier="standard",
                        ts="",
                    )
                ],
            ),
            # Tier badge
            html.Div(id=COPILOT_TIER_BADGE_ID, style={"marginBottom": "8px"}),
            # Input row
            dbc.InputGroup(
                [
                    dbc.Textarea(
                        id=COPILOT_INPUT_ID,
                        placeholder="Analise o mercado crypto atual...",
                        rows=2,
                        style={"fontSize": "13px", "resize": "none"},
                    ),
                    dbc.Button(
                        "→",
                        id=COPILOT_SEND_ID,
                        color="dark",
                        style={"minWidth": "44px"},
                    ),
                ]
            ),
            html.Div(
                "Tier automático: Light → Standard → Complex (orquestrador multi-agente)",
                style={"fontSize": "10px", "color": "#9CA3AF", "marginTop": "4px", "textAlign": "center"},
            ),
        ],
        style={
            "padding": "16px",
            "backgroundColor": "#FAFAFA",
            "borderLeft": "1px solid #E5E7EB",
            "height": "100%",
            "overflowY": "auto",
        },
    )


# ---------------------------------------------------------------------------
# Callback
# ---------------------------------------------------------------------------

@callback(
    Output(COPILOT_HISTORY_DIV_ID, "children"),
    Output(STORE_COPILOT, "data"),
    Output(COPILOT_TIER_BADGE_ID, "children"),
    Output(COPILOT_INPUT_ID, "value"),
    Input(COPILOT_SEND_ID, "n_clicks"),
    State(COPILOT_INPUT_ID, "value"),
    State(STORE_COPILOT, "data"),
    State(STORE_ASSETS, "data"),
    prevent_initial_call=True,
)
def send_copilot_message(n_clicks: int, message: str, history: list, assets_state: dict):
    from services import copilot_service

    if not message or not message.strip():
        return _render_history(history), history, [], ""

    selected = (assets_state or {}).get("selected", [])
    ts = datetime.datetime.now().strftime("%H:%M")

    new_history = list(history or [])
    new_history.append({"role": "user", "text": message.strip(), "tier": None, "ts": ts})

    result = copilot_service.ask(message.strip(), selected_assets=selected)

    new_history.append({
        "role": "assistant",
        "text": result.body,
        "tier": result.tier,
        "ts": ts,
        "citations": result.citations,
        "orchestrated": result.orchestrated,
        "cost": result.cost_estimate,
    })

    tier_label = _TIER_LABELS.get(result.tier, result.tier)
    tier_color = _TIER_COLORS.get(result.tier, "secondary")
    tier_badge = [
        dbc.Badge(tier_label, color=tier_color, pill=True, className="me-1"),
        dbc.Badge(f"{result.latency_ms} ms", color="light", text_color="dark", pill=True),
    ]
    if result.orchestrated:
        tier_badge.append(
            dbc.Badge("multi-agente", color="danger", pill=True, className="ms-1")
        )
    if result.cost_estimate is not None:
        tier_badge.append(
            dbc.Badge(f"~${result.cost_estimate:.5f}", color="secondary", pill=True, className="ms-1")
        )

    return _render_history(new_history), new_history, tier_badge, ""


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _render_history(history: list) -> list:
    if not history:
        return []
    bubbles = []
    for entry in history:
        role = entry.get("role", "user")
        text = entry.get("text", "")
        tier = entry.get("tier")
        ts = entry.get("ts", "")
        if role == "user":
            bubbles.append(_user_bubble(text, ts))
        else:
            bubbles.append(_assistant_bubble(text, tier, ts, entry))
    return bubbles


def _user_bubble(text: str, ts: str) -> html.Div:
    return html.Div(
        [
            html.Div(
                text,
                style={
                    "backgroundColor": "#1D4ED8",
                    "color": "white",
                    "padding": "8px 12px",
                    "borderRadius": "12px 12px 0 12px",
                    "fontSize": "12px",
                    "maxWidth": "85%",
                    "marginLeft": "auto",
                    "wordBreak": "break-word",
                },
            ),
            html.Small(ts, style={"color": "#9CA3AF", "fontSize": "10px", "textAlign": "right", "display": "block"}),
        ],
        style={"marginBottom": "8px", "textAlign": "right"},
    )


def _assistant_bubble(text: str, tier: str | None, ts: str, entry: dict | None = None) -> html.Div:
    citations = (entry or {}).get("citations", [])
    cost = (entry or {}).get("cost")
    orchestrated = (entry or {}).get("orchestrated", False)

    children: list = [
        html.Div(
            text or "(sem resposta)",
            style={
                "backgroundColor": "white",
                "border": "1px solid #E5E7EB",
                "padding": "8px 12px",
                "borderRadius": "12px 12px 12px 0",
                "fontSize": "12px",
                "maxWidth": "85%",
                "wordBreak": "break-word",
            },
        ),
    ]

    meta = []
    if ts:
        meta.append(html.Small(ts, style={"color": "#9CA3AF"}))
    if tier:
        meta.append(dbc.Badge(tier, color=_TIER_COLORS.get(tier, "secondary"), pill=True, className="ms-1", style={"fontSize": "9px"}))
    if orchestrated:
        meta.append(dbc.Badge("multi-agente", color="danger", pill=True, className="ms-1", style={"fontSize": "9px"}))
    if cost is not None:
        meta.append(html.Small(f" ~${cost:.5f}", style={"color": "#9CA3AF", "fontSize": "10px"}))
    if citations:
        meta.append(
            dbc.Tooltip(
                html.Ul([html.Li(c, style={"fontSize": "11px"}) for c in citations]),
                target="cite-badge",
            )
        )
        meta.append(html.Small(" [fontes]", id="cite-badge", style={"color": "#6B7280", "cursor": "pointer", "fontSize": "10px"}))

    if meta:
        children.append(html.Div(meta, style={"marginTop": "3px"}))

    return html.Div(children, style={"marginBottom": "8px"})
