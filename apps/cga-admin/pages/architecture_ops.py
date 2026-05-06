from __future__ import annotations

from collections import defaultdict

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from . import _card_header, _page_header

REFRESH_BTN_ID = "architecture-refresh-btn"
KPI_ROW_ID = "architecture-kpi-row"
RESOURCE_BOARD_ID = "architecture-resource-board"
RESOURCE_TABLE_ID = "architecture-resource-table"
OPTIMIZATION_ID = "architecture-optimization-list"
CHART_ROUTE_COST_ID = "architecture-route-cost-chart"

_STATUS_COLOR = {"healthy": "success", "warning": "warning", "critical": "danger"}
_STATUS_LABEL = {"healthy": "verde", "warning": "amarelo", "critical": "vermelho"}
_LAYER_ORDER = [
    "Fontes Externas",
    "Databricks Data Plane",
    "AI & Analytics",
    "Apps & Operações",
]


def layout() -> html.Div:
    return html.Div(
        [
            _page_header(
                "🗺️ Arquitetura & Infra Databricks",
                "Desenho operacional com status dinâmico, custo estimado e oportunidades de otimização",
                btn_id=REFRESH_BTN_ID,
            ),
            html.Div(id=KPI_ROW_ID, className="mb-3"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("🏗️", "Mapa de Arquitetura Operacional")),
                                dbc.CardBody(html.Div(id=RESOURCE_BOARD_ID)),
                            ],
                            className="shadow-sm h-100",
                        ),
                        width=8,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("💡", "Oportunidades de Otimização")),
                                dbc.CardBody(html.Div(id=OPTIMIZATION_ID)),
                            ],
                            className="shadow-sm h-100",
                        ),
                        width=4,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("📊", "Custo Estimado por Rota")),
                                dbc.CardBody(dcc.Graph(id=CHART_ROUTE_COST_ID, config={"displayModeBar": False})),
                            ],
                            className="shadow-sm",
                        ),
                        width=5,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("📋", "Recursos e Estado Atual")),
                                dbc.CardBody(html.Div(id=RESOURCE_TABLE_ID)),
                            ],
                            className="shadow-sm",
                        ),
                        width=7,
                    ),
                ]
            ),
        ],
        style={"padding": "16px"},
    )


@callback(
    Output(KPI_ROW_ID, "children"),
    Output(RESOURCE_BOARD_ID, "children"),
    Output(OPTIMIZATION_ID, "children"),
    Output(CHART_ROUTE_COST_ID, "figure"),
    Output(RESOURCE_TABLE_ID, "children"),
    Input(REFRESH_BTN_ID, "n_clicks"),
    prevent_initial_call=False,
)
def refresh_architecture(n_clicks):
    from services import ops_service

    ready_overview = (ops_service.fetch_ready_overview() or _mock_ready_overview())[0]
    route_rows = ops_service.fetch_route_readiness_latest() or _mock_route_readiness()
    bundle_rows = ops_service.fetch_bundle_run_status() or _mock_bundle_status()
    sentinela_rows = ops_service.fetch_sentinela_alert_status() or _mock_sentinela_status()
    backlog_rows = ops_service.fetch_alert_backlog() or _mock_alert_backlog()
    cost_rows = ops_service.fetch_cost_by_tier() or _mock_tier_cost()
    trend_rows = ops_service.fetch_cost_latency_trend(72) or _mock_cost_latency_trend()

    resources = _derive_resource_health(ready_overview, route_rows, bundle_rows, sentinela_rows, backlog_rows)
    opportunities = _derive_optimization_opportunities(route_rows, bundle_rows, trend_rows, sentinela_rows)

    return (
        _build_kpi_row(ready_overview, resources, cost_rows),
        _render_resource_board(resources),
        _render_optimization_list(opportunities),
        _build_route_cost_chart(route_rows),
        _render_resource_table(resources),
    )


