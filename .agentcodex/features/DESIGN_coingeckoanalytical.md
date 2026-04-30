# DESIGN: CoinGeckoAnalytical

> Target design for `coingeckoanalytical`, rewritten from the refreshed define for a complete-V1 product direction.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `coingeckoanalytical` |
| **Date** | `2026-04-30` |
| **Owner** | `operator` |
| **Authoring Role** | `workflow-designer` |
| **Status** | Ready for Build Planning |
| **Baseline Input** | `.agentcodex/features/DEFINE_coingeckoanalytical.md` |

## Design Decision

The product uses a three-plane architecture designed to support a broad V1 without pretending that every subsystem must be implemented simultaneously:

- `External web frontend` is the public tenant-facing product surface.
- `Databricks data/AI plane` is the mandatory backbone for ingestion, transformation, governance, analytical serving, AI support, and model lifecycle.
- `Sentinela operations plane` is the operational trust layer for freshness, quality, cost, token, lineage, alert, and audit interpretation.
- `AI/BI Genie` is the primary path for governed structured analytical natural-language querying.
- `Mosaic AI Agent Framework` is the primary coded market copilot path for narrative reasoning, comparisons, and guided analysis.
- `Databricks Apps` are reserved for internal/admin and low-volume operational surfaces.

## Core Design Principle

The V1 is intentionally broad, but the architecture must still preserve buildability.

That means the design separates:

- `full V1 product scope`
- `mandatory architectural capabilities`
- `build sequencing inside the same V1`

This is not a reduced-scope MVP design. It is a full-product design with explicit internal sequencing so the team can deliver a serious V1 without mistaking scaffolding for product completion.

## Why This Design

- The product must preserve the ambition of the prior concept while upgrading maturity and control surfaces.
- Databricks remains the right control plane for medallion data, governed analytics, AI support, model lifecycle, and operational review.
- A public external frontend preserves cost efficiency and keeps the product surface decoupled from workspace-bound runtime costs.
- `Genie` is the lowest-friction path for governed analytical NLQ over structured Gold assets.
- The flagship market copilot still requires coded orchestration, retrieval, provenance, policy handling, and answer shaping that should remain in code.
- Sentinela must remain off the public request path so it can observe, interpret, and coordinate operations without becoming a latency dependency.

## System Overview

```text
External market APIs and reference sources
  -> Bronze ingestion and raw landing
  -> Silver normalization, enrichment, validation, and source harmonization
  -> Gold analytical models, evidence views, and governed metric views
  -> Unity Catalog governance, permissions, lineage, discovery, and model lifecycle
  -> Two serving paths:
     1. Genie for structured governed analytical Q&A
     2. Agent Framework + retrieval + model serving for the coded copilot
  -> Backend-for-frontend / governed serving APIs
  -> External web frontend for dashboard and chat experiences
  -> Sentinela operations plane for observability, readiness, and audit interpretation
  -> Databricks Apps only for internal/admin workflows
```

## Product Planes

### 1. Experience Plane

- Public external web frontend
- Authenticated multi-tenant access
- Portuguese-first navigation and copy
- Dashboard exploration
- AI chat and guided research
- Freshness, provenance, and confidence surfaced to the user

### 2. Data And AI Plane

- Multi-source ingestion with CoinGecko included from day one
- Medallion architecture: Bronze, Silver, Gold
- Unity Catalog governance and lineage
- Gold analytical views for dashboard and Genie
- Evidence views and retrieval surfaces for the coded copilot
- Model serving, route policy, and usage telemetry

### 3. Operations Plane

- Sentinela signal interpretation
- Freshness, quality, and completeness monitoring
- Cost and token monitoring
- Readiness and release gate interpretation
- Audit and review surfaces
- Internal/admin-only operational UX

## Major Components

### 1. Source Ingestion Layer

- `CoinGecko` is a mandatory starting source.
- Additional market/reference sources are part of the design baseline, not future wish-list items.
- Each source must declare:
  - owner
  - freshness expectation
  - ingestion strategy
  - trust/quality posture
  - lineage identity

### 2. Bronze Layer

- Raw source snapshots or event streams
- Provider metadata
- Source timestamps preserved
- Minimal transformation beyond safe landing and schema conformance

### 3. Silver Layer

- Cross-source normalization
- Canonical asset and market dimensions
- Enrichment and harmonization
- Quality checks and exception surfacing
- Intermediate views required for Gold and AI evidenceability

