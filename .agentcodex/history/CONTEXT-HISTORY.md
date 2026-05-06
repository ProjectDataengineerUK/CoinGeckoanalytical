# Context History

## Purpose

Preserve resumable project context in repo files instead of relying on chat memory only.

## Current State

- project: `CoinGeckoAnalytical`
- status: `live-online`
- active_phase: `ship`
- primary_architecture: `Databricks Apps primary surface + Databricks data/AI plane + sentinela ops plane`
- generated_at: `2026-05-05`

## Canonical Artifacts

- brainstorm: `.agentcodex/features/BRAINSTORM_coingeckoanalytical.md`
- define: `.agentcodex/features/DEFINE_coingeckoanalytical.md`
- design: `.agentcodex/features/DESIGN_coingeckoanalytical.md`
- build: `.agentcodex/features/BUILD_coingeckoanalytical.md`
- architecture image: `docs/assets/coingeckoanalytical-architecture.png`
- architecture doc: `docs/architecture.md`
- current live status handoff: `.agentcodex/reports/status-handoff-2026-05-05.md`
- current project-standard manifest: `.agentcodex/ops/project-standard-status.md`
- current approval status: `.agentcodex/reports/approval-gate-status.md`
- final delivery report: `.agentcodex/reports/final-delivery-report-2026-05-04.md`
- current audit report: `.agentcodex/reports/general-audit-2026-05-05.md`
- agentcodex improvement analysis: `.agentcodex/reports/agentcodex-improvement-analysis-2026-05-05.md`

## Latest Workflow State

- `brainstorm`, `define`, `design`, and `build` completed and reconciled into a live Databricks-native V1 baseline
- architecture pivot finalized: `Databricks Apps` is the primary product surface, replacing the earlier external-frontend posture
- `cga-analytics` and `cga-admin` are both registered in Databricks Asset Bundles and treated as the canonical product/ops surfaces
- 22 jobs now cover Bronze, Silver, Gold, enrichment, MLOps, governance, compliance, and Sentinela operations
- CI structural validation is green and local validation passes: compileall, bundle validation, chain validation, backend tests, databricks tests, and repo tests
- the live baseline is considered online, while future mutations remain approval-gated through `workflow_dispatch`
- security hardening includes SQL input allowlisting, token-cache locking, prompt sanitization, user-id hashing, and Databricks host allowlisting on credentialed clients

## Important Decisions

- `Databricks Apps` is the chosen primary product surface:
  - `cga-analytics` for the user-facing analytics, charts, Genie, and copilot experience
  - `cga-admin` for Sentinela, pipeline health, access control, cost telemetry, and audit review
- `Databricks` remains the backend platform for ingestion, governance, analytics, SQL serving, AI, and model lifecycle
- `AI/BI Genie` handles structured analytical NLQ over governed Gold assets
- `Mosaic AI Agent Framework` plus the coded Python orchestrator handles narrative copilot behavior
- `Sentinela` remains the operations and observability coordination layer
- live environment changes remain operator-approved; the repo does not auto-mutate Databricks or Terraform on push

## Current Validation Snapshot

- `python3 -m compileall backend databricks apps -q`
- `python3 databricks/tools/validate_bundle.py`
- `python3 databricks/tools/validate_market_overview_chain.py`
- `python3 databricks/tools/validate_enrichment_chain.py`
- `python3 -m unittest discover -s backend/tests -p 'test_*.py'`
- `python3 -m unittest discover -s databricks/tests -p 'test_*.py'`
- `python3 -m unittest discover -s repo_tests -p 'test_*.py'`
- total validated tests in the current local sweep: `355`

## Residual Production Hardening Gaps

- notification webhooks from Sentinela to Slack/PagerDuty are still pending
- environment evidence in staging/prod can still be expanded over time
- tenant isolation beyond current row-level controls remains a future-depth item, not a blocker to the current baseline

## Resume Rule

When resuming work, read this file first, then review:

1. `AGENTS.md`
2. `.agentcodex/ops/project-standard-status.md`
3. `.agentcodex/reports/status-handoff-2026-05-05.md`
4. `.agentcodex/reports/general-audit-2026-05-05.md`

## Update Rule

Update this file whenever a major architecture, workflow, or operating-model decision changes.