def _build_kpi_row(overview: dict, resources: list[dict], cost_rows: list[dict]) -> dbc.Row:
    healthy = sum(1 for r in resources if r["status"] == "healthy")
    warning = sum(1 for r in resources if r["status"] == "warning")
    critical = sum(1 for r in resources if r["status"] == "critical")
    ai_cost = sum((row.get("total_cost_usd", 0) or 0) for row in cost_rows)
    route_cost = float(overview.get("total_cost_estimate", 0) or 0)
    total_cost = ai_cost + route_cost
    return dbc.Row(
        [
            dbc.Col(_kpi_card("💵 Custo Estimado", f"${total_cost:.4f}", "telemetria + readiness"), width=3),
            dbc.Col(_kpi_card("🟢 Recursos OK", str(healthy), "saudáveis"), width=3),
            dbc.Col(_kpi_card("🟡 Atenção", str(warning), "precisam ajuste"), width=3),
            dbc.Col(_kpi_card("🔴 Críticos", str(critical), "impactando operação"), width=3),
        ]
    )


def _kpi_card(label: str, value: str, sub: str) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(value, style={"fontSize": "24px", "fontWeight": "700"}),
                html.Div(label, style={"fontSize": "12px", "fontWeight": "600", "color": "#374151"}),
                html.Small(sub, style={"color": "#9CA3AF"}),
            ],
            className="p-3",
        ),
        className="shadow-sm h-100",
    )


def _derive_resource_health(
    overview: dict,
    route_rows: list[dict],
    bundle_rows: list[dict],
    sentinela_rows: list[dict],
    backlog_rows: list[dict],
) -> list[dict]:
    routes = {row.get("route_selected", ""): row for row in route_rows}
    bundle = {row.get("job_name", ""): row for row in bundle_rows}
    sentinela = sentinela_rows[0] if sentinela_rows else {}
    backlog = defaultdict(int)
    for row in backlog_rows:
        backlog[row.get("route_selected", "global")] += int(row.get("alert_count", 0) or 0)

    return [
        _resource_row(
            "Fontes Externas",
            "CoinGecko Ingestion",
            _job_status(bundle, "market_source_ingestion_job"),
            "Ingestão principal de mercado",
            _job_metric(bundle, "market_source_ingestion_job"),
        ),
        _resource_row(
            "Fontes Externas",
            "DefiLlama Ingestion",
            _job_status(bundle, "defillama_ingestion_job"),
            "TVL, fees e revenue DeFi",
            _job_metric(bundle, "defillama_ingestion_job"),
        ),
        _resource_row(
            "Databricks Data Plane",
            "Gold Serving Readiness",
            "healthy" if int(overview.get("stale_freshness_count", 0) or 0) == 0 else "warning",
            "Freshness e serving do Gold",
            f"stale={int(overview.get('stale_freshness_count', 0) or 0)}",
        ),
        _resource_row(
            "Databricks Data Plane",
            "Bundle Jobs",
            "healthy" if all((row.get("bundle_readiness_status") == "ready") for row in bundle_rows[:6]) else "warning",
            "Jobs do bundle e deploy contínuo",
            f"jobs={len(bundle_rows)}",
        ),
        _resource_row(
            "AI & Analytics",
            "Genie",
            _route_status(routes.get("genie")),
            "NLQ governado e SQL gerado",
            _route_metric(routes.get("genie"), backlog.get("genie", 0)),
        ),
        _resource_row(
            "AI & Analytics",
            "Copilot",
            _route_status(routes.get("copilot")),
            "Narrativa AI e multiagente",
            _route_metric(routes.get("copilot"), backlog.get("copilot", 0)),
        ),
        _resource_row(
            "AI & Analytics",
            "Dashboard API",
            _route_status(routes.get("dashboard_api")),
            "Payloads governados para o dashboard",
            _route_metric(routes.get("dashboard_api"), backlog.get("dashboard_api", 0)),
        ),
        _resource_row(
            "Apps & Operações",
            "cga-admin",
            _route_status(routes.get("internal_app")),
            "Superfície operacional interna",
            _route_metric(routes.get("internal_app"), backlog.get("internal_app", 0)),
        ),
        _resource_row(
            "Apps & Operações",
            "Sentinela",
            "healthy" if sentinela.get("sentinela_alert_status") == "ready" else "critical",
            "Alertas, runtime e backlog operacional",
            f"runtime={int(sentinela.get('runtime_alerts', 0) or 0)} bundle={int(sentinela.get('bundle_alerts', 0) or 0)}",
        ),
    ]