### 4. Gold Layer

- Tenant-facing analytical marts and views
- Ranking, movers, dominance, comparison, market context, and evidence views
- Metric views designed for Genie
- User-facing freshness and quality posture tied to served assets

### 5. Backend-For-Frontend Layer

- Auth and tenant context propagation
- Routing between dashboard retrieval, Genie, and copilot
- User-facing response normalization
- Policy enforcement
- Audit and telemetry emission

### 6. Analytical NLQ Path

- `Genie` handles KPI-style, ranking, filtering, comparison, and structured analytical questions.
- It must operate only on governed Gold assets and metric views.
- Its output must remain clearly labeled as analytical and distinct from the narrative copilot surface.

### 7. Coded Copilot Path

- `Mosaic AI Agent Framework` handles narrative reasoning, contextual market interpretation, guided analysis, and source-backed explanation.
- The copilot must:
  - classify intent
  - decide route/tool usage
  - retrieve governed evidence
  - produce provenance
  - surface freshness
  - enforce policy
  - emit token/cost telemetry

### 8. Sentinela Operations Plane

- Watches data freshness, data quality, route health, cost, tokens, backlog, errors, and compliance-sensitive anomalies.
- Produces readiness summaries and alert interpretations.
- Supports operational review without becoming part of the public serving path.

## Request Routing

| Request Type | Primary Path | Reason |
|--------------|--------------|--------|
| dashboard browse, ranking, comparison, market filters | `frontend + backend + Gold APIs/views` | deterministic rendering and cost-efficient public serving |
| governed structured analytical NLQ | `Genie` | best fit for repeatable analytics on governed Gold assets |
| narrative market interpretation and guided research | `Agent Framework` | requires coded orchestration, evidence handling, and answer policy |
| internal audit and operator review | `Databricks Apps` + ops plane | good fit for low-volume internal workflows |

## Interface Contracts

### Frontend -> Backend Routing

Required request fields:

- `tenant_id`
- `user_id`
- `session_id`
- `request_id`
- `locale`
- `channel`
- `request_type_hint`
- `message_text`
- `selected_assets`
- `time_range`
- `ui_context`

Rules:

- the frontend must never call workspace-bound AI or analytical services directly
- the backend decides dashboard retrieval versus Genie versus copilot
- the backend attaches authorization, audit, and route policy context

### Backend -> Genie

Required request fields:

- `request_id`
- `tenant_id`
- `user_id`
- `workspace_context`
- `semantic_scope`
- `question_text`
- `filters`
- `time_range`
- `response_format`

Required response fields:

- `request_id`
- `answer_text`
- `generated_query` when available
- `source_assets`
- `freshness_watermark`
- `execution_status`
- `latency_ms`

Rules:

- Genie answers must stay inside governed analytical scope
- structured outputs must be user-visible as analytical answers
- overflow from structured scope must be routed to the coded copilot

### Backend -> Copilot

Required request fields:

- `request_id`
- `tenant_id`
- `user_id`
- `conversation_id`
- `message_text`
- `conversation_summary`
- `retrieval_scope`
- `selected_assets`
- `time_range`
- `policy_context`
- `locale`

Required response fields:

- `request_id`
- `answer_text`
- `answer_type`
- `citations`
- `evidence_asset_ids`
- `freshness_watermark`
- `confidence_label`
- `followup_actions`
- `latency_ms`
- `token_usage`

Rules:

- provenance is mandatory for grounded answers
- unsupported or risky requests must be refused or degraded explicitly
- V1 defaults to Portuguese output unless intentionally overridden

### Frontend Rendering Envelope

Shared user-facing fields:

- `request_id`
- `surface_type`
- `title`
- `body`
- `citations`
- `freshness`
- `confidence`
- `actions`
- `warnings`

Rules:

- `analytics_answer` must emphasize governed structured output
- `copilot_answer` must emphasize narrative interpretation plus evidence
- `warnings` must surface stale data, partial coverage, policy limits, or degraded mode

## Data Strategy

### Multi-Source Model

The product must not assume a single-provider future.

Design obligations:

- each source has a traceable `source_system`
- Silver harmonization resolves provider differences explicitly
- Gold views expose source-aware traceability when needed
- AI responses and audit surfaces can point back to source identity

### Freshness Model

- `tier_a`: critical market views and high-priority operational intelligence
- `tier_b`: lower-priority comparative or enrichment surfaces
- user-facing freshness watermark required on served analytics and grounded AI answers

