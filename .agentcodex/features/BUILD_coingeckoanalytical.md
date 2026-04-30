# BUILD: CoinGeckoAnalytical

> Build planning artifact for `coingeckoanalytical`, derived from the approved design.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `coingeckoanalytical` |
| **Date** | `2026-04-30` |
| **Owner** | `operator` |
| **Authoring Role** | `workflow-builder` |
| **Status** | Build planning in progress |
| **Baseline Input** | `.agentcodex/features/DESIGN_coingeckoanalytical.md` |

## Build Goal

Convert the current architecture into executable implementation slices that preserve:

- public frontend cost optimization
- Databricks-governed backend boundaries
- structured analytics via `Genie`
- coded copilot behavior via `Mosaic AI Agent Framework`
- token, cost, freshness, and audit telemetry from the beginning

## Implementation Strategy

Build in thin vertical slices instead of trying to stand up the entire platform at once.

Priority order:

1. foundational contracts and repo structure
2. Gold analytical serving baseline
3. public frontend shell and BFF boundary
4. copilot slice with telemetry
5. observability, sentinela, and operations hardening

## Workstreams

### WS1. Foundation And Repo Structure

Scope:

- establish project directories for frontend, backend, and Databricks assets
- define environment boundaries: `dev`, `staging`, `prod`
- define CI/CD baseline and deployment ownership

Outputs:

- target repository layout
- deployment boundary notes
- initial config and environment contract

### WS2. Data Platform Baseline

Scope:

- define Bronze, Silver, and first Gold analytical assets
- define first metric views for `Genie`
- define freshness and quality checks for trusted Gold serving

Outputs:

- first dataset inventory
- Gold view contract set
- freshness and quality acceptance rules

### WS3. Frontend And Routing Baseline

Scope:

- define external frontend shell
- define backend-for-frontend/API boundary
- define routing from frontend requests to `Genie` or copilot

Outputs:

- frontend shell contract
- BFF/API request contract
- request routing rules

### WS4. Copilot Baseline

Scope:

- implement first coded copilot slice
- connect retrieval/evidence model
- emit provenance, confidence, freshness, and token telemetry

Outputs:

- copilot request and response schema
- telemetry event schema
- first grounded-answer acceptance criteria

### WS5. Operations And Sentinela

Scope:

- define initial dashboards and alerts
- define sentinela event interpretation
- define release-readiness checks for cost, freshness, and access-control posture

Outputs:

- alert catalog
- sentinela signal catalog
- ship-readiness checklist

## Initial Build Slices

### Slice 1

`contracts-first baseline`

- create payload schemas for:
  - frontend -> routing
  - routing -> Genie
  - routing -> copilot
  - normalized response envelope
  - usage telemetry event

Why first:

- every later implementation depends on stable contracts

### Slice 2

`Gold analytics baseline`

- define first market views:
  - market rankings
  - top movers
  - dominance
  - cross-asset comparison baseline

Why second:

- `Genie` and dashboard serving need governed analytical assets before UI and copilot can be trusted

### Slice 3

`public frontend shell`

- define the external frontend app skeleton
- define authentication and tenant context boundary
- define dashboard and chat entry points
- define BFF/routing boundary to `Genie` versus copilot
- keep public traffic and cache outside Databricks

### Slice 4

`copilot MVP slice`

- implement one grounded market-answer workflow
- include provenance, freshness, and token-cost telemetry
- keep the routing decision explicit between Genie and copilot

### Slice 5

`sentinela and operations spine`

- define operational signals and multi-agent coordination
- define freshness, quality, cost, and audit reporting
- define release-readiness checks for public serving and Databricks assets
- include route-specific readiness thresholds and escalation policies

## Verification Requirements

- each slice must produce a durable report under `.agentcodex/reports/`
- no slice is complete without explicit verification notes
- token and cost implications must be recorded when AI behavior is added
- access control and tenant isolation cannot be deferred out of user-facing slices

## Immediate Next Action

Expand the implemented slices into executable Databricks assets and telemetry wiring, then validate and deploy the Databricks bundle that schedules ingestion and refresh jobs from the backend telemetry handoff file.
