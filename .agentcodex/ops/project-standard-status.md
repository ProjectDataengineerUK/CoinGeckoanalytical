# Project Standard Status

## Purpose

Provide one durable manifest for the AgentCodex Project Standard blocks required by this repository.

## Current Workflow Position

- project: `CoinGeckoAnalytical`
- workflow_phase: `ship`
- phase_group: `Live Databricks Apps Baseline`
- status_date: `2026-05-05`
- last_update: `2026-05-05 reconciliacao final do estado live-online + auditoria geral`

## Status Matrix

| Block | Status | Primary Evidence | Residual Hardening Gap |
|---|---|---|---|
| `contexto` | `implemented` | `README.md`, `.agentcodex/history/CONTEXT-HISTORY.md`, `BRAINSTORM_`, `DEFINE_` | keep status artifacts reconciled as the runtime evolves |
| `arquitetura` | `implemented` | `docs/architecture.md`, `DESIGN_coingeckoanalytical.md`, `CLAUDE.md` | maintain the Databricks Apps primary-surface decision consistently |
| `dados` | `implemented` | Bronze→Silver→Gold + enrichment chain + 22 jobs + live baseline evidence in reports | future source expansion beyond current 4 sources |
| `governanca` | `implemented` | `.agentcodex/ops/governance-and-ownership.md`, `databricks/unity-catalog-foundation.md`, `databricks/terraform/main.tf`, `uc_grants_job` | keep workspace principals aligned across environments |
| `lineage` | `implemented` | `databricks/unity-catalog-lineage-map.md`, `databricks/docs/gold-data-contracts.md`, UC/System Tables posture | add richer automated lineage evidence when promoted to staging/prod |
| `execucao` | `implemented` | `backend/databricks_sql_client.py`, `backend/genie_client.py`, `backend/mosaic_copilot_client.py`, `backend/routing_bff.py`, BFF + apps + scheduled jobs | maintain evidence growth across environments |
| `validacao` | `implemented` | compile validation + `validate_bundle.py` + chain validators + `355` local tests + live validation path | strengthen PR-time live integration coverage |
| `observabilidade` | `implemented` | `backend/sentinela.py`, `telemetry-observability.sql`, `ops_readiness_dashboard.sql`, `cga-admin` | outbound notification delivery still pending |
| `access control` | `implemented` | `.agentcodex/ops/access-control-model.md`, UC grants flow, `rls_migration_job`, masking SQL | tenant isolation beyond current RLS remains open |
| `data contracts` | `implemented` | `contracts/*.schema.json`, Gold data contracts, chain validators | evolve versioning policy as external consumers grow |
| `operacao` | `implemented` | `sentinela_evaluation_job`, `ops_readiness_refresh_job`, runbooks, approval policy, `cga-admin` | incident escalation/webhook automation still pending |
| `deploy` | `implemented` | `databricks.yml`, CI gates, apps deploy path, serialized workflow dependencies | staging/prod promotion still manual |
| `custo` | `implemented` | tier routing, telemetry schema, `cga-admin` cost monitor, cost controls policy | enforce runtime rate limiting in addition to budget caps |
| `compliance` | `implemented` | `.agentcodex/ops/compliance-posture.md`, retention/audit policy, `rls_migration_job`, masking | add DR evidence and environment-by-environment control attestations |

## Live Baseline Note

The project-standard baseline is considered implemented for the current live-online Databricks Apps scenario.

This does not mean hardening is finished. Remaining work is now primarily:

- promotion automation
- cross-environment evidence growth
- notification automation

## Update Rule

Update this manifest whenever one of the 14 blocks changes status or receives materially stronger live evidence.