### Quality Model

- null and key integrity checks
- duplicate suppression
- bounded numeric sanity checks
- source completeness checks
- degraded-state surfacing rather than silent serving

## Governance, Compliance, And Trust

- Unity Catalog is the mandatory governance plane
- tenant isolation applies to dashboards, AI flows, telemetry, and audit surfaces
- sensitive logs and traces are access-controlled and retained under policy
- access to admin audit review is separate from end-user product access
- compliance posture must be explicit in design, not implied by generic governance language
- AI trust requires provenance, freshness, confidence signaling, and request traceability

## Security And Access Control

- external users authenticate through the public product surface, not directly against workspace internals
- workforce and admin access use centralized identity and stronger administrative controls
- secret storage must remain managed and externalized from app code
- policy context must be attached before analytical or AI execution
- tenant-aware authorization boundaries must exist across request routing, served assets, and audit review

## Observability

### Product Metrics

- daily active users
- successful dashboard sessions
- AI answer success rate
- stale-answer suppression rate

### Data Metrics

- ingestion lag
- Gold publish latency
- completeness score
- quality rule pass rate

### AI Metrics

- tokens by tenant
- tokens by request type
- cost by tenant
- grounded-answer rate
- citation coverage rate
- reviewed answer quality outcomes

### Operational Metrics

- alert backlog
- route health
- release readiness posture
- failed or degraded source publishes
- compliance-sensitive anomaly count

## Deployment Shape

- Databricks environments separated as `dev`, `staging`, `prod`
- public frontend deployed outside Databricks on cost-efficient infrastructure
- backend routing and serving boundaries deployed with environment-aware configuration
- data, AI, and operational assets promoted with controlled release flow
- rollback must exist for frontend, backend, serving endpoints, and data model changes

## Internal Sequencing Inside The Same V1

Because no meaningful scope cuts were accepted, the design must define execution order without redefining the product.

### Sequence 1. Foundational Backbone

- source strategy
- medallion contracts
- auth and tenant model
- governance and access control baseline
- telemetry baseline

### Sequence 2. Public Analytical Surface

- dashboard-serving Gold views
- frontend shell
- backend retrieval APIs
- user-facing freshness posture

### Sequence 3. Governed Analytical NLQ

- Genie metric views
- governed analytical routing
- NLQ response labeling and evidence posture

### Sequence 4. Coded Copilot

- evidence views
- retrieval scope
- narrative copilot orchestration
- provenance and trust metadata

### Sequence 5. Operational Completion

- Sentinela readiness surfaces
- admin/audit review flows
- runbooks, alerts, and release interpretation

This sequencing preserves the chosen full-product V1 while still preventing random build activity.

## Build Gating Rules

The build must not be considered healthy unless:

- the product can be traced back to this design rather than to isolated scaffolding
- dashboard, Genie, and copilot paths all map to governed data contracts
- trust metadata is visible to users, not only to internal schemas
- operational readiness is treated as product behavior, not as optional postscript

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Full-product V1 scope overwhelms execution | The team creates scaffolding without closing product flows | enforce internal sequencing and route every build activity to a named product capability |
| Multi-source onboarding is slower than planned | Product breadth claims become untrustworthy | define mandatory versus follow-on sources explicitly in build planning |
| Copilot cost becomes too high | Product economics and latency degrade | enforce route policy, retrieval limits, and Genie redirection |
| Governance/compliance controls slow delivery | schedule pressure increases | treat controls as architecture primitives, not bolt-ons |
| Public/frontend and Databricks/backend boundaries drift | security and cost posture degrade | keep BFF and route contracts explicit and reviewable |

## Verification Plan

- verify every critical user journey maps to exactly one primary serving path
- verify all project-standard blocks are represented in the design
- verify token/cost instrumentation is explicit before build
- verify tenant isolation applies across dashboard, AI, telemetry, and audit surfaces
- verify the internal V1 sequencing is clear enough to avoid fake progress

## Exit Check

- [x] architecture direction selected
- [x] public experience layer selected
- [x] analytical NLQ path selected
- [x] coded copilot path selected
- [x] governance, compliance, and trust posture included
- [x] token/cost strategy included
- [x] internal sequencing for a broad V1 defined
- [x] build gating logic defined

## Next Step

**Ready for:** `build planning`, but only if the build plan follows the internal sequencing above and ties each build slice to concrete product behavior.
