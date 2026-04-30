# Specialist Routing Matrix

- date: `2026-04-29`
- project: `CoinGeckoAnalytical`
- purpose: `map AgentCodex specialists, knowledge domains, and expected deliverables by workflow phase`

## Summary

The project should not try to activate every specialist at once. It should route work by phase and by concrete decision surface.

Primary specialist set for this project:

- `workflow-designer`
- `databricks-architect`
- `mosaic-ai-engineer`
- `lakeflow-architect`
- `data-contracts-engineer`
- `data-observability-engineer`
- `data-governance-architect`
- `sentinel-interpreter`

## Phase Routing

| Phase | Primary Specialists | Supporting KB / Domains | Main Deliverables |
|------|----------------------|--------------------------|-------------------|
| `brainstorm` | `workflow-brainstormer`, `databricks-architect` | Databricks platform, governance, cost | product direction, platform choice, scope boundaries |
| `define` | `workflow-definer`, `databricks-architect`, `data-governance-architect` | Databricks, governance, lineage, cost | requirements, acceptance tests, provider assumptions, trust model |
| `design` | `workflow-designer`, `mosaic-ai-engineer`, `lakeflow-architect`, `data-contracts-engineer`, `data-observability-engineer` | Genie, Agent Framework, Lakeflow, data contracts, observability | target architecture, contracts, routing, telemetry, deployment shape |
| `build` | `workflow-builder`, `spark-engineer`, `lakeflow-pipeline-builder`, `mosaic-ai-engineer`, `data-contracts-engineer` | pipelines, serving, telemetry, quality | implementation slices, schemas, APIs, telemetry events, quality controls |
| `ship` | `workflow-shipper`, `data-observability-engineer`, `sentinel-interpreter`, `data-governance-architect` | observability, cost, operations, compliance | release checks, runbooks, alerts, audit evidence, production readiness |

## Specialist Detail

### workflow-designer

- use for: architecture synthesis, workflow control, and design artifact quality
- expected outputs:
  - `DEFINE`
  - `DESIGN`
  - build planning structure

### databricks-architect

- use for: Databricks-native topology, Unity Catalog boundaries, serving choices, and CI/CD shape
- expected outputs:
  - workspace and environment strategy
  - Unity Catalog model
  - Databricks Apps posture
  - DABs and deployment guidance

### mosaic-ai-engineer

- use for: copilot architecture, model serving, provenance, and guardrail design
- expected outputs:
  - copilot request/response contract
  - retrieval/evidence model
  - token telemetry requirements

### lakeflow-architect

- use for: ingestion, medallion flow, streaming or micro-batch decisions, and pipeline orchestration
- expected outputs:
  - Bronze/Silver/Gold pipeline shape
  - freshness tiers
  - ingestion and transformation boundaries

### data-contracts-engineer

- use for: interface and dataset contracts across frontend, Genie, copilot, and Gold assets
- expected outputs:
  - payload schemas
  - usage telemetry schema
  - analytical dataset contracts

### data-observability-engineer

- use for: freshness, quality, token/cost observability, dashboards, alerts, and operational metrics
- expected outputs:
  - metrics definition
  - alerting design
  - token/cost instrumentation model

### data-governance-architect

- use for: access control, lineage, policy boundaries, auditability, and compliance posture
- expected outputs:
  - tenant isolation model
  - governance controls
  - audit trail requirements

### sentinel-interpreter

- use for: operational signal interpretation, anomaly review, and reliability posture later in the lifecycle
- expected outputs:
  - sentinel event model
  - failure interpretation rules
  - production monitoring guidance

## Recommended KB Focus

Prioritize these AgentCodex knowledge areas when continuing the project:

- Databricks platform
- Lakeflow
- governance
- lineage
- data contracts
- observability
- cost

## Current Recommendation

For the current repo state, the most relevant active specialists are:

1. `workflow-designer`
2. `databricks-architect`
3. `mosaic-ai-engineer`
4. `lakeflow-architect`
5. `data-contracts-engineer`
6. `data-observability-engineer`

`sentinel-interpreter` should become more active after implementation starts and operational telemetry exists.
