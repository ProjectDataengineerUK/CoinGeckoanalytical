# AgentCodex Project Standard Coverage

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- workflow_phase: `build`
- scope: `coverage review of required AgentCodex Project Standard blocks`

## Executive Summary

- implemented: `6/14`
- partial: `7/14`
- missing: `1/14`

The repository already has strong build-time materialization for contracts, Databricks bundle helpers, telemetry, and operational observability. The largest remaining gaps are explicit project-standard packaging, concrete access-control/governance artifacts, live deployment evidence, and a dedicated compliance posture.

## Structural Gap

- `AGENTS.md` references `.agentcodex/features/example-project-standard/`, but that scaffold does not exist in this repository
- there is no single project-standard manifest that marks each required block as implemented, partial, or not applicable

## Coverage Matrix

| Block | Status | Evidence | Gap |
|---|---|---|---|
| `contexto` | `implemented` | `README.md`, `.agentcodex/history/CONTEXT-HISTORY.md`, `BRAINSTORM_`, `DEFINE_` | coverage is spread across files rather than consolidated in a project-standard artifact |
| `arquitetura` | `implemented` | `docs/architecture.md`, `DESIGN_coingeckoanalytical.md` | no issue for build phase |
| `dados` | `implemented` | `databricks/gold_market_views.sql`, `genie_metric_views.sql`, `freshness_quality_baseline.sql` | Bronze and Silver remain mostly design-described rather than executable |
| `governanca` | `partial` | Unity Catalog and governance posture are described in `DESIGN_`, `docs/architecture.md`, `dataops-llmops-operating-model.md` | missing concrete governance model, ownership matrix, approval flow, and policy artifact |
| `lineage` | `partial` | `databricks/gold-data-contracts.md`, `gold_market_views.sql` lineage fields | missing explicit lineage map, lineage verification routine, and operational lineage ownership view |
| `execucao` | `implemented` | `BUILD_coingeckoanalytical.md`, Databricks jobs, backend handoff writers, CI workflow | live Databricks execution evidence is still pending |
| `validacao` | `partial` | backend tests, repo tests, `validate_bundle.py`, helper tests, CI | no live workspace validation evidence, no end-to-end acceptance report |
| `observabilidade` | `implemented` | `backend/sentinela.py`, `telemetry_handoff.py`, `telemetry-observability.sql`, `ops_readiness_dashboard.sql` | dashboard rendering and live ingestion are pending |
| `access control` | `partial` | tenant and policy fields in schemas, design notes, watch-list references | missing explicit RBAC/ACL model, role matrix, admin vs tenant boundary, and secrets/access procedure |
| `data contracts` | `implemented` | `contracts/*.schema.json`, `databricks/gold-data-contracts.md` | contract ownership and lifecycle are not yet centralized |
| `operacao` | `partial` | `sentinela-baseline.md`, `notification_policy.md`, `deployment_runbook.md`, ops dashboard docs | missing incident runbook set, escalation tree, and real operator workflow evidence |
| `deploy` | `partial` | `databricks.yml`, `preflight_databricks_deploy.py`, `deployment_runbook.md`, CI deploy gate | no real workspace deploy evidence, no release artifact proving successful target execution |
| `custo` | `partial` | usage schema cost fields, Sentinela checks, readiness dashboard cost views, design policy notes | missing explicit budget policy, per-plan limits, and operator action thresholds as a dedicated artifact |
| `compliance` | `missing` | only requirement-level mentions in `DEFINE_`, `DESIGN_`, and routing notes | missing dedicated compliance posture, retention/audit policy, regulated-data assumptions, and control mapping |

## Priority Materialization Order

1. create a single project-standard manifest under `.agentcodex/features/` or `.agentcodex/ops/` that tracks all 14 blocks explicitly
2. materialize `access control`, `governanca`, and `compliance` as first-class docs with owners, controls, and decision records
3. materialize `deploy`, `operacao`, and `validacao` with live Databricks execution evidence instead of local-only checks
4. add explicit `lineage` and `custo` operating artifacts instead of leaving them distributed across design and SQL surfaces

## Smallest High-Value Next Docs

1. `.agentcodex/ops/project-standard-status.md`
2. `.agentcodex/ops/access-control-model.md`
3. `.agentcodex/ops/governance-and-ownership.md`
4. `.agentcodex/ops/compliance-posture.md`
5. `.agentcodex/reports/live-workspace-validation-YYYY-MM-DD.md`

## Recommended Acceptance Rule

Do not move to `ship` until:

- every standard block is either `implemented` or explicitly `not applicable`
- `deploy`, `operacao`, and `validacao` have live Databricks evidence
- `access control` and `compliance` are backed by repo-local artifacts instead of design-only statements
