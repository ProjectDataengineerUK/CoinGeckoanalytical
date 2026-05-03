# DEFINE: CoinGeckoAnalytical

> Validated requirements for `coingeckoanalytical`, rewritten from the refreshed brainstorm.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `coingeckoanalytical` |
| **Date** | `2026-04-30` |
| **Owner** | `operator` |
| **Authoring Role** | `workflow-definer` |
| **Status** | Ready for Design |
| **Clarity Score** | `14/15` |

## Input Classification

| Attribute | Value |
|-----------|-------|
| **Input Type** | `mixed_sources` |
| **Source Artifact(s)** | `Requisitos.pdf`, `context.md`, refreshed brainstorm answers |
| **Brainstorm Source** | `.agentcodex/features/BRAINSTORM_coingeckoanalytical.md` |
| **Preserved Decision** | recreate the prior product almost entirely, but with a new and more mature Databricks-first architecture |

## Problem Statement

The project must recreate the previously envisioned CoinGecko Analytical product as a production-grade, cloud-first, multi-tenant crypto intelligence SaaS. The new version must preserve the ambition of the earlier product almost in full, but replace the prior local open-source stack with a more mature Databricks-first platform that supports broader data sources, stronger governance, stronger operational controls, and a more trustworthy AI-assisted research experience.

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Public self-serve user | Independent researcher, trader, or market enthusiast | Wants fast access to trustworthy crypto insights, rankings, comparisons, and AI-assisted explanations without assembling fragmented tools. |
| Professional analyst | Research analyst, intelligence lead, or strategy user | Needs broad market coverage, governed datasets, repeatable analytical views, and AI assistance with provenance and freshness signals. |
| Institutional team | Fund, desk, enterprise data consumer, or governance-sensitive team | Requires access control, lineage, auditability, operational trust, and dependable AI outputs before using the platform in serious workflows. |

## Goals

What success looks like, prioritized:

| Priority | Goal |
|----------|------|
| **MUST** | Deliver a complete V1 product with dashboard, pipelines, governed analytics, and AI chat as one integrated experience. |
| **MUST** | Recreate the earlier product ambition on a stronger Databricks-first architecture rather than narrowing the product into a lightweight proof of concept. |
| **MUST** | Support self-serve, analyst, and institutional use from the start with multi-tenant boundaries and enterprise-grade controls. |
| **MUST** | Include provenance, freshness, traceability, governance, compliance posture, and access control as first-class V1 requirements. |
| **SHOULD** | Support multiple market-data sources from the beginning, with CoinGecko as one important input but not the only one. |
| **SHOULD** | Deliver Portuguese-first UI and AI responses in V1. |
| **SHOULD** | Provide near-real-time or real-time analytical behavior where technically and economically viable. |
| **COULD** | Add future premium workflows and differentiated institutional experiences without forcing a second core architecture later. |

## Success Criteria

- [ ] The V1 product supports authenticated multi-tenant access for public, analyst, and institutional usage patterns.
- [ ] The V1 includes a complete dashboard experience, governed analytical serving, and AI chat in one coherent product surface.
- [ ] AI answers include provenance, freshness metadata, query or evidence traceability, and confidence context for grounded responses.
- [ ] The platform supports multiple data sources in its design and initial implementation posture, with clear source ownership and quality controls.
- [ ] Governance controls exist for tenant separation, access control, auditability, lineage, and compliance-sensitive operational review.
- [ ] The platform can be demonstrated end to end in a cloud deployment posture with operational observability, secrets handling, and runbook readiness.
- [ ] The product is strong enough to be judged as a real V1 candidate rather than a technical scaffold or internal prototype.

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Dashboard exploration | An authenticated tenant user opens the platform | The user navigates the dashboard experience | The user can explore governed crypto market views, filters, rankings, and comparisons with freshness visibility. |
| AT-002 | Grounded AI answer | An authenticated user asks a market question in natural language | The AI experience returns an answer | The response includes grounded explanation plus provenance, freshness, and evidence context. |
| AT-003 | Portuguese-first product | A Portuguese-speaking user uses dashboard and AI chat flows | The product renders UI and responses | The product behaves in Portuguese consistently for supported V1 flows. |
| AT-004 | Tenant isolation | Two tenants exist with distinct permissions | One tenant user accesses product surfaces | The user cannot access another tenant's protected data, AI context, or audit trails. |
| AT-005 | Freshness enforcement | One core data feed is stale or delayed | A user opens related analytics or asks an affected question | The platform exposes freshness state and does not present stale data as silently current. |
| AT-006 | Governance traceability | An administrator or authorized operator reviews an important AI-assisted answer | The reviewer inspects the audit surface | The answer can be traced to source datasets, evidence or query artifacts, and request metadata. |
| AT-007 | Operational readiness | The platform is evaluated for V1 approval | Operators review observability, controls, and runbooks | The platform exposes meaningful readiness signals rather than relying only on local tests or placeholder assets. |

