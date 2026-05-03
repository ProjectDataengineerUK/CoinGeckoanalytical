from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from state.app_state import STORE_ASSETS, STORE_GENIE

# ---------------------------------------------------------------------------
# Component IDs
# ---------------------------------------------------------------------------

CHART_RANKINGS_ID = "chart-rankings"
CHART_MOVERS_ID = "chart-movers"
CHART_DEFI_ID = "chart-defi"
CHART_MACRO_ID = "chart-macro"
CHART_ACTIVE_BADGE_ID = "chart-active-badge"
CHART_GENIE_RESULT_ID = "chart-genie-result"


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def layout() -> html.Div:
    return html.Div(
        [
            # Active query badge
            html.Div(id=CHART_ACTIVE_BADGE_ID, style={"marginBottom": "8px"}),

            # Genie custom result table (shown when SQL returns non-chart data)
            html.Div(id=CHART_GENIE_RESULT_ID, style={"marginBottom": "12px"}),

            # 2x2 chart grid
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_section_header("📊", "Market Rankings", "#1D4ED8")),
                                dbc.CardBody(dcc.Graph(id=CHART_RANKINGS_ID, config={"displayModeBar": False})),
                            ],
                            className="h-100 shadow-sm",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_section_header("🔥", "Top Movers 24h", "#DC2626")),
                                dbc.CardBody(dcc.Graph(id=CHART_MOVERS_ID, config={"displayModeBar": False})),
                            ],
                            className="h-100 shadow-sm",
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
                style={"height": "320px"},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_section_header("🏦", "DeFi — TVL por Protocolo", "#059669")),
                                dbc.CardBody(dcc.Graph(id=CHART_DEFI_ID, config={"displayModeBar": False})),
                            ],
                            className="h-100 shadow-sm",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_section_header("🌍", "Regime Macro (FRED)", "#7C3AED")),
                                dbc.CardBody(dcc.Graph(id=CHART_MACRO_ID, config={"displayModeBar": False})),
                            ],
                            className="h-100 shadow-sm",
                        ),
                        width=6,
                    ),
                ],
                style={"height": "320px"},
            ),
        ],
        style={"padding": "12px", "height": "100%", "overflowY": "auto"},
    )


# ---------------------------------------------------------------------------
# Callback — all charts react to STORE_GENIE updates
# ---------------------------------------------------------------------------

@callback(
    Output(CHART_RANKINGS_ID, "figure"),
    Output(CHART_MOVERS_ID, "figure"),
    Output(CHART_DEFI_ID, "figure"),
    Output(CHART_MACRO_ID, "figure"),
    Output(CHART_ACTIVE_BADGE_ID, "children"),
    Output(CHART_GENIE_RESULT_ID, "children"),
    Input(STORE_GENIE, "data"),
    Input(STORE_ASSETS, "data"),
)
def update_charts(genie_state: dict, assets_state: dict):
    from services import sql_service

    active_sql = (genie_state or {}).get("sql")
    genie_status = (genie_state or {}).get("status", "idle")
    selected_assets = (assets_state or {}).get("selected", [])

    # Active query badge
    if active_sql and genie_status == "completed":
        badge = dbc.Alert(
            [
                dbc.Badge("Genie ativo", color="success", pill=True, className="me-2"),
                html.Small("Gráficos filtrados pela consulta do Genie", style={"color": "#374151"}),
            ],
            color="light",
            style={"padding": "6px 12px", "fontSize": "12px"},
        )
    else:
        badge = dbc.Alert(
            [
                dbc.Badge("Visualização padrão", color="secondary", pill=True, className="me-2"),
                html.Small("Use o Genie para filtrar os gráficos", style={"color": "#6B7280"}),
            ],
            color="light",
            style={"padding": "6px 12px", "fontSize": "12px"},
        )

    # Genie custom result — if the SQL returns generic data, show as table
    genie_result_block = []
    if active_sql and genie_status == "completed":
        genie_rows = sql_service.run_query(active_sql)
        if genie_rows:
            genie_result_block = _build_result_table(genie_rows, label="Resultado Genie")

    # Default data sources (or fall back to mocks when no live connection)
    rankings = sql_service.fetch_market_rankings(12) or _mock_rankings()
    movers = sql_service.fetch_top_movers(10) or _mock_movers()
    defi = sql_service.fetch_defi_protocols(10) or _mock_defi()
    macro = sql_service.fetch_macro_regime(8) or _mock_macro()

    # If Genie returned data compatible with rankings schema, override
    if active_sql and genie_status == "completed":
        genie_rows = sql_service.run_query(active_sql)
        if genie_rows and "market_cap_usd" in genie_rows[0]:
            rankings = genie_rows
        elif genie_rows and "tvl_usd" in genie_rows[0]:
            defi = genie_rows
        elif genie_rows and "price_change_pct_24h" in genie_rows[0]:
            movers = genie_rows

    return (
        _build_rankings_chart(rankings),
        _build_movers_chart(movers),
        _build_defi_chart(defi),
        _build_macro_chart(macro),
        badge,
        genie_result_block,
    )


