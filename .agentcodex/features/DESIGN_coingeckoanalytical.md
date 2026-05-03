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

The product uses a two-app Databricks-native architecture:

- `cga-analytics` (Databricks App): the primary user-facing product surface — Genie conversational BI controller + coded multi-agent copilot + dynamic chart dashboard.
- `cga-admin` (Databricks App): internal ops surface — Sentinela monitoring, access management, cost/token telemetry, and audit review.
- `Databricks data/AI plane` is the mandatory backbone for ingestion, transformation, governance, analytical serving, AI support, and model lifecycle.
- `Sentinela operations plane` is the operational trust layer surfaced inside `cga-admin`.
- `AI/BI Genie` is the primary analytical query controller — its generated SQL drives all chart state inside `cga-analytics`.
- `Mosaic AI Agent Framework` (coded Python orchestrator, not Agent Bricks) handles narrative copilot reasoning.
- External web frontend is not in scope for V1.

## Core Design Principle

The V1 is intentionally broad, but the architecture must still preserve buildability.

That means the design separates:

- `full V1 product scope`
- `mandatory architectural capabilities`
- `build sequencing inside the same V1`

This is not a reduced-scope MVP design. It is a full-product design with explicit internal sequencing so the team can deliver a serious V1 without mistaking scaffolding for product completion.

## Why This Design

- Databricks Apps eliminates the need to build and operate an external web frontend for V1, collapsing the infrastructure surface.
- Genie as the chart controller creates a conversational BI experience where a single natural-language query updates the entire dashboard — no hardcoded filters or dropdowns needed.
- The coded multi-agent orchestrator (`copilot_orchestrator.py`) is already built and tested — Agent Bricks adds complexity without additional value.
- Two separate apps enforce a clean boundary between product experience (`cga-analytics`) and operational review (`cga-admin`).
- Sentinela remains off the user request path by living exclusively in `cga-admin`.
- All data, AI, governance, and auth remain in a single Databricks workspace — reducing integration surface and operational overhead.

## System Overview

```text
External market APIs (CoinGecko, DefiLlama, GitHub, FRED)
  -> Bronze ingestion and raw landing (Delta Lake)
  -> Silver normalization, enrichment, validation, source harmonization
  -> Gold analytical models, evidence views, metric views
  -> Unity Catalog: governance, permissions, lineage, model lifecycle
  -> Two AI serving paths:
     1. Genie: structured NLQ -> generated SQL -> chart state controller
     2. Coded orchestrator: market + macro + defi agents -> synthesis (complex tier)
  -> cga-analytics Databricks App (primary product surface):
       [Genie Chat Panel] -> SQL result -> [Chart Dashboard re-renders]
       [Copilot Panel]    -> narrative answer with provenance + freshness
  -> cga-admin Databricks App (ops surface):
       Sentinela alerts + pipeline health
       Access management + tenant controls
       Cost/token telemetry + audit review
```

## Product Planes

### 1. Analytics App Plane — `cga-analytics`

- Databricks App serving authenticated users (analysts, traders, institutional teams)
- **Genie Panel** (left): conversational NLQ input → `genie_client.ask_genie()` → `generated_query` SQL → executes on warehouse → updates shared `active_dataset` state → all charts re-render
- **Chart Dashboard** (center): subscribes to `active_dataset` state — market rankings, DeFi TVL, macro indicators, movers
- **Copilot Panel** (right/bottom): narrative chat → tier classification (light/standard/complex) → orchestrator (complex) or direct Mosaic (standard/light) → answer with provenance + freshness badge
- **State architecture**:
  - `genie_active_sql`: SQL string from last Genie response — chart controller
  - `genie_answer_text`: narrative explanation from Genie
  - `copilot_conversation`: message history + tier routing log
  - `selected_assets`: propagates to both Genie context and copilot orchestrator
- Portuguese-first navigation and AI responses
- Freshness watermark and confidence label visible on every answer

