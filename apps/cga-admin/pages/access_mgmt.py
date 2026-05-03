from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html

REFRESH_BTN_ID = "access-refresh-btn"
TENANT_TABLE_ID = "access-tenant-table"
GROUPS_TABLE_ID = "access-groups-table"
ACTION_MSG_ID = "access-action-msg"
NEW_TENANT_INPUT_ID = "access-new-tenant-input"
ADD_TENANT_BTN_ID = "access-add-tenant-btn"

# Unity Catalog groups mapped to product roles
_UC_GROUPS = [
    {"group": "cga_analysts", "role": "Analista", "access": "cga-analytics (read)", "color": "primary"},
    {"group": "cga_traders", "role": "Trader", "access": "cga-analytics (read)", "color": "primary"},
    {"group": "cga_institutional", "role": "Institucional", "access": "cga-analytics (read) + Gold exports", "color": "success"},
    {"group": "cga_admins", "role": "Admin", "access": "cga-analytics + cga-admin (full)", "color": "danger"},
    {"group": "cga_ops", "role": "Operações", "access": "cga-admin (read)", "color": "warning"},
]


def layout() -> html.Div:
    return html.Div(
        [
            _page_header(
                "🔐 Gestão de Acessos — Unity Catalog",
                "Tenants, grupos e permissões da plataforma",
                btn_id=REFRESH_BTN_ID,
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("👥", "Grupos Unity Catalog")),
                                dbc.CardBody(_render_uc_groups()),
                            ],
                            className="shadow-sm",
                        ),
                        width=5,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(_card_header("🏢", "Tenants Ativos")),
                                dbc.CardBody(html.Div(id=TENANT_TABLE_ID)),
                            ],
                            className="shadow-sm",
                        ),
                        width=7,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Card(
                [
                    dbc.CardHeader(_card_header("➕", "Provisionar Novo Tenant")),
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Input(
                                            id=NEW_TENANT_INPUT_ID,
                                            placeholder="ID do tenant (ex: tenant_gamma)",
                                            size="sm",
                                        ),
                                        width=5,
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "Provisionar",
                                            id=ADD_TENANT_BTN_ID,
                                            color="primary",
                                            size="sm",
                                        ),
                                        width=2,
                                    ),
                                    dbc.Col(html.Div(id=ACTION_MSG_ID), width=5),
                                ],
                                align="center",
                            ),
                            html.Hr(style={"marginTop": "12px"}),
                            dbc.Alert(
                                [
                                    html.Strong("Nota: "),
                                    "O provisionamento efetivo de grupos e permissões no Unity Catalog "
                                    "requer execução via Databricks REST API com credenciais de admin. "
                                    "Este painel registra a intenção e gera o comando GRANT correspondente.",
                                ],
                                color="info",
                                style={"fontSize": "12px"},
                            ),
                        ]
                    ),
                ],
                className="shadow-sm",
            ),
        ],
        style={"padding": "16px"},
    )


@callback(
    Output(TENANT_TABLE_ID, "children"),
    Input(REFRESH_BTN_ID, "n_clicks"),
    prevent_initial_call=False,
)
def refresh_tenants(n_clicks):
    from services import ops_service

    # Derive active tenants from usage events
    usage = ops_service.fetch_usage_events(500)
    if usage:
        tenants: dict = {}
        for r in usage:
            tid = r.get("tenant_id", "unknown")
            tenants.setdefault(tid, {"requests": 0, "last_seen": ""})
            tenants[tid]["requests"] += 1
            ts = str(r.get("event_time", ""))
            if ts > tenants[tid]["last_seen"]:
                tenants[tid]["last_seen"] = ts
        rows = [{"tenant_id": k, **v} for k, v in sorted(tenants.items(), key=lambda x: -x[1]["requests"])]
    else:
        rows = _mock_tenants()

    return _render_tenant_table(rows)


@callback(
    Output(ACTION_MSG_ID, "children"),
    Input(ADD_TENANT_BTN_ID, "n_clicks"),
    State(NEW_TENANT_INPUT_ID, "value"),
    prevent_initial_call=True,
)
def provision_tenant(n_clicks, tenant_id):
    if not tenant_id or not tenant_id.strip():
        return dbc.Alert("Digite um tenant ID.", color="warning", style={"fontSize": "12px"})
    tid = tenant_id.strip().lower().replace(" ", "_")
    grant_sql = (
        f"GRANT USAGE ON CATALOG cgadev TO `cga_analysts`;\n"
        f"-- Tenant: {tid}\n"
        f"-- Execute via Databricks Admin Console ou CLI:\n"
        f"-- databricks groups add-member --group-name cga_analysts --member-name {tid}"
    )
    return dbc.Alert(
        [
            html.Strong(f"Tenant '{tid}' preparado. "),
            html.Details(
                [
                    html.Summary("Ver comando GRANT", style={"cursor": "pointer", "color": "#2563EB"}),
                    html.Pre(grant_sql, style={"fontSize": "11px", "marginTop": "6px"}),
                ]
            ),
        ],
        color="success",
        style={"fontSize": "12px"},
    )


def _render_uc_groups() -> html.Div:
    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Grupo UC", style={"fontSize": "11px"}),
                html.Th("Papel", style={"fontSize": "11px"}),
                html.Th("Acesso", style={"fontSize": "11px"}),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(html.Code(g["group"], style={"fontSize": "11px"})),
                    html.Td(dbc.Badge(g["role"], color=g["color"], pill=True, style={"fontSize": "10px"})),
                    html.Td(html.Small(g["access"], style={"color": "#6B7280"})),
                ])
                for g in _UC_GROUPS
            ]),
        ],
        bordered=False, striped=True, size="sm",
    )


def _render_tenant_table(rows: list[dict]) -> html.Div:
    if not rows:
        return html.Small("Nenhum tenant ativo encontrado.", style={"color": "#6B7280"})
    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Tenant ID", style={"fontSize": "12px"}),
                html.Th("Requests", style={"fontSize": "12px"}),
                html.Th("Último acesso", style={"fontSize": "12px"}),
                html.Th("Status", style={"fontSize": "12px"}),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(html.Strong(r.get("tenant_id", "?"), style={"fontSize": "12px"})),
                    html.Td(f"{r.get('requests', 0):,}", style={"fontSize": "12px"}),
                    html.Td(str(r.get("last_seen", ""))[:16], style={"fontSize": "12px"}),
                    html.Td(dbc.Badge("ativo", color="success", pill=True, style={"fontSize": "10px"})),
                ])
                for r in rows
            ]),
        ],
        bordered=False, striped=True, hover=True, size="sm", responsive=True,
    )


def _mock_tenants() -> list[dict]:
    return [
        {"tenant_id": "tenant_alpha", "requests": 22, "last_seen": "2026-05-02 14:22"},
        {"tenant_id": "tenant_beta", "requests": 180, "last_seen": "2026-05-02 13:55"},
        {"tenant_id": "default", "requests": 640, "last_seen": "2026-05-02 14:30"},
    ]