def _resource_row(layer: str, resource: str, status: str, detail: str, metric: str) -> dict:
    return {"layer": layer, "resource": resource, "status": status, "detail": detail, "metric": metric}


def _job_status(rows: dict[str, dict], job_name: str) -> str:
    row = rows.get(job_name)
    if not row:
        return "warning"
    if (row.get("failed_count", 0) or 0) > 0 or row.get("bundle_readiness_status") != "ready":
        return "critical"
    if (row.get("running_count", 0) or 0) > 0:
        return "warning"
    return "healthy"


def _job_metric(rows: dict[str, dict], job_name: str) -> str:
    row = rows.get(job_name) or {}
    return f"ok={int(row.get('success_count', 0) or 0)} fail={int(row.get('failed_count', 0) or 0)}"


def _route_status(row: dict | None) -> str:
    if not row:
        return "warning"
    if row.get("readiness_status") == "ready":
        return "healthy"
    if int(row.get("error_count", 0) or 0) > 0:
        return "critical"
    return "warning"


def _route_metric(row: dict | None, backlog_count: int) -> str:
    if not row:
        return f"alerts={backlog_count}"
    return (
        f"lat={int(row.get('avg_latency_ms', 0) or 0)}ms "
        f"cost=${float(row.get('total_cost_estimate', 0) or 0):.4f} "
        f"alerts={backlog_count}"
    )


def _derive_optimization_opportunities(
    route_rows: list[dict],
    bundle_rows: list[dict],
    trend_rows: list[dict],
    sentinela_rows: list[dict],
) -> list[dict]:
    items: list[dict] = []
    routes = {row.get("route_selected", ""): row for row in route_rows}
    copilot = routes.get("copilot")
    genie = routes.get("genie")
    if copilot:
        current = float(copilot.get("total_cost_estimate", 0) or 0)
        policy = float(copilot.get("policy_max_cost_estimate", 0) or 0)
        tokens = int(copilot.get("total_tokens", 0) or 0)
        if policy and current >= policy * 0.8:
            items.append({
                "title": "Ajustar tier routing do Copilot",
                "impact": "alta",
                "detail": f"Custo do copilot em ${current:.4f} perto do limite de ${policy:.4f}.",
            })
        if tokens >= 3000:
            items.append({
                "title": "Reduzir max tokens e prompts longos",
                "impact": "média",
                "detail": f"Copilot acumulou {tokens:,} tokens na janela mais recente.",
            })
    if genie and int(genie.get("stale_freshness_count", 0) or 0) > 0:
        items.append({
            "title": "Sincronizar Genie com freshness Gold",
            "impact": "alta",
            "detail": "Há leituras stale no Genie; revisar cadência de refresh e readiness.",
        })
    failed_jobs = [row for row in bundle_rows if (row.get("failed_count", 0) or 0) > 0]
    if failed_jobs:
        items.append({
            "title": "Reduzir reruns de jobs com falha",
            "impact": "alta",
            "detail": f"{len(failed_jobs)} jobs com falhas aumentam custo operacional e atraso de serving.",
        })
    if sentinela_rows and sentinela_rows[0].get("runtime_alerts", 0):
        items.append({
            "title": "Atacar backlog runtime do Sentinela",
            "impact": "média",
            "detail": f"Há {int(sentinela_rows[0].get('runtime_alerts', 0) or 0)} alertas runtime acumulados.",
        })
    costly_routes = [
        row for row in trend_rows
        if float(row.get("total_cost_estimate", 0) or 0) >= 0.03
    ]
    if costly_routes:
        items.append({
            "title": "Aplicar budget cap por rota",
            "impact": "média",
            "detail": f"{len(costly_routes)} buckets horários excederam custo operacional elevado.",
        })
    if not items:
        items.append({
            "title": "Sem gargalos críticos no momento",
            "impact": "baixa",
            "detail": "Os sinais atuais estão alinhados com o baseline de custo e operação.",
        })
    return items[:6]