# ---------------------------------------------------------------------------
# Chart builders
# ---------------------------------------------------------------------------

def _build_rankings_chart(rows: list[dict]) -> go.Figure:
    if not rows:
        return _empty_fig("Sem dados de rankings")
    symbols = [r.get("symbol", r.get("asset_id", "?")) for r in rows]
    caps = [r.get("market_cap_usd", 0) for r in rows]
    changes = [r.get("price_change_pct_24h", 0) for r in rows]
    colors = ["#16A34A" if c and c >= 0 else "#DC2626" for c in changes]
    fig = go.Figure(
        go.Bar(
            x=symbols,
            y=[c / 1e9 for c in caps],
            marker_color=colors,
            hovertemplate="%{x}<br>Market Cap: $%{y:.1f}B<extra></extra>",
        )
    )
    fig.update_layout(**_base_layout("Market Cap (USD bilhões)"))
    return fig


def _build_movers_chart(rows: list[dict]) -> go.Figure:
    if not rows:
        return _empty_fig("Sem dados de movers")
    symbols = [r.get("symbol", r.get("asset_id", "?")) for r in rows]
    changes = [r.get("price_change_pct_24h", 0) for r in rows]
    colors = ["#16A34A" if c and c >= 0 else "#DC2626" for c in changes]
    fig = go.Figure(
        go.Bar(
            x=symbols,
            y=changes,
            marker_color=colors,
            hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>",
        )
    )
    fig.update_layout(**_base_layout("Variação 24h (%)"))
    fig.add_hline(y=0, line_dash="dash", line_color="#9CA3AF", line_width=1)
    return fig


def _build_defi_chart(rows: list[dict]) -> go.Figure:
    if not rows:
        return _empty_fig("Sem dados DeFi")
    labels = [r.get("protocol_name", "?") for r in rows]
    values = [r.get("tvl_usd", 0) for r in rows]
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            hovertemplate="%{label}<br>TVL: $%{value:,.0f}<extra></extra>",
            textinfo="label+percent",
            textfont_size=10,
        )
    )
    fig.update_layout(**_base_layout(None))
    return fig


def _build_macro_chart(rows: list[dict]) -> go.Figure:
    if not rows:
        return _empty_fig("Sem dados macro")
    series = {}
    for r in rows:
        name = r.get("series_name", "unknown")
        series.setdefault(name, {"dates": [], "values": []})
        series[name]["dates"].append(r.get("observation_date", ""))
        series[name]["values"].append(r.get("value", 0))
    fig = go.Figure()
    colors_cycle = ["#1D4ED8", "#DC2626", "#059669", "#7C3AED", "#D97706"]
    for i, (name, data) in enumerate(series.items()):
        fig.add_trace(
            go.Scatter(
                x=data["dates"],
                y=data["values"],
                mode="lines+markers",
                name=name,
                line={"color": colors_cycle[i % len(colors_cycle)], "width": 2},
                marker={"size": 5},
            )
        )
    fig.update_layout(**_base_layout("Valor"))
    return fig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _section_header(icon: str, title: str, color: str) -> html.Div:
    return html.Div(
        [html.Span(icon, style={"marginRight": "6px"}), html.Strong(title)],
        style={"color": color, "fontSize": "13px"},
    )


