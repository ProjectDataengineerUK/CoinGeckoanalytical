# CLAUDE.md

## Project

- name: `CoinGeckoAnalytical`
- repository_root: `/home/user/Projetos/CoinGeckoanalytical`
- workflow_system: `AgentCodex`

## Current Product Direction

CoinGeckoAnalytical is a crypto market intelligence platform built entirely on Databricks with two product surfaces:

- `cga-analytics` Databricks App: main user-facing product — Genie conversational BI + coded copilot + dynamic charts
- `cga-admin` Databricks App: internal ops surface — Sentinela monitoring + access management + cost/token telemetry
- `Databricks` as the data, AI, governance, and serving platform
- `AI/BI Genie` as the analytical query controller — Genie SQL output drives chart state updates across the analytics app
- `Mosaic AI Agent Framework` (coded Python orchestrator, not Agent Bricks) for the narrative market copilot
- External web frontend is not in scope for V1 — Databricks Apps is the chosen primary surface

## Source Of Truth

Use these files in this order:

1. `AGENTS.md`
2. `.agentcodex/features/DEFINE_coingeckoanalytical.md`
3. `.agentcodex/features/DESIGN_coingeckoanalytical.md`
4. `README.md`

## Mandatory Workflow

Follow the AgentCodex flow unless the repository state clearly justifies a later step:

1. `brainstorm`
2. `define`
3. `design`
4. `build`
5. `ship`

Record verification artifacts under `.agentcodex/reports/`.

## Architecture Rules

- `Databricks Apps` is the chosen primary product surface — two apps: `cga-analytics` (user) and `cga-admin` (ops).
- `Genie` is the analytical query controller inside `cga-analytics` — its generated SQL drives chart re-rendering.
- Keep `Genie` scoped to structured analytics over governed Gold assets only.
- Keep the copilot in coded Python orchestration — do not use Agent Bricks as the primary agent mechanism.
- The coded multi-agent orchestrator (`copilot_orchestrator.py`) is the only approved copilot execution path.
- Keep all governed analytical assets under `Unity Catalog`.
- `cga-admin` is the only surface for Sentinela, access management, cost telemetry, and audit review.

## Data And AI Rules

- Primary initial data source: `CoinGecko API`
- Plan for future multi-source market intelligence rather than permanent single-provider dependence.
- Every grounded AI answer should expose provenance, freshness, and confidence context.
- Token and cost telemetry are required for copilot flows.
- Tenant isolation applies to dashboards, telemetry, and AI responses.

## CI/CD And Auth Guidance

- Prefer `Databricks Asset Bundles` for deployment automation.
- Use `service principal` authentication for CI/CD.
- Prefer `OAuth M2M` or workload identity federation over user PAT-based automation.
- Do not rely on interactive `databricks auth login` flows in CI.

## Approval Model

- All Databricks and Terraform mutations require explicit approval in chat before execution.
- Approval state is tracked in `.agentcodex/ops/approval-gate-policy.md` and `.agentcodex/reports/approval-gate-status.md`.
- Treat `workflow_dispatch` gates as the execution mechanism, not the approval source.

## Project Standard Blocks

Do not consider the project complete until these are implemented or explicitly marked not applicable:

- `contexto`
- `arquitetura`
- `dados`
- `governanca`
- `lineage`
- `execucao`
- `validacao`
- `observabilidade`
- `access control`
- `data contracts`
- `operacao`
- `deploy`
- `custo`
- `compliance`

## Current Repository State

Build phase in progress — backend contracts and data pipeline complete, apps not yet built:

- Medallion pipeline (Bronze → Silver → Gold) deployed and running in Databricks
- `backend/copilot_orchestrator.py` — multi-agent orchestrator (market + macro + defi + synth), coded Python
- `backend/copilot_mvp.py` — routing BFF with tier classification and orchestrator integration
- `backend/mosaic_copilot_client.py` — Unity AI Gateway client (3-tier: light / standard / complex)
- `backend/model_tier_router.py` — token cost optimizer
- `backend/databricks_sql_client.py` and `backend/genie_client.py` — Databricks SQL and Genie REST clients
- Design documents updated to reflect two-app Databricks surface

Not yet built:
- `cga-analytics` Databricks App (Genie-driven BI + Copilot + charts)
- `cga-admin` Databricks App (Sentinela + access management + ops telemetry)
- Sentinela live runtime
- Unity Catalog access control implementation
- DataOps / LLMOps operating stack

## Expected Next Steps

1. Design and build `cga-analytics` app skeleton (layout + Genie state controller + chart components)
2. Wire copilot orchestrator into analytics app chat panel
3. Design and build `cga-admin` app (Sentinela dashboard + access management + telemetry views)
4. Sentinela live monitoring runtime
5. Unity Catalog access control and tenant isolation

## Avoid

- Do not build a third app surface — all product UI goes into `cga-analytics` or `cga-admin`.
- Do not bypass Genie as the chart controller — Genie SQL output must drive state, not hardcoded queries.
- Do not assume the public API source mix is solved permanently by one provider.
- Do not skip telemetry, cost controls, or auditability for AI features.
- Do not treat design artifacts as implementation completion.
