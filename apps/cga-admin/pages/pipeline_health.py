from __future__ import annotations

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

REFRESH_BTN_ID = "pipeline-refresh-btn"
SUMMARY_TABLE_ID = "pipeline-summary-table"
RUNS_TABLE_ID = "pipeline-runs-table"
CHART_SUCCESS_RATE_ID = "pipeline-success-chart"

_SOURCE_ICONS = {
    "market_source_ingestion_job": "📈",
    "defillama_ingestion_job": "🏦",
    "github_activity_ingestion_job": "🐙",
    "fred_macro_ingestion_job": "🌍",
    "silver_enrichment_pipeline_job": "⚗️",
    "ops_usage_ingestion_job": "📊",
    "ops_readiness_refresh_job": "🔄",
    "ops_sentinela_alert_ingestion_job": "◉",
    "ops_bundle_run_ingestion_job": "📦",
}


def layout() -> html.Div:
    return html.Div(
        [
            _page_header(
                "⚙️ Pipeline Health — Ingestão e Processamento",
                "Status dos jobs Databricks por fonte de dados",
                btn_id=REFRESH_BTN_ID,
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("📋", "Resumo por Job")),
                                dbc.CardBody(html.Div(id=SUMMARY_TABLE_ID)),
                            ],
                            className="shadow-sm",
                        ),
                        width=7,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("✅", "Taxa de Sucesso")),
                                dbc.CardBody(dcc.Graph(id=CHART_SUCCESS_RATE_ID, config={"displayModeBar": False})),
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
                    dbc.CardHeader(_card_header("🕐", "Execuções Recentes")),
                    dbc.CardBody(html.Div(id=RUNS_TABLE_ID)),
                ],
                className="shadow-sm",
            ),
        ],
        style={"padding": "16px"},
    )


@callback(
    Output(SUMMARY_TABLE_ID, "children"),
    Output(RUNS_TABLE_ID, "children"),
    Output(CHART_SUCCESS_RATE_ID, "figure"),
    Input(REFRESH_BTN_ID, "n_clicks"),
    prevent_initial_call=False,
)
def refresh_pipeline(n_clicks):
    from services import ops_service

    summary = ops_service.fetch_pipeline_summary() or _mock_summary()
    runs = ops_service.fetch_bundle_runs(30) or _mock_runs()

    return (
        _render_summary(summary),
        _render_runs(runs),
        _build_success_chart(summary),
    )


def _render_summary(rows: list[dict]) -> html.Div:
    if not rows:
        return html.Small("Sem dados de pipeline.", style={"color": "#6B7280"})
    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Job", style={"fontSize": "12px"}),
                html.Th("Última execução", style={"fontSize": "12px"}),
                html.Th("Total", style={"fontSize": "12px"}),
                html.Th("Sucesso", style={"fontSize": "12px"}),
                html.Th("Falhas", style={"fontSize": "12px"}),
                html.Th("Status", style={"fontSize": "12px"}),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(
                        [
                            html.Span(_SOURCE_ICONS.get(r.get("job_name", ""), "📦") + " "),
                            html.Strong(r.get("job_name", "?"), style={"fontSize": "11px"}),
                        ]
                    ),
                    html.Td(str(r.get("last_run", "—"))[:19], style={"fontSize": "11px"}),
                    html.Td(r.get("total_runs", 0), style={"fontSize": "11px"}),
                    html.Td(
                        dbc.Badge(str(r.get("success_count", 0)), color="success", pill=True),
                    ),
                    html.Td(
                        dbc.Badge(str(r.get("failure_count", 0)),
                                  color="danger" if r.get("failure_count", 0) > 0 else "light",
                                  text_color="dark" if r.get("failure_count", 0) == 0 else None,
                                  pill=True),
                    ),
                    html.Td(
                        dbc.Badge("ok", color="success", pill=True)
                        if r.get("failure_count", 0) == 0 else
                        dbc.Badge("falhas", color="danger", pill=True)
                    ),
                ])
                for r in rows
            ]),
        ],
        bordered=False, striped=True, hover=True, size="sm", responsive=True,
    )


