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

Status as of 2026-05-03:

- `contexto` — DONE
- `arquitetura` — DONE
- `dados` — DONE (Bronze → Silver → Gold, 22 jobs across market, enrichment, ops, MLOps, governance, and compliance)
- `governanca` — DONE (`uc_grants_job` executes foundation SQL as CI-triggerable Databricks job)
- `lineage` — DONE (`unity-catalog-lineage-map.md`, automated lineage via UC System Tables optional)
- `execucao` — DONE (all jobs scheduled in DABs, CI gate)
- `validacao` — DONE (355 tests, validate_bundle, validate chains, live_sql_validation path, compile validation)
- `observabilidade` — DONE (`sentinela_evaluation_job` scheduled every 15 min, ops views, cga-admin surfaces)
- `access control` — DONE (`uc_grants_job` automates GRANT execution; triggered via `confirm_uc_grants` workflow_dispatch)
- `data contracts` — DONE (7 JSON schema contracts + Gold data contracts doc + contract CI step)
- `operacao` — DONE (`sentinela_evaluation_job` live runtime + `ops_readiness_refresh_job` + cga-admin ops surface)
- `deploy` — DONE (DABs full pipeline, 4 CI gates: deploy/apps/uc_grants/train)
- `custo` — DONE (model tier routing, cost_estimate on every response, cga-admin cost monitor)
- `compliance` — DONE (`rls_migration_job` applies UC row filters + cost_usd column masking; triggered via `confirm_uc_grants`)
- `mlops` — DONE (feature engineering + regime classifier + anomaly detector + batch scoring + MLflow registry)

## Current Repository State

Live baseline online. CI green. Future Databricks and Terraform mutations still require explicit approval and workflow_dispatch execution.

**Data Pipeline**
- Bronze → Silver → Gold medallion, 22 jobs (market + enrichment + ops + MLOps + governance + compliance)
- `ops_readiness_refresh_job` creates Gold views and Genie metric views on schedule

**Backend**
- `copilot_orchestrator.py` — 3 domain agents + SynthAgent, coded Python
- `copilot_mvp.py` — routing BFF, tier classification, orchestrator integration
- `mosaic_copilot_client.py`, `model_tier_router.py`, `databricks_sql_client.py`, `genie_client.py`

**Apps**
- `apps/cga-analytics/` — Genie panel + chart dashboard + copilot panel, registered in DABs
- `apps/cga-admin/` — 5-page admin surface (Sentinela, Pipeline Health, Cost, Access, Audit), registered in DABs

**MLOps**
- `feature_engineering_job.py` — Silver feature table with momentum/dominance features
- `train_market_model_job.py` — Regime Classifier + Anomaly Detector → MLflow Model Registry
- `score_market_assets_job.py` — batch scoring → `gold_ml_scores`

**Governance / Compliance**
- `uc_grants_job.py` — executes unity_catalog_foundation.sql (CREATE CATALOG, GRANT) in workspace
- `rls_migration_job.py` — applies UC row filters and cost_usd column masking

## Workspace Activation (runtime only — requires live credentials)

Three `workflow_dispatch` triggers remain the controlled path for future workspace mutations:

1. `confirm_deploy=true` — deploys bundle + runs full data pipeline (Bronze→Silver→Gold→MLOps)
2. `confirm_uc_grants=true` — runs `uc_grants_job` (GRANT statements) + `rls_migration_job` (RLS/masking)
3. `confirm_train=true` — runs `train_market_model_job` after first Silver batch lands

## Avoid

- Do not build a third app surface — all product UI goes into `cga-analytics` or `cga-admin`.
- Do not bypass Genie as the chart controller — Genie SQL output must drive state, not hardcoded queries.
- Do not assume the public API source mix is solved permanently by one provider.
- Do not skip telemetry, cost controls, or auditability for AI features.
- Do not treat design artifacts as implementation completion.
