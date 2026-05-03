from __future__ import annotations

import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

_SEVERITY_COLOR = {"critical": "danger", "warning": "warning", "info": "info"}
_SEVERITY_ICON = {"critical": "🔴", "warning": "🟡", "info": "🔵"}

REFRESH_BTN_ID = "sentinela-refresh-btn"
READINESS_CARD_ID = "sentinela-readiness-card"
ALERT_COUNTS_ID = "sentinela-alert-counts"
ALERT_LIST_ID = "sentinela-alert-list"
FRESHNESS_TABLE_ID = "sentinela-freshness-table"
CHART_ALERT_TREND_ID = "sentinela-alert-trend"


def layout() -> html.Div:
    return html.Div(
        [
            _page_header(
                "◉ Sentinela — Observabilidade e Alertas",
                "Pipeline health, freshness, qualidade e prontidão operacional",
                btn_id=REFRESH_BTN_ID,
            ),
            dbc.Row(
                [
                    dbc.Col(_kpi_placeholder("Prontidão Operacional", READINESS_CARD_ID), width=3),
                    dbc.Col(_kpi_placeholder("Alertas (7 dias)", ALERT_COUNTS_ID), width=9),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("📋", "Alertas Recentes")),
                                dbc.CardBody(html.Div(id=ALERT_LIST_ID)),
                            ],
                            className="shadow-sm",
                        ),
                        width=7,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("🕐", "Freshness por Fonte")),
                                dbc.CardBody(html.Div(id=FRESHNESS_TABLE_ID)),
                            ],
                            className="shadow-sm",
                        ),
                        width=5,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Card(
                [
                    dbc.CardHeader(_card_header("📈", "Tendência de Alertas — últimos 7 dias")),
                    dbc.CardBody(dcc.Graph(id=CHART_ALERT_TREND_ID, config={"displayModeBar": False})),
                ],
                className="shadow-sm",
            ),
        ],
        style={"padding": "16px"},
    )


@callback(
    Output(READINESS_CARD_ID, "children"),
    Output(ALERT_COUNTS_ID, "children"),
    Output(ALERT_LIST_ID, "children"),
    Output(FRESHNESS_TABLE_ID, "children"),
    Output(CHART_ALERT_TREND_ID, "figure"),
    Input(REFRESH_BTN_ID, "n_clicks"),
    prevent_initial_call=False,
)
def refresh_sentinela(n_clicks):
    from services import ops_service, sentinela_service

    usage_rows = ops_service.fetch_usage_events(200)
    bundle_rows = ops_service.fetch_bundle_runs(50)
    alert_rows = ops_service.fetch_alerts(100)
    freshness_rows = ops_service.fetch_freshness_status()
    alert_counts = ops_service.fetch_alert_counts()

    # Readiness
    readiness = sentinela_service.evaluate_readiness(usage_rows, bundle_rows)
    ready = readiness.get("ready", False)
    score = readiness.get("score", 0)
    blockers = readiness.get("blockers", [])
    readiness_card = _readiness_kpi(ready, score, blockers)

    # Alert count badges
    counts_row = _alert_count_badges(alert_counts or alert_rows)

    # Alert list
    alert_list = _render_alert_list(alert_rows or _mock_alerts())

    # Freshness table
    freshness_block = _render_freshness(freshness_rows or _mock_freshness())

    # Alert trend chart
    trend_fig = _build_alert_trend(alert_rows or _mock_alerts())

    return readiness_card, counts_row, alert_list, freshness_block, trend_fig


# ---------------------------------------------------------------------------
# Sub-renderers
# ---------------------------------------------------------------------------

def _readiness_kpi(ready: bool, score: int | float, blockers: list) -> html.Div:
    color = "#16A34A" if ready else "#DC2626"
    label = "PRONTO" if ready else "BLOQUEADO"
    return html.Div(
        [
            html.Div(
                label,
                style={"fontSize": "22px", "fontWeight": "700", "color": color},
            ),
            html.Div(f"Score: {score}", style={"fontSize": "13px", "color": "#6B7280"}),
            html.Div(
                [dbc.Badge(b, color="danger", pill=True, className="me-1 mb-1") for b in blockers[:4]],
                style={"marginTop": "6px"},
            ) if blockers else html.Small("Sem bloqueadores", style={"color": "#16A34A"}),
        ]
    )


def _alert_count_badges(rows: list[dict]) -> html.Div:
    counts = {"critical": 0, "warning": 0, "info": 0}
    for r in rows:
        sev = str(r.get("severity") or r.get("kind") or "info").lower()
        if "critical" in sev or "error" in sev:
            counts["critical"] += r.get("count", 1)
        elif "warning" in sev or "latency" in sev or "cost" in sev:
            counts["warning"] += r.get("count", 1)
        else:
            counts["info"] += r.get("count", 1)

    return dbc.Row(
        [
            dbc.Col(_count_card("🔴 Críticos", counts["critical"], "danger"), width=4),
            dbc.Col(_count_card("🟡 Avisos", counts["warning"], "warning"), width=4),
            dbc.Col(_count_card("🔵 Info", counts["info"], "info"), width=4),
        ]
    )