def _render_runs(rows: list[dict]) -> html.Div:
    if not rows:
        return html.Small("Sem execuções registradas.", style={"color": "#6B7280"})
    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Timestamp", style={"fontSize": "11px"}),
                html.Th("Job", style={"fontSize": "11px"}),
                html.Th("Status", style={"fontSize": "11px"}),
                html.Th("Linhas", style={"fontSize": "11px"}),
                html.Th("Erro", style={"fontSize": "11px"}),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(str(r.get("ingested_at", ""))[:19], style={"fontSize": "11px"}),
                    html.Td(r.get("job_name", "?"), style={"fontSize": "11px"}),
                    html.Td(
                        dbc.Badge(r.get("status", "?"),
                                  color="success" if r.get("status") == "SUCCESS" else "danger",
                                  pill=True, style={"fontSize": "10px"})
                    ),
                    html.Td(f"{r.get('rows_written', 0):,}", style={"fontSize": "11px"}),
                    html.Td(
                        html.Small(str(r.get("error_message", ""))[:50], style={"color": "#DC2626"})
                        if r.get("error_message") else ""
                    ),
                ])
                for r in rows[:20]
            ]),
        ],
        bordered=False, striped=True, size="sm", responsive=True,
    )


def _build_success_chart(rows: list[dict]) -> go.Figure:
    if not rows:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=250, margin={"t": 10, "b": 30, "l": 40, "r": 10}, paper_bgcolor="white", plot_bgcolor="white")
        return fig

    jobs = [r.get("job_name", "?").replace("_job", "").replace("_ingestion", "") for r in rows]
    success = [r.get("success_count", 0) for r in rows]
    failures = [r.get("failure_count", 0) for r in rows]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Sucesso", x=jobs, y=success, marker_color="#16A34A"))
    fig.add_trace(go.Bar(name="Falha", x=jobs, y=failures, marker_color="#DC2626"))
    fig.update_layout(
        barmode="stack", height=250,
        margin={"t": 10, "b": 60, "l": 40, "r": 10},
        paper_bgcolor="white", plot_bgcolor="white",
        font={"size": 10},
        xaxis={"tickangle": -30},
        legend={"font": {"size": 9}},
    )
    return fig


def _mock_summary() -> list[dict]:
    return [
        {"job_name": "market_source_ingestion_job", "last_run": "2026-05-02 14:00", "total_runs": 42, "success_count": 42, "failure_count": 0},
        {"job_name": "defillama_ingestion_job", "last_run": "2026-05-02 13:30", "total_runs": 38, "success_count": 37, "failure_count": 1},
        {"job_name": "github_activity_ingestion_job", "last_run": "2026-05-02 10:00", "total_runs": 14, "success_count": 14, "failure_count": 0},
        {"job_name": "fred_macro_ingestion_job", "last_run": "2026-05-01 08:00", "total_runs": 7, "success_count": 7, "failure_count": 0},
        {"job_name": "silver_enrichment_pipeline_job", "last_run": "2026-05-02 14:05", "total_runs": 42, "success_count": 41, "failure_count": 1},
    ]


def _mock_runs() -> list[dict]:
    return [
        {"ingested_at": "2026-05-02 14:05", "job_name": "silver_enrichment_pipeline_job", "status": "SUCCESS", "rows_written": 523, "error_message": None},
        {"ingested_at": "2026-05-02 14:00", "job_name": "market_source_ingestion_job", "status": "SUCCESS", "rows_written": 1200, "error_message": None},
        {"ingested_at": "2026-05-02 13:30", "job_name": "defillama_ingestion_job", "status": "FAILED", "rows_written": 0, "error_message": "DNS resolution failed"},
        {"ingested_at": "2026-05-02 10:00", "job_name": "github_activity_ingestion_job", "status": "SUCCESS", "rows_written": 48, "error_message": None},
    ]
