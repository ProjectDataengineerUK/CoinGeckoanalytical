from __future__ import annotations

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

REFRESH_BTN_ID = "audit-refresh-btn"
AUDIT_TABLE_ID = "audit-table"
CHART_LATENCY_ID = "audit-latency-chart"
CHART_STATUS_ID = "audit-status-chart"


def layout() -> html.Div:
    return html.Div(
        [
            _page_header(
                "🔍 Audit Trail — Rastreabilidade de Requests",
                "Histórico completo de consultas, modelos, latência e proveniência",
                btn_id=REFRESH_BTN_ID,
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("⏱", "Latência por Tier (ms)")),
                                dbc.CardBody(dcc.Graph(id=CHART_LATENCY_ID, config={"displayModeBar": False})),
                            ],
                            className="shadow-sm",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("✅", "Status das Respostas")),
                                dbc.CardBody(dcc.Graph(id=CHART_STATUS_ID, config={"displayModeBar": False})),
                            ],
                            className="shadow-sm",
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Card(
                [
                    dbc.CardHeader(_card_header("📋", "Log de Requests (últimos 100)")),
                    dbc.CardBody(html.Div(id=AUDIT_TABLE_ID)),
                ],
                className="shadow-sm",
            ),
        ],
        style={"padding": "16px"},
    )


@callback(
    Output(AUDIT_TABLE_ID, "children"),
    Output(CHART_LATENCY_ID, "figure"),
    Output(CHART_STATUS_ID, "figure"),
    Input(REFRESH_BTN_ID, "n_clicks"),
    prevent_initial_call=False,
)
def refresh_audit(n_clicks):
    from services import ops_service

    rows = ops_service.fetch_audit_trail(100) or _mock_audit()

    return (
        _render_audit_table(rows),
        _build_latency_chart(rows),
        _build_status_chart(rows),
    )


def _render_audit_table(rows: list[dict]) -> html.Div:
    if not rows:
        return html.Small("Nenhum registro de audit encontrado.", style={"color": "#6B7280"})

    _tier_color = {"light": "success", "standard": "primary", "complex": "danger"}

    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Timestamp", style={"fontSize": "11px"}),
                html.Th("Request ID", style={"fontSize": "11px"}),
                html.Th("Tenant", style={"fontSize": "11px"}),
                html.Th("Rota", style={"fontSize": "11px"}),
                html.Th("Tier", style={"fontSize": "11px"}),
                html.Th("Tokens", style={"fontSize": "11px"}),
                html.Th("Latência", style={"fontSize": "11px"}),
                html.Th("Custo", style={"fontSize": "11px"}),
                html.Th("Status", style={"fontSize": "11px"}),
                html.Th("Freshness", style={"fontSize": "11px"}),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(str(r.get("event_time", ""))[:16], style={"fontSize": "10px"}),
                    html.Td(
                        html.Code(str(r.get("request_id", ""))[:8] + "…", style={"fontSize": "10px"}),
                    ),
                    html.Td(r.get("tenant_id", "?"), style={"fontSize": "10px"}),
                    html.Td(
                        dbc.Badge(r.get("route_selected", "?"), color="secondary", pill=True, style={"fontSize": "9px"})
                    ),
                    html.Td(
                        dbc.Badge(
                            r.get("model_tier", "?"),
                            color=_tier_color.get(r.get("model_tier", ""), "secondary"),
                            pill=True, style={"fontSize": "9px"},
                        )
                    ),
                    html.Td(f"{r.get('total_tokens', 0):,}", style={"fontSize": "10px"}),
                    html.Td(f"{r.get('latency_ms', 0)} ms", style={"fontSize": "10px"}),
                    html.Td(
                        f"${r.get('cost_estimate', 0):.5f}" if r.get("cost_estimate") else "—",
                        style={"fontSize": "10px"},
                    ),
                    html.Td(
                        dbc.Badge(
                            r.get("response_status", "?"),
                            color="success" if r.get("response_status") == "success" else "danger",
                            pill=True, style={"fontSize": "9px"},
                        )
                    ),
                    html.Td(
                        html.Small(str(r.get("freshness_watermark", "—")), style={"fontSize": "10px", "color": "#6B7280"})
                    ),
                ])
                for r in rows
            ]),
        ],
        bordered=False, striped=True, hover=True, size="sm", responsive=True,
        style={"fontSize": "11px"},
    )


def _build_latency_chart(rows: list[dict]) -> go.Figure:
    if not rows:
        return _empty_fig("Sem dados de latência")

    tiers = ["light", "standard", "complex"]
    tier_latencies: dict = {t: [] for t in tiers}
    for r in rows:
        t = r.get("model_tier", "standard")
        lat = r.get("latency_ms")
        if t in tier_latencies and lat is not None:
            tier_latencies[t].append(lat)

    _color = {"light": "#10B981", "standard": "#3B82F6", "complex": "#EF4444"}
    fig = go.Figure()
    for tier in tiers:
        if tier_latencies[tier]:
            fig.add_trace(go.Box(
                y=tier_latencies[tier],
                name=tier,
                marker_color=_color[tier],
                boxpoints="outliers",
            ))
    fig.update_layout(**_base_layout(230))
    return fig


def _build_status_chart(rows: list[dict]) -> go.Figure:
    if not rows:
        return _empty_fig("Sem dados de status")

    counts: dict = {}
    for r in rows:
        status = r.get("response_status", "unknown")
        counts[status] = counts.get(status, 0) + 1

    colors = {"success": "#16A34A", "error": "#DC2626", "failed": "#DC2626", "unknown": "#9CA3AF"}
    fig = go.Figure(go.Pie(
        labels=list(counts.keys()),
        values=list(counts.values()),
        hole=0.4,
        marker={"colors": [colors.get(k, "#6B7280") for k in counts]},
        textinfo="label+percent",
        textfont_size=11,
    ))
    fig.update_layout(**_base_layout(230))
    return fig


def _empty_fig(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    fig.update_layout(**_base_layout(230))
    return fig


def _base_layout(height: int) -> dict:
    return {
        "height": height,
        "margin": {"t": 10, "b": 30, "l": 50, "r": 10},
        "paper_bgcolor": "white",
        "plot_bgcolor": "white",
        "font": {"size": 11},
        "legend": {"font": {"size": 9}},
    }


def _mock_audit() -> list[dict]:
    import uuid
    rows = []
    tiers = ["light", "light", "standard", "standard", "standard", "complex"]
    routes = ["copilot", "copilot", "genie", "dashboard_api", "copilot", "copilot"]
    import random
    random.seed(7)
    for i in range(20):
        tier = tiers[i % len(tiers)]
        route = routes[i % len(routes)]
        latency = {"light": 180, "standard": 540, "complex": 2400}[tier] + random.randint(-50, 200)
        cost = {"light": 0.0008, "standard": 0.004, "complex": 0.025}[tier] * random.uniform(0.5, 2.0)
        rows.append({
            "event_time": f"2026-05-02 {12 + i // 4:02d}:{(i * 3) % 60:02d}",
            "request_id": str(uuid.uuid4()),
            "tenant_id": ["default", "tenant_alpha", "tenant_beta"][i % 3],
            "route_selected": route,
            "model_tier": tier,
            "total_tokens": random.randint(100, 1500),
            "latency_ms": latency,
            "cost_estimate": round(cost, 6),
            "response_status": "success" if random.random() > 0.1 else "error",
            "freshness_watermark": "live" if route != "dashboard_api" else "5min",
        })
    return rows
