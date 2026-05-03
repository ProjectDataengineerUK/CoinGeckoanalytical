from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html


def _page_header(title: str, subtitle: str, btn_id: str) -> html.Div:
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H5(title, style={"fontWeight": "700", "marginBottom": "2px"}),
                            html.Small(subtitle, style={"color": "#6B7280"}),
                        ],
                        width=10,
                    ),
                    dbc.Col(
                        dbc.Button("↺ Atualizar", id=btn_id, color="secondary", outline=True, size="sm"),
                        width=2,
                        className="text-end",
                    ),
                ],
                align="center",
            ),
            html.Hr(style={"marginTop": "8px", "marginBottom": "12px"}),
        ]
    )


def _card_header(icon: str, title: str) -> html.Div:
    return html.Div([html.Span(icon + " "), html.Strong(title, style={"fontSize": "13px"})])


def _kpi_placeholder(label: str, component_id: str) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(label, style={"fontSize": "12px", "fontWeight": "600", "color": "#6B7280", "marginBottom": "6px"}),
                html.Div(id=component_id),
            ],
            className="p-3",
        ),
        className="shadow-sm h-100",
    )
