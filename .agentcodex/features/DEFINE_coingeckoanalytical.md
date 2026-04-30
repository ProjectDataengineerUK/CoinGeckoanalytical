# DEFINE: CoinGeckoAnalytical

> Validated requirements for `coingeckoanalytical`.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `coingeckoanalytical` |
| **Date** | `2026-04-29` |
| **Owner** | `operator` |
| **Authoring Role** | `workflow-definer` |
| **Status** | Design completed, ready for Build Planning |
| **Clarity Score** | `13/15` |

## Input Classification

| Attribute | Value |
|-----------|-------|
| **Input Type** | `mixed_sources` |
| **Source Artifact(s)** | `Requisitos.pdf`, `context.md`, operator brainstorm answers |
| **Brainstorm Source** | `.agentcodex/features/BRAINSTORM_coingeckoanalytical.md` |
| **Preserved Decision** | rebuild as a production-ready product from scratch, using the PDF as inspiration only |

## Problem Statement

Public users, analysts, and institutional teams lack a trusted crypto intelligence product that combines governed market data, analytical exploration, and AI-assisted research in one production-grade platform. The project must rebuild the prior CoinGecko-inspired concept as a cloud-first SaaS product on Databricks, with stronger trust, scalability, governance, and Portuguese-first AI-assisted decision support.

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Self-serve market user | Independent trader, researcher, or crypto enthusiast | Can access fragmented dashboards, but struggles to get trusted, explainable, cross-asset insights quickly. |
| Professional analyst | Market analyst or research lead | Needs deeper, fresher, and more reliable analytics than generic dashboards provide, with provenance and repeatability. |
| Institutional team | Fund, desk, or enterprise intelligence consumer | Requires governed data, auditability, access control, and dependable AI-assisted answers before using the product operationally. |

## Goals

What success looks like, prioritized:

| Priority | Goal |
|----------|------|
| **MUST** | Deliver a cloud-first multi-tenant crypto intelligence platform on Databricks with governed lakehouse-backed analytics, interactive dashboard surfaces, and AI chat in one product. |
| **MUST** | Provide trustworthy AI answers with provenance, freshness metadata, and query traceability tied to governed market data. |
| **MUST** | Support broad crypto intelligence coverage, including cross-asset analytics, rankings, movers, correlations, and market context. |
| **SHOULD** | Provide near-real-time to real-time analytical experiences where technically and economically feasible. |
| **SHOULD** | Deliver a Portuguese-first user experience in V1, with architecture prepared for future multilingual expansion. |
| **COULD** | Include differentiated institution-facing workflows and premium analytical depth that expand after the initial flagship release. |

## Success Criteria

- [ ] The V1 product supports authenticated multi-tenant access for self-serve users and team accounts.
- [ ] Core dashboard and AI copilot flows are available in Portuguese for the first release, with localization boundaries defined for future expansion.
- [ ] AI answers include source references, query trace, freshness metadata, and confidence or explanation context for every grounded response.
- [ ] The data platform refreshes core market intelligence datasets on a real-time or near-real-time basis for supported feeds, with documented SLA targets by layer.
- [ ] The product exposes a stable set of production-ready crypto intelligence views covering market rankings, movers, dominance, correlations, and related cross-asset analysis.
- [ ] Governance controls exist for tenant separation, access control, auditability, and lineage on critical datasets.
- [ ] The platform can be demonstrated end-to-end in a cloud deployment with production-oriented observability, secrets handling, and operational runbooks.

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Dashboard exploration | A signed-in tenant user with valid permissions | The user opens the product and selects key market views | The user can explore governed crypto analytics with current metrics, filters, and visual summaries. |
| AT-002 | Grounded AI answer | A signed-in user asks a market question in natural language | The AI copilot generates an answer | The response includes a grounded answer plus provenance, freshness, and query evidence. |
| AT-003 | Portuguese-first interaction | A Portuguese-speaking user opens the product and interacts with dashboards or AI chat | The request is processed | The product returns UI labels, metrics context, and AI answers in Portuguese consistently for supported V1 flows. |
| AT-004 | Tenant isolation | Two tenants exist with separate accounts and permissions | One tenant user accesses dashboards or AI chat | The user can access only their authorized product surface and never another tenant's protected data or audit trail. |
| AT-005 | Freshness enforcement | A core supported feed is delayed or stale beyond SLA | A user queries related insights | The system surfaces freshness status and does not present stale results as current without warning. |
| AT-006 | Governance traceability | An administrator reviews a critical AI-assisted answer | The admin inspects the audit surface | The admin can trace the answer to source dataset versions, query evidence, and request metadata. |