## Out Of Scope

No meaningful scope cuts were accepted during brainstorm.

This means the `design` phase must treat scope pressure, sequencing, and risk management as explicit concerns rather than assuming a narrow V1.

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Databricks is mandatory as the core platform. | Design must define Databricks-native boundaries for ingestion, ETL, governance, serving, AI, and operations. |
| Product | The product should recreate almost the full ambition of the prior concept. | Design cannot collapse the effort into a small demo without violating the chosen product direction. |
| Security/Compliance | Security, compliance, lineage, governance, access control, and auditability are required from the start. | Design must include identity, authorization, traceability, review surfaces, and controlled data/AI flows early. |
| Operational | The V1 is expected to behave like a serious production candidate, not only a local scaffold. | Design must include observability, runbooks, quality posture, and operational controls as part of the product definition. |
| Data | CoinGecko plus other data sources are in scope from the beginning. | Design must define source mix, source trust model, onboarding strategy, and data ownership. |
| Business | The product serves both self-serve and institutional expectations from day one. | Design must reconcile broad adoption with stronger controls and governance-sensitive workflows. |

## Technical Context

> Essential context for design. This prevents misplaced architecture and false assumptions about maturity.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `custom greenfield monorepo/product structure` | Existing repo contents are partial scaffolding and must not be mistaken for full product completion. |
| **Runtime/Platform** | `Databricks cloud-first multi-tenant SaaS` | Databricks is fixed, but exact product-serving, data, AI, and operational boundaries still need design finalization. |
| **Architecture Pressure** | `full-product ambition with strong controls` | Design must resolve sequencing pressure created by the lack of meaningful YAGNI cuts. |
| **IaC / Resource Impact** | `new resources and new operating surfaces` | Environment separation, secrets, observability, tenancy, and external serving all need explicit design treatment. |
| **Relevant KB Domains** | `lakehouse`, `medallion`, `lakeflow`, `operations` | Design should anchor implementation decisions in these local domains where applicable. |

## Product Scope

The defined V1 includes all of the following as one integrated product:

- public external frontend
- authenticated multi-tenant product access
- governed data ingestion and medallion pipeline posture
- dashboard analytics and comparative market views
- AI chat for market research and explanation
- provenance, freshness, and confidence signaling
- operational observability, alerting posture, and reviewability
- governance, access control, lineage, and auditability surfaces

## Data Contract

> This feature includes multiple source families, governed analytics, and AI evidenceability from the start.

### Source Inventory

| Source | Type | Freshness | Notes |
|--------|------|-----------|-------|
| CoinGecko market data | API | near-real-time where feasible | Mandatory starting source, but not the only intended source |
| Additional market and reference sources | API / feed / partner datasets | TBD in design | Must be explicitly defined rather than hand-waved |
| Derived analytical datasets | Databricks lakehouse tables and views | tiered by layer | Must back dashboards and AI grounding |
| AI retrieval, evidence, and query artifacts | metadata and logs | immediate | Required for trust and audit surfaces |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `asset_id` | `STRING` | required, stable business identifier | No |
| `observed_at` | `TIMESTAMP` | required, freshness anchor | No |
| `metric_name` | `STRING` | required for analytical semantics | No |
| `metric_value` | `DECIMAL` | required where metric is emitted | No |
| `source_system` | `STRING` | required for multi-source traceability | No |
| `tenant_id` | `STRING` | required where access or audit scope is tenant-specific | Potentially sensitive |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Raw ingestion | as close to source availability as feasible | source timestamp vs ingestion timestamp |
| Curated analytics | near-real-time for priority views, defined explicitly in design | pipeline completion and serving lag |
| AI answer evidence | always surfaced at response time | response metadata vs dataset watermark |

