# Context History

## Purpose

Preserve resumable project context in repo files instead of relying on chat memory only.

## Current State

- project: `CoinGeckoAnalytical`
- status: `pre-build`
- active_phase: `design`
- primary_architecture: `external frontend + Databricks data/AI plane + sentinela ops plane`
- generated_at: `2026-04-30`

## Canonical Artifacts

- brainstorm: `.agentcodex/features/BRAINSTORM_coingeckoanalytical.md`
- define: `.agentcodex/features/DEFINE_coingeckoanalytical.md`
- design: `.agentcodex/features/DESIGN_coingeckoanalytical.md`
- architecture image: `docs/assets/coingeckoanalytical-architecture.png`
- architecture doc: `docs/architecture.md`
- routing matrix: `.agentcodex/reports/specialist-routing-matrix-2026-04-29.md`

## Important Decisions

- public SaaS surface uses `external web frontend`
- `Databricks` is the backend platform for data, governance, analytics, AI, and model versioning
- `AI/BI Genie` handles structured analytical NLQ
- `Mosaic AI Agent Framework` handles the main market copilot
- `Sentinela` handles multi-agent coordination and observability
- `Databricks Apps` is not the primary public frontend
- initial source of truth for market data is `CoinGecko API`
- current architecture image is the detailed enterprise diagram in `docs/assets/coingeckoanalytical-architecture.png`

## Open Gaps

- build plan
- project-standard materialization
- DataOps / LLMOps operating baseline
- sentinela baseline
- daily flow
- history update routine

## Resume Rule

When resuming work, read this file first, then review:

1. `.agentcodex/features/DESIGN_coingeckoanalytical.md`
2. `.agentcodex/reports/specialist-routing-matrix-2026-04-29.md`
3. `CLAUDE.md`

## Update Rule

Update this file whenever a major architecture, workflow, or operating-model decision changes.