## Out of Scope

Explicitly not included in this feature:

- Portfolio management
- Trading or execution workflows
- Social/community features
- User-generated content ecosystems
- Rebuilding the prior implementation line by line

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | The product must be rebuilt as a new cloud-first SaaS on Databricks rather than a direct port of the previous local Docker architecture. | Design must define Databricks-native platform boundaries, services, and deployment topology. |
| Product | V1 must preserve the flagship end-to-end vision instead of narrowing to a small internal tool. | Scope management must protect the core differentiated experience without losing production viability. |
| Security/Compliance | Trust, lineage, access control, and auditability are required from the start. | Design must include identity, authorization, observability, and governed data/AI flows early. |
| Operational | Real-time or near-real-time experiences are expected where possible. | Architecture must define freshness tiers, streaming boundaries, and graceful degradation paths. |
| Business | The product must work for self-serve adoption while remaining extensible for enterprise expansion. | Design must balance multi-tenant SaaS simplicity with enterprise controls and premium plan boundaries. |

## Technical Context

> Essential context for design. This prevents misplaced files and missed infrastructure work.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `custom path (greenfield monorepo/product structure to be defined in design)` | The current repo is effectively empty aside from AgentCodex artifacts. |
| **KB Domains** | `lakehouse`, `medallion`, `lakeflow`, `operations` | Design should use these patterns as the nearest local knowledge base for Databricks platform and data architecture. |
| **IaC Impact** | `new resources` | A new cloud environment, tenancy model, secrets, observability, and data services will be required. |
| **Runtime/Platform** | `Databricks cloud-first multi-tenant SaaS` | Databricks is fixed; the design still needs to choose supporting services, serving pattern, and control boundaries. |

## Data Contract

> This feature includes data pipelines, analytics serving, freshness SLAs, lineage, and governed AI access to analytical data.

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| CoinGecko market data | API | TBD during design; expected high-cardinality market snapshots and time series | real-time or near-real-time where feasible | Product platform team |
| Derived analytical datasets | Databricks lakehouse tables/views | TBD during design; depends on modeled assets, exchanges, and history depth | tiered by layer | Product platform team |
| AI retrieval/query evidence | metadata and query logs | proportional to AI/chat traffic | immediate | Product platform team |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `asset_id` | `STRING` | not null, stable business key | No |
| `observed_at` | `TIMESTAMP` | not null, freshness anchor | No |
| `metric_name` | `STRING` | not null | No |
| `metric_value` | `DECIMAL` | not null where metric is emitted | No |
| `tenant_id` | `STRING` | required for protected product data and audit surfaces | Potentially sensitive |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Raw / ingestion | as close to source availability as feasible; target defined per feed in design | source timestamp vs ingestion timestamp |
| Curated analytics | near-real-time for key market intelligence views; batch fallback allowed for secondary views | pipeline completion and serving lag |
| AI answer evidence | freshness displayed at response time | response metadata vs dataset watermark |

### Completeness Metrics

- Critical market datasets must publish completeness checks and freshness status before being exposed as trusted intelligence.
- Tenant-facing analytical views must detect and surface degraded or partial data instead of silently presenting missing coverage.

### Lineage Requirements

