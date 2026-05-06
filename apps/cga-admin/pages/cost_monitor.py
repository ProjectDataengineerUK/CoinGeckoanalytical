from __future__ import annotations

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from . import _card_header, _page_header

REFRESH_BTN_ID = "cost-refresh-btn"
KPI_ROW_ID = "cost-kpi-row"
CHART_DAILY_ID = "cost-daily-chart"
CHART_TIER_ID = "cost-tier-chart"
TABLE_TENANT_ID = "cost-tenant-table"
INFRA_TABLE_ID = "cost-infra-table"
OPTIMIZATION_ID = "cost-optimization-list"

_TIER_COLOR = {"light": "#10B981", "standard": "#3B82F6", "complex": "#EF4444"}
_TIER_LABEL = {
    "light": "⚡ Light — Gemma 12B",
    "standard": "🔷 Standard — GPT-OSS 120B",
    "complex": "🧠 Complex — Qwen3 80B",
}


def layout() -> html.Div:
    return html.Div(
        [
            _page_header(
                "💰 Custo & Tokens — LLMOps Telemetria",
                "Consumo por tier de modelo, tenant e período",
                btn_id=REFRESH_BTN_ID,
            ),
            html.Div(id=KPI_ROW_ID, className="mb-3"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("📅", "Gasto Diário por Tier")),
                                dbc.CardBody(dcc.Graph(id=CHART_DAILY_ID, config={"displayModeBar": False})),
                            ],
                            className="shadow-sm",
                        ),
                        width=8,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("🥧", "Distribuição por Tier")),
                                dbc.CardBody(dcc.Graph(id=CHART_TIER_ID, config={"displayModeBar": False})),
                            ],
                            className="shadow-sm",
                        ),
                        width=4,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Card(
                [
                    dbc.CardHeader(_card_header("👥", "Top Tenants por Custo")),
                    dbc.CardBody(html.Div(id=TABLE_TENANT_ID)),
                ],
                className="shadow-sm",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("🧱", "Infra & Recursos Databricks")),
                                dbc.CardBody(html.Div(id=INFRA_TABLE_ID)),
                            ],
                            className="shadow-sm h-100",
                        ),
                        width=7,
                        className="mt-3",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("💡", "Oportunidades de Otimização")),
                                dbc.CardBody(html.Div(id=OPTIMIZATION_ID)),
                            ],
                            className="shadow-sm h-100",
                        ),
                        width=5,
                        className="mt-3",
                    ),
                ]
            ),
        ],
        style={"padding": "16px"},
    )


@callback(
    Output(KPI_ROW_ID, "children"),
    Output(CHART_DAILY_ID, "figure"),
    Output(CHART_TIER_ID, "figure"),
    Output(TABLE_TENANT_ID, "children"),
    Output(INFRA_TABLE_ID, "children"),
    Output(OPTIMIZATION_ID, "children"),
    Input(REFRESH_BTN_ID, "n_clicks"),
    prevent_initial_call=False,
)
def refresh_cost(n_clicks):
    from services import ops_service

    tier_rows = ops_service.fetch_cost_by_tier() or _mock_tier_summary()
    daily_rows = ops_service.fetch_daily_spend(14) or _mock_daily()
    tenant_rows = ops_service.fetch_cost_by_tenant() or _mock_tenants()
    route_rows = ops_service.fetch_route_readiness_latest() or _mock_route_readiness()
    bundle_rows = ops_service.fetch_bundle_run_status() or _mock_bundle_status()

    total_cost = sum(r.get("total_cost_usd", 0) or 0 for r in tier_rows)
    total_tokens = sum(r.get("total_tokens", 0) or 0 for r in tier_rows)
    total_requests = sum(r.get("requests", 0) or 0 for r in tier_rows)
    infra_rows = _build_infra_rows(route_rows, bundle_rows)
    opportunities = _build_cost_opportunities(route_rows, bundle_rows)

    kpi_row = dbc.Row(
        [
            dbc.Col(_kpi_card("💵 Custo Total", f"${total_cost:.4f}", "USD estimado"), width=3),
            dbc.Col(_kpi_card("🔤 Tokens Total", f"{total_tokens:,}", "soma todos os tiers"), width=3),
            dbc.Col(_kpi_card("📨 Requests", f"{total_requests:,}", "total de consultas"), width=3),
            dbc.Col(_kpi_card("⚡ Custo Médio", f"${total_cost / max(total_requests, 1):.5f}", "por request"), width=3),
        ]
    )

    return (
        kpi_row,
        _build_daily_chart(daily_rows),
        _build_tier_pie(tier_rows),
        _render_tenant_table(tenant_rows),
        _render_infra_table(infra_rows),
        _render_optimization_list(opportunities),
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


def _build_daily_chart(rows: list[dict]) -> go.Figure:
    if not rows:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(**_base_layout(260))
        return fig

    tiers = sorted({r.get("model_tier", "standard") for r in rows})
    days = sorted({str(r.get("day", ""))[:10] for r in rows})

    fig = go.Figure()
    for tier in tiers:
        tier_rows = [r for r in rows if r.get("model_tier") == tier]
        day_cost = {str(r.get("day", ""))[:10]: r.get("cost_usd", 0) for r in tier_rows}
        fig.add_trace(go.Bar(
            name=_TIER_LABEL.get(tier, tier),
            x=days,
            y=[day_cost.get(d, 0) for d in days],
            marker_color=_TIER_COLOR.get(tier, "#6B7280"),
        ))
    fig.update_layout(barmode="stack", **_base_layout(260))
    return fig


def _build_tier_pie(rows: list[dict]) -> go.Figure:
    if not rows:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(**_base_layout(260))
        return fig

    labels = [_TIER_LABEL.get(r.get("model_tier", "?"), r.get("model_tier", "?")) for r in rows]
    values = [r.get("total_cost_usd", 0) or 0 for r in rows]
    colors = [_TIER_COLOR.get(r.get("model_tier", ""), "#6B7280") for r in rows]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.45,
        marker={"colors": colors},
        textinfo="percent+label",
        textfont_size=10,
        hovertemplate="%{label}<br>$%{value:.5f}<extra></extra>",
    ))
    fig.update_layout(**_base_layout(260))
    return fig


