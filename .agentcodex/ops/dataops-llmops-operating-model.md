# DataOps And LLMOps Operating Model

## Purpose

Define the minimum operating baseline for DataOps, MLOps, and LLMOps in CoinGeckoAnalytical.

## Scope

- ingestion and medallion pipelines
- governed analytical serving
- AI copilot runtime
- token, cost, and quality observability

## DataOps Baseline

- Bronze, Silver, and Gold layers must have named owners.
- Freshness targets must be defined per dataset family.
- Quality checks must run before Gold promotion for trusted tenant-facing views.
- Schema changes must be tracked through data contracts and lineage.
- Failed or degraded datasets must surface status instead of silently serving stale data.

## MLOps Baseline

- Model-serving endpoints must be versioned.
- Deployment changes must have rollback guidance.
- Evaluation criteria must exist for any model-dependent tenant-facing behavior.
- Production-serving configuration must be separated by environment.

## LLMOps Baseline

- Every copilot route must emit token and cost telemetry.
- Prompt, retrieval, and policy changes must be reviewable.
- Grounded answers must include provenance and freshness metadata.
- Unsupported or risky requests must degrade or refuse explicitly.
- Model selection should follow a documented routing policy.

## Shared Controls

- tenant isolation
- access control
- audit trail
- freshness monitoring
- cost controls
- alerting

## Required Operating Artifacts

- telemetry schema for usage events
- freshness and quality metrics
- model and route policy
- incident and rollback notes
- release verification report