### Lineage Requirements

- Lineage is required from source ingestion through curated views, dashboards, and AI-assisted answers.
- Multi-source blending must remain reviewable and attributable.
- Critical AI answers must be traceable to source datasets, freshness state, and request/evidence artifacts.

## Assumptions

Assumptions that could invalidate the design if wrong:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | CoinGecko plus additional sources can be onboarded early enough to satisfy the chosen V1 breadth. | The source strategy or V1 claims would need narrowing despite the brainstorm choice. | [ ] |
| A-002 | A Databricks-first multi-tenant architecture can support the chosen full-product scope at acceptable cost and complexity. | The product may require stricter sequencing or commercial trade-offs. | [ ] |
| A-003 | Portuguese-first release remains appropriate even for the broader user mix. | Localization scope may need to expand sooner. | [ ] |
| A-004 | One V1 can satisfy both self-serve and institutional expectations without splitting the control plane early. | The product may need stronger tier separation sooner than planned. | [ ] |
| A-005 | The project can ship a strong production-candidate V1 without meaningful YAGNI cuts. | Design and build may need explicit phased subplans inside the same V1. | [ ] |

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | The product goal is explicit and ambitious. |
| Users | 3 | User classes and approval posture are clear. |
| Goals | 3 | Product-level goals are strong and aligned to the brainstorm. |
| Success | 3 | Success posture is clear, including operational seriousness. |
| Scope | 2 | Scope is explicit, but intentionally broad and therefore high-risk. |
| **Total** | **14/15** | Ready for design, with risk driven by breadth rather than ambiguity. |

## Open Questions

- Which exact additional sources beyond CoinGecko are mandatory for the first approved V1?
- Which Databricks-native and adjacent managed services anchor ingestion, auth, serving, and observability at launch?
- What exact user journeys must exist on day one for self-serve, analyst, and institutional flows?
- What exact compliance posture is required for the intended user mix in V1?
- What sequencing inside design prevents a “complete V1” from collapsing into an unfinishable plan?

## Architecture Direction

The feature proceeds with the following product direction:

- `Databricks Apps` as the primary product surface — two apps:
  - `cga-analytics`: user-facing — Genie conversational BI controller + multi-agent copilot + dynamic charts
  - `cga-admin`: ops-facing — Sentinela monitoring + access management + cost/token telemetry
- `Databricks` as the mandatory data, analytics, AI, governance, and model-lifecycle platform
- `AI/BI Genie` as the analytical chart controller — generated SQL from Genie drives all dashboard state
- `Mosaic AI Agent Framework` (coded Python orchestrator only, not Agent Bricks) for narrative copilot
- `Sentinela` for observability, surfaced in `cga-admin` only
- External web frontend is not in scope for V1

### Rationale

- Databricks Apps eliminates the need for external web infrastructure, reducing operational surface.
- Genie-as-chart-controller enables conversational BI without hardcoded filter logic.
- The coded multi-agent orchestrator is already built, tested, and deployed — no Agent Bricks needed.
- Two-app separation enforces a clean boundary between product experience and operational review.
- All data, AI, auth, and governance stay in a single workspace — reducing integration complexity.

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | `2026-04-29` | workflow-definer | Initial version |
| 2.0 | `2026-04-30` | workflow-definer | Rewritten from refreshed brainstorm for full-product V1 direction |

## Exit Check

- [x] problem statement is clear and specific
- [x] target users and approver posture are explicit
- [x] goals reflect the refreshed brainstorm
- [x] success criteria are measurable at product level
- [x] acceptance tests are testable
- [x] constraints are explicit
- [x] non-cut scope pressure is made explicit
- [x] assumptions are documented
- [x] technical context is gathered
- [x] clarity score >= 12/15

## Next Step

**Ready for:** `design`, with explicit attention to architecture boundaries, source strategy, sequencing pressure, and complete-V1 feasibility.