def _base_layout(y_label: str | None) -> dict:
    layout = {
        "margin": {"t": 10, "b": 30, "l": 40, "r": 10},
        "height": 220,
        "plot_bgcolor": "white",
        "paper_bgcolor": "white",
        "font": {"size": 11},
        "showlegend": True,
        "legend": {"font": {"size": 9}},
    }
    if y_label:
        layout["yaxis"] = {"title": y_label, "titlefont": {"size": 10}}
    return layout


def _empty_fig(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    fig.update_layout(**_base_layout(None))
    return fig


def _build_result_table(rows: list[dict], label: str) -> list:
    if not rows:
        return []
    headers = list(rows[0].keys())
    return [
        html.Div(
            [
                html.Small(label, style={"fontWeight": "600", "color": "#374151"}),
                dbc.Table(
                    [
                        html.Thead(html.Tr([html.Th(h, style={"fontSize": "11px"}) for h in headers])),
                        html.Tbody([
                            html.Tr([
                                html.Td(
                                    str(row.get(h, ""))[:40],
                                    style={"fontSize": "11px"},
                                )
                                for h in headers
                            ])
                            for row in rows[:8]
                        ]),
                    ],
                    bordered=True,
                    striped=True,
                    hover=True,
                    size="sm",
                    responsive=True,
                    style={"marginTop": "4px"},
                ),
            ]
        )
    ]


# ---------------------------------------------------------------------------
# Mock data (fallback when Databricks is unreachable)
# ---------------------------------------------------------------------------

def _mock_rankings() -> list[dict]:
    assets = [
        ("BTC", "Bitcoin", 1_300_000_000_000, 2.1),
        ("ETH", "Ethereum", 450_000_000_000, -0.8),
        ("BNB", "BNB", 85_000_000_000, 1.2),
        ("SOL", "Solana", 70_000_000_000, 4.5),
        ("XRP", "XRP", 60_000_000_000, -1.1),
        ("USDC", "USDC", 55_000_000_000, 0.0),
        ("ADA", "Cardano", 22_000_000_000, 0.7),
        ("AVAX", "Avalanche", 18_000_000_000, 3.2),
    ]
    return [
        {"symbol": s, "name": n, "market_cap_usd": c, "price_change_pct_24h": p}
        for s, n, c, p in assets
    ]


def _mock_movers() -> list[dict]:
    return [
        {"symbol": "SOL", "price_change_pct_24h": 4.5},
        {"symbol": "AVAX", "price_change_pct_24h": 3.2},
        {"symbol": "BTC", "price_change_pct_24h": 2.1},
        {"symbol": "ADA", "price_change_pct_24h": 0.7},
        {"symbol": "USDC", "price_change_pct_24h": 0.0},
        {"symbol": "ETH", "price_change_pct_24h": -0.8},
        {"symbol": "XRP", "price_change_pct_24h": -1.1},
        {"symbol": "DOGE", "price_change_pct_24h": -2.3},
    ]


def _mock_defi() -> list[dict]:
    return [
        {"protocol_name": "Uniswap", "tvl_usd": 5_200_000_000},
        {"protocol_name": "Aave", "tvl_usd": 12_000_000_000},
        {"protocol_name": "Lido", "tvl_usd": 28_000_000_000},
        {"protocol_name": "Curve", "tvl_usd": 3_800_000_000},
        {"protocol_name": "MakerDAO", "tvl_usd": 8_500_000_000},
        {"protocol_name": "Compound", "tvl_usd": 2_100_000_000},
    ]


def _mock_macro() -> list[dict]:
    return [
        {"series_name": "Fed Funds Rate", "observation_date": "2026-03-01", "value": 4.25},
        {"series_name": "Fed Funds Rate", "observation_date": "2026-04-01", "value": 4.00},
        {"series_name": "CPI YoY", "observation_date": "2026-03-01", "value": 2.8},
        {"series_name": "CPI YoY", "observation_date": "2026-04-01", "value": 2.6},
        {"series_name": "M2 Growth", "observation_date": "2026-03-01", "value": 3.2},
        {"series_name": "M2 Growth", "observation_date": "2026-04-01", "value": 3.5},
    ]
