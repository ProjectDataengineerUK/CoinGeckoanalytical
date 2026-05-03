from __future__ import annotations

import json

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

from state.app_state import STORE_GENIE

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

GENIE_PANEL_ID = "genie-panel"
GENIE_INPUT_ID = "genie-input"
GENIE_SEND_ID = "genie-send"
GENIE_ANSWER_ID = "genie-answer"
GENIE_SQL_BADGE_ID = "genie-sql-badge"
GENIE_STATUS_ID = "genie-status"


def layout() -> html.Div:
    return html.Div(
        id=GENIE_PANEL_ID,
        children=[
            html.Div(
                [
                    html.Span("◈", style={"fontSize": "18px", "color": "#7C3AED"}),
                    html.Span(
                        " Genie — Análise Conversacional",
                        style={"fontWeight": "700", "fontSize": "14px", "marginLeft": "6px"},
                    ),
                ],
                style={"marginBottom": "10px"},
            ),
            dbc.Textarea(
                id=GENIE_INPUT_ID,
                placeholder="Pergunte ao Genie: 'Top 5 assets por market cap' ou 'Protocolos DeFi com TVL acima de $1B'...",
                rows=3,
                style={"fontSize": "13px", "resize": "vertical"},
            ),
            dbc.Button(
                "Consultar Genie",
                id=GENIE_SEND_ID,
                color="primary",
                size="sm",
                className="mt-2 w-100",
                style={"backgroundColor": "#7C3AED", "border": "none"},
            ),
            html.Div(id=GENIE_STATUS_ID, className="mt-2"),
            html.Div(
                id=GENIE_ANSWER_ID,
                style={
                    "marginTop": "12px",
                    "padding": "10px",
                    "backgroundColor": "#F3F0FF",
                    "borderRadius": "6px",
                    "fontSize": "13px",
                    "minHeight": "60px",
                    "display": "none",
                },
            ),
            html.Div(
                id=GENIE_SQL_BADGE_ID,
                style={"marginTop": "8px", "display": "none"},
            ),
            html.Hr(style={"marginTop": "16px"}),
            html.Div(
                "Os gráficos atualizam automaticamente com o resultado da consulta.",
                style={"fontSize": "11px", "color": "#6B7280", "textAlign": "center"},
            ),
        ],
        style={
            "padding": "16px",
            "backgroundColor": "#FAFAFA",
            "borderRight": "1px solid #E5E7EB",
            "height": "100%",
            "overflowY": "auto",
        },
    )


# ---------------------------------------------------------------------------
# Callback — sends question to Genie, stores result in STORE_GENIE
# ---------------------------------------------------------------------------

@callback(
    Output(STORE_GENIE, "data"),
    Output(GENIE_ANSWER_ID, "children"),
    Output(GENIE_ANSWER_ID, "style"),
    Output(GENIE_SQL_BADGE_ID, "children"),
    Output(GENIE_SQL_BADGE_ID, "style"),
    Output(GENIE_STATUS_ID, "children"),
    Input(GENIE_SEND_ID, "n_clicks"),
    State(GENIE_INPUT_ID, "value"),
    State(STORE_GENIE, "data"),
    prevent_initial_call=True,
)
def send_genie_question(n_clicks: int, question: str, current_state: dict):
    from services import genie_service, sql_service

    if not question or not question.strip():
        return (
            current_state,
            "", _hidden_style(),
            "", _hidden_style(),
            dbc.Alert("Digite uma pergunta.", color="warning", dismissable=True),
        )

    result = genie_service.ask(question.strip())

    new_state = {
        "sql": result.generated_query,
        "answer_text": result.answer_text,
        "latency_ms": result.latency_ms,
        "status": result.execution_status,
    }

    # Answer text block
    answer_block = [
        html.Strong("Genie: "),
        html.Span(result.answer_text or "Sem resposta disponível."),
        html.Br(),
        html.Small(
            f"⏱ {result.latency_ms} ms",
            style={"color": "#6B7280"},
        ),
    ]
    answer_style = {**_visible_style(), "backgroundColor": "#F3F0FF", "borderLeft": "3px solid #7C3AED"}

    # SQL badge
    if result.generated_query:
        sql_badge = [
            html.Div(
                [
                    html.Small("SQL gerado pelo Genie:", style={"color": "#374151", "fontWeight": "600"}),
                    html.Pre(
                        result.generated_query,
                        style={
                            "fontSize": "11px",
                            "backgroundColor": "#1E1E2E",
                            "color": "#CDD6F4",
                            "padding": "8px",
                            "borderRadius": "4px",
                            "marginTop": "4px",
                            "overflowX": "auto",
                            "whiteSpace": "pre-wrap",
                        },
                    ),
                    dbc.Badge("→ Gráficos atualizados", color="success", pill=True, className="mt-1"),
                ]
            )
        ]
        sql_style = _visible_style()
    else:
        sql_badge = []
        sql_style = _hidden_style()

    status_color = "success" if result.execution_status == "completed" else "warning"
    status_msg = dbc.Alert(
        f"Status: {result.execution_status}", color=status_color, dismissable=True, style={"fontSize": "12px"}
    )

    return new_state, answer_block, answer_style, sql_badge, sql_style, status_msg


def _hidden_style() -> dict:
    return {"display": "none"}


def _visible_style() -> dict:
    return {
        "display": "block",
        "marginTop": "8px",
        "padding": "10px",
        "borderRadius": "6px",
        "fontSize": "13px",
    }
