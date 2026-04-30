# Design Architecture Decision Report

- date: `2026-04-29`
- feature: `coingeckoanalytical`
- scope: `define update + initial design artifact`

## Changes Recorded

- updated `.agentcodex/features/DEFINE_coingeckoanalytical.md`
- created `.agentcodex/features/DESIGN_coingeckoanalytical.md`

## Decision Summary

- `AI/BI Genie` is the default path for governed analytical NLQ on structured Gold data.
- `External web frontend` is the default product experience layer for the public SaaS surface.
- `Mosaic AI Agent Framework` is the default coded copilot foundation.
- `Databricks Apps` is limited to internal/admin workflows and rapid platform-native prototypes.
- `Agent Bricks` is limited to optional experiments and bounded accelerators.

## Verification

- Verified the repo had no existing `design` artifact before creation.
- Verified the `define` artifact already established Databricks as the mandatory platform direction.
- Verified the new design includes `observabilidade`, `custo`, `governanca`, `lineage`, `access control`, and `data contracts` coverage at design level.

## Follow-up

- materialize build plan and delivery slices
- define telemetry schema for token and cost tracking
- define Gold views and metric views for first Genie use cases
- define the external frontend and backend-for-frontend boundary