def _count_card(label: str, count: int, color: str) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(str(count), style={"fontSize": "32px", "fontWeight": "700"}),
                html.Small(label, style={"color": "#6B7280"}),
            ],
            className="text-center p-2",
        ),
        color=color,
        outline=True,
        className="h-100",
    )


def _render_alert_list(rows: list[dict]) -> html.Div:
    if not rows:
        return html.Small("Nenhum alerta registrado.", style={"color": "#6B7280"})
    items = []
    for r in rows[:20]:
        sev = str(r.get("severity") or r.get("kind") or "info").lower()
        if "critical" in sev or "error" in sev:
            color = "danger"
            icon = "🔴"
        elif "warning" in sev or "latency" in sev or "cost" in sev:
            color = "warning"
            icon = "🟡"
        else:
            color = "info"
            icon = "🔵"
        items.append(
            dbc.ListGroupItem(
                [
                    html.Span(icon + " ", style={"marginRight": "4px"}),
                    html.Strong(r.get("kind") or r.get("severity") or "alert", style={"fontSize": "12px"}),
                    html.Span(
                        f" — {r.get('message', r.get('route_selected', ''))}",
                        style={"fontSize": "12px"},
                    ),
                    html.Small(
                        f"  {r.get('alert_time', r.get('event_time', ''))}",
                        style={"color": "#9CA3AF", "marginLeft": "8px"},
                    ),
                ],
                color=color,
                style={"padding": "6px 10px"},
            )
        )
    return dbc.ListGroup(items, flush=True, style={"fontSize": "12px"})


def _render_freshness(rows: list[dict]) -> html.Div:
    if not rows:
        return html.Small("Dados de freshness indisponíveis.", style={"color": "#6B7280"})
    return dbc.Table(
        [
            html.Thead(
                html.Tr([
                    html.Th("Fonte", style={"fontSize": "12px"}),
                    html.Th("Última ingestão", style={"fontSize": "12px"}),
                    html.Th("Registros", style={"fontSize": "12px"}),
                    html.Th("Status", style={"fontSize": "12px"}),
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(html.Strong(r.get("source_system", "?")), style={"fontSize": "12px"}),
                    html.Td(str(r.get("last_ingestion", "—"))[:19], style={"fontSize": "12px"}),
                    html.Td(f"{r.get('total_records', 0):,}", style={"fontSize": "12px"}),
                    html.Td(
                        dbc.Badge("fresh", color="success", pill=True)
                        if r.get("last_ingestion") else
                        dbc.Badge("stale", color="danger", pill=True)
                    ),
                ])
                for r in rows
            ]),
        ],
        bordered=False, striped=True, hover=True, size="sm", responsive=True,
    )


def _build_alert_trend(rows: list[dict]) -> go.Figure:
    if not rows:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados de alertas", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=200, margin={"t": 10, "b": 30, "l": 40, "r": 10}, paper_bgcolor="white", plot_bgcolor="white")
        return fig

    from collections import defaultdict
    daily: dict = defaultdict(lambda: {"critical": 0, "warning": 0, "info": 0})
    for r in rows:
        day = str(r.get("alert_time", r.get("event_time", "unknown")))[:10]
        sev = str(r.get("severity") or r.get("kind") or "info").lower()
        if "critical" in sev or "error" in sev:
            daily[day]["critical"] += 1
        elif "warning" in sev or "latency" in sev or "cost" in sev:
            daily[day]["warning"] += 1
        else:
            daily[day]["info"] += 1

    days = sorted(daily.keys())
    fig = go.Figure()
    fig.add_trace(go.Bar(x=days, y=[daily[d]["critical"] for d in days], name="Crítico", marker_color="#DC2626"))
    fig.add_trace(go.Bar(x=days, y=[daily[d]["warning"] for d in days], name="Aviso", marker_color="#D97706"))
    fig.add_trace(go.Bar(x=days, y=[daily[d]["info"] for d in days], name="Info", marker_color="#2563EB"))
    fig.update_layout(
        barmode="stack", height=200, margin={"t": 10, "b": 30, "l": 40, "r": 10},
        paper_bgcolor="white", plot_bgcolor="white", font={"size": 11},
        legend={"font": {"size": 9}},
    )
    return fig


# ---------------------------------------------------------------------------
# Mock fallback
# ---------------------------------------------------------------------------

def _mock_alerts() -> list[dict]:
    return [
        {"kind": "latency_breach", "severity": "warning", "route_selected": "copilot", "message": "latency > 1200ms", "alert_time": "2026-05-02 14:22"},
        {"kind": "cost_breach", "severity": "critical", "route_selected": "complex", "message": "cost > $0.05", "alert_time": "2026-05-02 13:10"},
        {"kind": "freshness_lag", "severity": "info", "route_selected": "dashboard_api", "message": "coingecko lag > 5min", "alert_time": "2026-05-02 12:00"},
    ]


def _mock_freshness() -> list[dict]:
    return [
        {"source_system": "coingecko", "last_ingestion": "2026-05-02 14:00:00", "total_records": 15420},
        {"source_system": "defillama", "last_ingestion": "2026-05-02 13:30:00", "total_records": 8740},
        {"source_system": "github", "last_ingestion": "2026-05-02 10:00:00", "total_records": 240},
        {"source_system": "fred", "last_ingestion": "2026-05-01 08:00:00", "total_records": 1280},
    ]