def _render_tenant_table(rows: list[dict]) -> html.Div:
    if not rows:
        return html.Small("Sem dados de tenant.", style={"color": "#6B7280"})
    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Tenant", style={"fontSize": "12px"}),
                html.Th("Tier", style={"fontSize": "12px"}),
                html.Th("Requests", style={"fontSize": "12px"}),
                html.Th("Tokens", style={"fontSize": "12px"}),
                html.Th("Custo (USD)", style={"fontSize": "12px"}),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(r.get("tenant_id", "?"), style={"fontSize": "11px"}),
                    html.Td(
                        dbc.Badge(r.get("model_tier", "?"),
                                  color={"light": "success", "standard": "primary", "complex": "danger"}.get(r.get("model_tier", ""), "secondary"),
                                  pill=True, style={"fontSize": "10px"})
                    ),
                    html.Td(f"{r.get('requests', 0):,}", style={"fontSize": "11px"}),
                    html.Td(f"{r.get('total_tokens', 0):,}", style={"fontSize": "11px"}),
                    html.Td(f"${r.get('total_cost_usd', 0):.5f}", style={"fontSize": "11px", "fontWeight": "600"}),
                ])
                for r in rows[:15]
            ]),
        ],
        bordered=False, striped=True, hover=True, size="sm", responsive=True,
    )


def _build_infra_rows(route_rows: list[dict], bundle_rows: list[dict]) -> list[dict]:
    route_map = {row.get("route_selected", ""): row for row in route_rows}
    return [
        {
            "resource": "SQL Warehouse / Genie",
            "category": "consulta governada",
            "cost": float((route_map.get("genie") or {}).get("total_cost_estimate", 0) or 0),
            "latency": int((route_map.get("genie") or {}).get("avg_latency_ms", 0) or 0),
            "status": (route_map.get("genie") or {}).get("readiness_status", "hold"),
        },
        {
            "resource": "Mosaic AI / Copilot",
            "category": "narrativa AI",
            "cost": float((route_map.get("copilot") or {}).get("total_cost_estimate", 0) or 0),
            "latency": int((route_map.get("copilot") or {}).get("avg_latency_ms", 0) or 0),
            "status": (route_map.get("copilot") or {}).get("readiness_status", "hold"),
        },
        {
            "resource": "Dashboard API",
            "category": "payload analítico",
            "cost": float((route_map.get("dashboard_api") or {}).get("total_cost_estimate", 0) or 0),
            "latency": int((route_map.get("dashboard_api") or {}).get("avg_latency_ms", 0) or 0),
            "status": (route_map.get("dashboard_api") or {}).get("readiness_status", "hold"),
        },
        {
            "resource": "Databricks Jobs",
            "category": "ingestão e refresh",
            "cost": 0.0,
            "latency": int(max((row.get("avg_duration_ms", 0) or 0) for row in bundle_rows) if bundle_rows else 0),
            "status": "ready" if all((row.get("bundle_readiness_status") == "ready") for row in bundle_rows) else "hold",
        },
    ]


def _render_infra_table(rows: list[dict]) -> html.Div:
    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Recurso", style={"fontSize": "12px"}),
                html.Th("Categoria", style={"fontSize": "12px"}),
                html.Th("Custo", style={"fontSize": "12px"}),
                html.Th("Latência / Duração", style={"fontSize": "12px"}),
                html.Th("Status", style={"fontSize": "12px"}),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(html.Strong(row["resource"], style={"fontSize": "11px"})),
                    html.Td(row["category"], style={"fontSize": "11px"}),
                    html.Td(f"${row['cost']:.4f}", style={"fontSize": "11px", "fontWeight": "600"}),
                    html.Td(f"{row['latency']} ms", style={"fontSize": "11px"}),
                    html.Td(
                        dbc.Badge(
                            "verde" if row["status"] == "ready" else "amarelo",
                            color="success" if row["status"] == "ready" else "warning",
                            pill=True,
                        )
                    ),
                ])
                for row in rows
            ]),
        ],
        bordered=False,
        striped=True,
        hover=True,
        size="sm",
        responsive=True,
    )