### 2. Admin App Plane — `cga-admin`

- Databricks App serving operators and admins only
- **Sentinela Dashboard**: live pipeline alerts, freshness status per source, quality score trend, error backlog
- **Pipeline Health**: ingestion job status (CoinGecko, DefiLlama, GitHub, FRED), last run time, rows ingested
- **Cost & Token Monitor**: spend by model tier (light/standard/complex), by tenant, daily/weekly trends
- **Access Management**: user/tenant provisioning, permission assignments, Unity Catalog group management
- **Audit Trail**: request traces, AI answer provenance, generated queries, source watermarks at answer time
- **Ops Readiness View**: gate status, readiness score, runbook links

### 3. Data And AI Plane

- Multi-source ingestion: CoinGecko, DefiLlama, GitHub Activity, FRED Macro
- Medallion architecture: Bronze → Silver → Gold
- Unity Catalog governance, lineage, and permissions
- Gold metric views for Genie
- Gold evidence views for copilot retrieval
- Unity AI Gateway endpoints: `databricks-gemma-3-12b` (light), `databricks-gpt-oss-120b` (standard), `databricks-qwen3-next-80b-a3b-instruct` (complex)

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

| Request Type | Surface | Primary Path | Reason |
|--------------|---------|--------------|--------|
| KPI lookup, ranking, comparison, filtering | `cga-analytics` | Genie Panel → SQL → chart re-render | governed analytical NLQ over Gold assets; SQL result drives state |
| narrative market interpretation, trend explanation | `cga-analytics` | Copilot Panel → tier router → direct Mosaic (standard/light) | concise reasoning without full orchestration |
| cross-domain deep analysis (multi-asset, macro + DeFi) | `cga-analytics` | Copilot Panel → tier router → multi-agent orchestrator (complex) | requires market + macro + defi domain agents + synthesis |
| pipeline status, alerts, freshness review | `cga-admin` | Sentinela Dashboard | operational trust layer, not on user request path |
| cost/token audit, access management | `cga-admin` | Admin panels | low-volume, ops-only |

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

### Sequence 1. Foundational Backbone — COMPLETE

- medallion pipeline: CoinGecko + DefiLlama + GitHub + FRED ingested to Bronze/Silver/Gold
- Unity Catalog governance and lineage active
- Databricks Asset Bundles CI/CD deployed
- Telemetry baseline (ops landing table, token/cost tracking)

### Sequence 2. Coded Copilot Backend — COMPLETE

- `copilot_orchestrator.py`: market + macro + defi domain agents + synthesis agent
- `model_tier_router.py`: light/standard/complex classification
- `mosaic_copilot_client.py`: Unity AI Gateway 3-tier endpoint resolution
- `databricks_sql_client.py` and `genie_client.py`: DBSQL + Genie REST clients
- 133 backend tests passing

### Sequence 3. Analytics App — NEXT

- `cga-analytics` Databricks App scaffold (Dash or Streamlit)
- Layout: Genie panel + chart dashboard + copilot panel
- Genie state controller: `ask_genie()` → `generated_query` → execute → broadcast to charts
- Chart components: market rankings, DeFi TVL, macro indicators, movers
- Copilot panel wired to `copilot_orchestrator.orchestrate()`
- Freshness and provenance badges on all AI answers
- Portuguese-first UI copy

### Sequence 4. Admin App — NEXT

- `cga-admin` Databricks App scaffold
- Sentinela dashboard: pipeline health, freshness alerts, quality scores
- Cost/token monitor: spend by tier, by tenant, daily trends
- Access management: Unity Catalog group provisioning
- Audit trail: request traces, generated queries, answer provenance

### Sequence 5. Operational Completion

- Sentinela live runtime (continuous monitoring loop)
- Unity Catalog fine-grained access control and tenant isolation
- Runbooks, release gates, compliance review surfaces

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
