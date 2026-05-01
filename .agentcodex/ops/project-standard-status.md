# Project Standard Status

## Purpose

Provide one durable manifest for the AgentCodex Project Standard blocks required by this repository.

## Current Workflow Position

- project: `CoinGeckoAnalytical`
- workflow_phase: `build`
- phase_group: `Phase 1 Base`
- status_date: `2026-04-30`

## Status Matrix

| Block | Status | Primary Evidence | Remaining Gap |
|---|---|---|---|
| `contexto` | `implemented` | `README.md`, `.agentcodex/history/CONTEXT-HISTORY.md`, `BRAINSTORM_`, `DEFINE_` | keep the manifest current as the build evolves |
| `arquitetura` | `implemented` | `docs/architecture.md`, `DESIGN_coingeckoanalytical.md` | none for Phase 1 |
| `dados` | `implemented` | `databricks/bronze_silver_market_foundation.sql`, `databricks/gold_market_views.sql`, `databricks/genie_metric_views.sql` | bind to live Databricks execution evidence |
| `governanca` | `implemented` | `.agentcodex/ops/governance-and-ownership.md`, `databricks/unity-catalog-foundation.md`, `databricks/terraform/main.tf` | live workspace grants and owners still need evidence |
| `lineage` | `implemented` | `databricks/unity-catalog-lineage-map.md`, `databricks/gold-data-contracts.md` | add live Catalog Explorer validation evidence |
| `execucao` | `implemented` | `.agentcodex/features/BUILD_coingeckoanalytical.md`, `backend/routing_bff.py`, Databricks jobs and Terraform job baseline | execution is still repo-local, not live workspace verified |
| `validacao` | `partial` | backend tests, repo tests, `validate_bundle.py`, helper tests | missing live workspace validation and end-to-end acceptance report |
| `observabilidade` | `implemented` | `backend/sentinela.py`, `telemetry-observability.sql`, `ops_readiness_dashboard.sql` | live ingestion and rendered dashboard evidence still pending |
| `access control` | `implemented` | `.agentcodex/ops/access-control-model.md`, `databricks/unity_catalog_foundation.sql`, `databricks/terraform/main.tf` | live principal binding evidence still pending |
| `data contracts` | `implemented` | `contracts/*.schema.json`, `databricks/gold-data-contracts.md`, `databricks/bronze-silver-market-foundation.md` | contract lifecycle evidence can be strengthened later |
| `operacao` | `partial` | `.agentcodex/ops/sentinela-baseline.md`, `notification_policy.md`, `deployment_runbook.md`, `terraform-plan-apply-promotion.md` | missing incident runbook set and live operator evidence |
| `deploy` | `implemented` | `databricks.yml`, `preflight_databricks_deploy.py`, `deployment_runbook.md`, GitHub Actions `ci` run `25198087949`, `databricks-live-sql-validation` artifact metadata | inspect artifact JSON for row-count details |
| `custo` | `implemented` | `.agentcodex/ops/cost-controls-policy.md`, `backend/sentinela.py`, `ops_readiness_dashboard.md` | live usage evidence still pending |
| `compliance` | `implemented` | `.agentcodex/ops/compliance-posture.md`, `.agentcodex/ops/retention-audit-policy.md`, `databricks/unity-catalog-foundation.md` | control validation in real workspace still pending |

## Phase 1 Exit Rule

Phase 1 is not complete until:

- `validacao`, `operacao`, and `deploy` move from `partial` to `implemented`
- the implemented blocks have live Databricks evidence where applicable
- the repo no longer depends on demo-only paths for Phase 1 infrastructure claims

## Update Rule

Update this manifest whenever one of the 14 blocks changes status or receives live evidence.