def _render_resource_board(resources: list[dict]) -> html.Div:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for resource in resources:
        grouped[resource["layer"]].append(resource)

    sections: list = []
    for layer in _LAYER_ORDER:
        rows = grouped.get(layer, [])
        if not rows:
            continue
        sections.append(
            dbc.Card(
                [
                    dbc.CardHeader(html.Strong(layer, style={"fontSize": "13px"})),
                    dbc.CardBody(
                        dbc.Row(
                            [
                                dbc.Col(_resource_card(row), width=6, className="mb-2")
                                for row in rows
                            ]
                        )
                    ),
                ],
                className="mb-3 border-0 shadow-sm",
            )
        )
    return html.Div(sections)


def _resource_card(row: dict) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(html.Div(row["resource"], style={"fontSize": "13px", "fontWeight": "700"}), width=8),
                        dbc.Col(
                            dbc.Badge(_STATUS_LABEL[row["status"]], color=_STATUS_COLOR[row["status"]], pill=True),
                            width=4,
                            className="text-end",
                        ),
                    ],
                    align="center",
                ),
                html.Div(row["detail"], style={"fontSize": "11px", "color": "#6B7280", "marginTop": "6px"}),
                html.Div(row["metric"], style={"fontSize": "11px", "fontWeight": "600", "marginTop": "8px"}),
            ]
        ),
        className=f"border-start border-4 border-{_STATUS_COLOR[row['status']]} h-100",
    )


def _render_optimization_list(items: list[dict]) -> html.Div:
    blocks = []
    for item in items:
        color = {"alta": "danger", "média": "warning", "baixa": "success"}[item["impact"]]
        blocks.append(
            dbc.Alert(
                [
                    html.Div(item["title"], style={"fontWeight": "700", "fontSize": "12px"}),
                    html.Div(item["detail"], style={"fontSize": "11px"}),
                ],
                color=color,
                className="mb-2",
                style={"padding": "10px 12px"},
            )
        )
    return html.Div(blocks)


def _build_route_cost_chart(route_rows: list[dict]) -> go.Figure:
    if not route_rows:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados de custo por rota", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=260, margin={"t": 10, "b": 30, "l": 40, "r": 10}, paper_bgcolor="white", plot_bgcolor="white")
        return fig
    fig = go.Figure()
    for row in route_rows:
        fig.add_trace(
            go.Bar(
                x=[row.get("route_selected", "?")],
                y=[float(row.get("total_cost_estimate", 0) or 0)],
                marker_color={
                    "ready": "#16A34A",
                    "hold": "#D97706",
                }.get(row.get("readiness_status", "hold"), "#DC2626"),
                text=[f"${float(row.get('total_cost_estimate', 0) or 0):.4f}"],
                textposition="outside",
                name=row.get("route_selected", "?"),
            )
        )
    fig.update_layout(
        height=260,
        showlegend=False,
        margin={"t": 10, "b": 40, "l": 40, "r": 10},
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"size": 11},
        yaxis={"title": "USD estimado"},
    )
    return fig