def _build_cost_opportunities(route_rows: list[dict], bundle_rows: list[dict]) -> list[dict]:
    items: list[dict] = []
    for row in route_rows:
        route = row.get("route_selected", "?")
        cost = float(row.get("total_cost_estimate", 0) or 0)
        latency = int(row.get("avg_latency_ms", 0) or 0)
        policy = float(row.get("policy_max_cost_estimate", 0) or 0)
        if policy and cost >= policy * 0.8:
            items.append({
                "title": f"Reduzir custo da rota {route}",
                "detail": f"Custo em ${cost:.4f} próximo do teto ${policy:.4f}.",
                "color": "warning",
            })
        if latency >= 1000:
            items.append({
                "title": f"Otimizar latência da rota {route}",
                "detail": f"Latência média de {latency} ms indica oportunidade de simplificar o caminho.",
                "color": "danger",
            })
    if any((row.get("failed_count", 0) or 0) > 0 for row in bundle_rows):
        items.append({
            "title": "Reduzir custo de rerun de jobs",
            "detail": "Há jobs com falhas recentes; estabilizar ingestões evita recomputação e atraso.",
            "color": "danger",
        })
    if not items:
        items.append({
            "title": "Sem alertas fortes de custo",
            "detail": "O baseline atual está dentro do envelope esperado de AI e operação.",
            "color": "success",
        })
    return items[:6]


def _render_optimization_list(items: list[dict]) -> html.Div:
    return html.Div(
        [
            dbc.Alert(
                [
                    html.Div(item["title"], style={"fontWeight": "700", "fontSize": "12px"}),
                    html.Div(item["detail"], style={"fontSize": "11px"}),
                ],
                color=item["color"],
                className="mb-2",
                style={"padding": "10px 12px"},
            )
            for item in items
        ]
    )


def _base_layout(height: int) -> dict:
    return {
        "height": height,
        "margin": {"t": 10, "b": 30, "l": 50, "r": 10},
        "paper_bgcolor": "white",
        "plot_bgcolor": "white",
        "font": {"size": 11},
        "legend": {"font": {"size": 9}},
    }


def _mock_tier_summary() -> list[dict]:
    return [
        {"model_tier": "light", "requests": 820, "total_tokens": 380_000, "total_cost_usd": 0.304, "avg_latency_ms": 180},
        {"model_tier": "standard", "requests": 340, "total_tokens": 620_000, "total_cost_usd": 2.48, "avg_latency_ms": 540},
        {"model_tier": "complex", "requests": 42, "total_tokens": 210_000, "total_cost_usd": 5.25, "avg_latency_ms": 2400},
    ]


def _mock_daily() -> list[dict]:
    import datetime
    rows = []
    base = datetime.date(2026, 4, 20)
    import random
    random.seed(42)
    for i in range(14):
        day = str(base + datetime.timedelta(days=i))
        rows += [
            {"day": day, "model_tier": "light", "cost_usd": round(random.uniform(0.01, 0.05), 4)},
            {"day": day, "model_tier": "standard", "cost_usd": round(random.uniform(0.1, 0.3), 4)},
            {"day": day, "model_tier": "complex", "cost_usd": round(random.uniform(0.2, 0.8), 4)},
        ]
    return rows


def _mock_tenants() -> list[dict]:
    return [
        {"tenant_id": "tenant_alpha", "model_tier": "complex", "requests": 22, "total_tokens": 110_000, "total_cost_usd": 2.75},
        {"tenant_id": "tenant_beta", "model_tier": "standard", "requests": 180, "total_tokens": 320_000, "total_cost_usd": 1.28},
        {"tenant_id": "default", "model_tier": "light", "requests": 640, "total_tokens": 280_000, "total_cost_usd": 0.224},
    ]


def _mock_route_readiness() -> list[dict]:
    return [
        {"route_selected": "genie", "readiness_status": "hold", "avg_latency_ms": 240, "total_cost_estimate": 0.004, "policy_max_cost_estimate": 0.02},
        {"route_selected": "copilot", "readiness_status": "ready", "avg_latency_ms": 820, "total_cost_estimate": 0.041, "policy_max_cost_estimate": 0.05},
        {"route_selected": "dashboard_api", "readiness_status": "ready", "avg_latency_ms": 120, "total_cost_estimate": 0.003, "policy_max_cost_estimate": 0.005},
    ]


def _mock_bundle_status() -> list[dict]:
    return [
        {"job_name": "market_source_ingestion_job", "bundle_readiness_status": "ready", "failed_count": 0, "avg_duration_ms": 1800},
        {"job_name": "defillama_ingestion_job", "bundle_readiness_status": "hold", "failed_count": 1, "avg_duration_ms": 4200},
    ]