- Lineage is required from source ingestion through curated analytical views used by dashboards and AI responses.
- Critical AI answers must be traceable to dataset versions, query artifacts, and freshness metadata.
- Audit surfaces must support impact analysis for schema or model changes affecting tenant-facing intelligence.

## Assumptions

Assumptions that could invalidate the design if wrong:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | CoinGecko or equivalent market data sources can support the breadth and freshness required for V1. | The scope or provider strategy would need revision, including secondary data sources. | [ ] |
| A-002 | A Databricks-first multi-tenant architecture can deliver the intended AI + analytics experience within acceptable cost bounds. | The tenancy, freshness, or AI interaction model may need narrowing. | [ ] |
| A-003 | Portuguese-first release is sufficient for V1 adoption before multilingual expansion. | Localization may need to be accelerated earlier than planned. | [ ] |
| A-004 | Public self-serve and enterprise expansion can share one product core without conflicting requirements in V1. | Separate product tiers or control planes may be needed earlier. | [ ] |
| A-005 | Real-time or near-real-time expectations are necessary for the core differentiated value. | A more tiered freshness strategy may be sufficient and cheaper. | [ ] |

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Clear problem and product direction were established in the brainstorm. |
| Users | 3 | Primary user classes and pain points are explicit. |
| Goals | 3 | Prioritized goals are clear and aligned with the selected product position. |
| Success | 2 | Success criteria are measurable at a product level, but final SLA numbers and target thresholds remain for design. |
| Scope | 2 | Boundaries are explicit, but cloud vendor, exact data providers, and exact V1 cuts remain open. |
| **Total** | **13/15** | Ready to move into design with targeted open questions carried forward. |

## Open Questions

- Which exact Databricks-native and adjacent managed services should anchor ingestion, serving, auth, and observability at V1 launch versus later hardening?
- What exact data provider mix is required beyond CoinGecko to satisfy breadth, freshness, and reliability goals?
- What are the exact Portuguese-first UX and content boundaries for V1?
- Which user journeys are mandatory for V1 dashboard exploration versus later institutional expansion?
- What concrete SLA and latency targets are commercially and financially viable for V1?

## Architecture Direction

The feature will proceed with a split AI architecture rather than one generic agent layer:

- `AI/BI Genie` for natural-language analytics over governed Gold tables, views, and metric views in Unity Catalog.
- `External web frontend` as the main tenant-facing product experience layer for the public SaaS surface.
- `Databricks Apps` only for internal operational tools, admin surfaces, premium internal workflows, or rapid prototypes where platform proximity matters more than serving-cost efficiency.
- `Mosaic AI Agent Framework` as the primary coded copilot for market-intelligence workflows that need custom orchestration, provenance, guardrails, and response policies.
- `Agent Bricks` only as an optional accelerator for bounded subcases or prototyping, not as the foundation of the product.

### Rationale

- Genie is the most direct fit for governed NLQ over structured lakehouse analytics.
- A public SaaS frontend should avoid paying Databricks app runtime costs for high-volume lightweight web traffic when cheaper external web serving is sufficient.
- The primary copilot requires custom product behavior, explainability, provenance, and business rules that should live in code.
- Agent Bricks remains useful for selective acceleration, but its beta posture and operational constraints make it a poor default foundation for the core product.
- This split keeps analytical Q&A simple where the platform already provides leverage, reserves custom agent engineering for the differentiated user experience, and keeps public web serving cost-optimized.

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | `2026-04-29` | workflow-definer | Initial version |

## Exit Check

- [x] problem statement is clear and specific
- [x] at least one user persona has a pain point
- [x] goals use MoSCoW priorities
- [x] success criteria are measurable
- [x] acceptance tests are testable
- [x] constraints are explicit
- [x] out of scope is explicit
- [x] assumptions documented with impact if wrong
- [x] KB domains identified for design
- [x] technical context gathered
- [x] clarity score >= 12/15

## Next Step

**Ready for:** `build planning` using `.agentcodex/features/DESIGN_coingeckoanalytical.md` as the implementation baseline.