def _render_resource_table(resources: list[dict]) -> html.Div:
    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Camada", style={"fontSize": "12px"}),
                html.Th("Recurso", style={"fontSize": "12px"}),
                html.Th("Status", style={"fontSize": "12px"}),
                html.Th("Detalhe", style={"fontSize": "12px"}),
                html.Th("Métrica", style={"fontSize": "12px"}),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(row["layer"], style={"fontSize": "11px"}),
                    html.Td(html.Strong(row["resource"], style={"fontSize": "11px"})),
                    html.Td(dbc.Badge(_STATUS_LABEL[row["status"]], color=_STATUS_COLOR[row["status"]], pill=True)),
                    html.Td(row["detail"], style={"fontSize": "11px"}),
                    html.Td(row["metric"], style={"fontSize": "11px", "fontWeight": "600"}),
                ])
                for row in resources
            ]),
        ],
        bordered=False,
        striped=True,
        hover=True,
        size="sm",
        responsive=True,
    )


def _mock_ready_overview() -> list[dict]:
    return [{
        "route_rows": 4,
        "ready_routes": 3,
        "hold_routes": 1,
        "total_events": 1280,
        "total_errors": 4,
        "total_cost_estimate": 0.084,
        "peak_latency_ms": 1400,
        "stale_freshness_count": 1,
    }]


def _mock_route_readiness() -> list[dict]:
    return [
        {"route_selected": "genie", "readiness_status": "hold", "avg_latency_ms": 210, "error_count": 0, "total_tokens": 0, "total_cost_estimate": 0.001, "stale_freshness_count": 1, "policy_max_cost_estimate": 0.02},
        {"route_selected": "copilot", "readiness_status": "ready", "avg_latency_ms": 820, "error_count": 0, "total_tokens": 3150, "total_cost_estimate": 0.041, "stale_freshness_count": 0, "policy_max_cost_estimate": 0.05},
        {"route_selected": "dashboard_api", "readiness_status": "ready", "avg_latency_ms": 110, "error_count": 0, "total_tokens": 300, "total_cost_estimate": 0.002, "stale_freshness_count": 0, "policy_max_cost_estimate": 0.005},
        {"route_selected": "internal_app", "readiness_status": "ready", "avg_latency_ms": 180, "error_count": 0, "total_tokens": 650, "total_cost_estimate": 0.004, "stale_freshness_count": 0, "policy_max_cost_estimate": 0.03},
    ]


def _mock_bundle_status() -> list[dict]:
    return [
        {"job_name": "market_source_ingestion_job", "bundle_readiness_status": "ready", "success_count": 42, "failed_count": 0, "running_count": 0},
        {"job_name": "defillama_ingestion_job", "bundle_readiness_status": "hold", "success_count": 38, "failed_count": 1, "running_count": 0},
        {"job_name": "ops_readiness_refresh_job", "bundle_readiness_status": "ready", "success_count": 28, "failed_count": 0, "running_count": 0},
    ]


def _mock_sentinela_status() -> list[dict]:
    return [{"sentinela_alert_status": "hold", "total_alerts": 3, "bundle_alerts": 1, "runtime_alerts": 2}]


def _mock_alert_backlog() -> list[dict]:
    return [
        {"alert_kind": "freshness_gap", "route_selected": "genie", "alert_count": 1, "latest_event_time": "2026-05-06T12:00:00Z"},
        {"alert_kind": "cost_anomaly", "route_selected": "copilot", "alert_count": 1, "latest_event_time": "2026-05-06T12:00:00Z"},
    ]


def _mock_tier_cost() -> list[dict]:
    return [
        {"model_tier": "light", "total_cost_usd": 0.304},
        {"model_tier": "standard", "total_cost_usd": 2.480},
        {"model_tier": "complex", "total_cost_usd": 5.250},
    ]


def _mock_cost_latency_trend() -> list[dict]:
    return [
        {"route_selected": "copilot", "hour_bucket": "2026-05-06T11:00:00Z", "total_cost_estimate": 0.041},
        {"route_selected": "copilot", "hour_bucket": "2026-05-06T10:00:00Z", "total_cost_estimate": 0.032},
        {"route_selected": "genie", "hour_bucket": "2026-05-06T11:00:00Z", "total_cost_estimate": 0.001},
    ]
