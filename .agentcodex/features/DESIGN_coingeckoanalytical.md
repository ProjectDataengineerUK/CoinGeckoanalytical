# DESIGN: CoinGeckoAnalytical

> Target design for `coingeckoanalytical` based on the approved Databricks-first product direction.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `coingeckoanalytical` |
| **Date** | `2026-04-29` |
| **Owner** | `operator` |
| **Authoring Role** | `workflow-designer` |
| **Status** | Draft ready for build planning |
| **Baseline Input** | `.agentcodex/features/DEFINE_coingeckoanalytical.md` |

## Design Decision

The product will use a three-plane architecture with split AI serving paths:

- `External web frontend` for the public tenant-facing product surface.
- `Databricks data/AI plane` for ingestion, ETL, governance, Gold assets, Genie, Vector Search, and model lifecycle.
- `Sentinela operations plane` for multi-agent coordination, freshness, quality, cost, tokens, and audit observability.
- `AI/BI Genie` for governed analytical natural-language querying on structured Gold data.
- `Mosaic AI Agent Framework` for the main market copilot with custom orchestration, provenance, and response policy enforcement.
- `Databricks Apps` only for internal operational tools, admin experiences, premium internal workflows, or rapid platform-native prototypes.
- `Agent Bricks` only for selective experiments or bounded accelerators, not as the main platform dependency.

## Why This Design

- `Genie` fits structured analytics over Unity Catalog assets better than a custom agent for every analytical question.
- The flagship copilot needs custom prompt orchestration, tool routing, provenance, confidence policy, and answer shaping that should remain in code.
- A public web frontend can be served much more cheaply than keeping the main product UX on hourly Databricks app runtime.
- Databricks remains the right backend control plane for data, governed analytics, model serving, and AI orchestration.
- Sentinela belongs in the operations plane, not in the public request path, so it can monitor and coordinate without inflating latency.
- `Agent Bricks` can speed up a narrow proof of concept, but its beta posture makes it unsuitable as the core production abstraction.

## System Overview

```text
External market APIs
  -> Bronze ingestion
  -> Silver normalization and quality
  -> Gold analytical models and metric views
  -> Unity Catalog governance and lineage
  -> Two serving paths:
     1. Genie for governed analytical NLQ
     2. Agent Framework + Model Serving + retrieval/evidence for the copilot
  -> Backend APIs / governed serving layer
  -> External web frontend for dashboard and chat experiences
  -> Sentinela operations plane for observability and multi-agent coordination
  -> Databricks Apps only for internal/admin product surfaces
```

## Major Components

### 1. Data Platform

- Bronze: raw market events, snapshots, reference assets, and provider metadata.
- Silver: normalized entities, cleaned timeseries, conformed dimensions, quality-checked datasets.
- Gold: tenant-facing analytical marts, market ranking views, movers, correlations, dominance, and AI-ready evidence views.
- Unity Catalog: central governance plane for schemas, permissions, lineage, discovery, audit support, and model versioning.

### 2. Ingestion and Processing

- Prefer Databricks-native ingestion and orchestration patterns.
- Use streaming or micro-batch ingestion for high-value freshness-sensitive feeds.
- Use scheduled batch for lower-priority enrichment datasets.
- Publish freshness watermarks and completeness status per served dataset.

### 3. Product Experience

- An `external web frontend` hosts the authenticated public tenant-facing product.
- The app exposes two user entry paths:
  - dashboard exploration for charts, rankings, filters, and drilldowns
  - AI copilot for market questions, comparisons, explanations, and guided analysis
- Portuguese is the default language for UI copy and AI responses in V1.
- Recommended shape:
  - static or edge-served frontend for low-cost public traffic
  - backend-for-frontend or API layer to call Databricks-backed services securely
  - `Databricks Apps` reserved for admin/internal workflows that benefit from native workspace proximity

### 4. Analytical NLQ Path

- `Genie` answers structured questions against Gold tables, views, and metric views governed in Unity Catalog.
- This path is best for:
  - rankings
  - top movers
  - filtered comparisons
  - market summaries
  - repeatable KPI-style analytical questions
- Genie outputs should be clearly labeled as analytics-generated responses, distinct from the richer copilot path.

### 5. Copilot Path

- `Mosaic AI Agent Framework` implements the main coded copilot.
- The copilot is responsible for:
  - intent classification
  - tool selection
  - evidence retrieval
  - market narrative generation
  - provenance packaging
  - confidence/freshness policy enforcement
- Use `Model Serving` for hosted model endpoints and supporting inference APIs.
- Keep the copilot grounded on governed Gold data and explicit evidence tables, not raw uncontrolled prompt context.

### 6. Optional Agent Bricks Lane

- Use `Agent Bricks` only for:
  - fast prototyping of a bounded assistant
  - selective evaluation of packaged agent capabilities
  - low-risk experiments that can be replaced later
- Do not couple core product flows to Agent Bricks beta-only assumptions.

### 7. Sentinela Operations Plane

- Centralize freshness, quality, cost, token, and audit signals.
- Coordinate multi-agent execution without serving public traffic directly.
- Produce operational summaries and alerts for product, data, and AI teams.

## Request Routing

| Request Type | Primary Path | Reason |
|--------------|--------------|--------|
| KPI, ranking, filter, comparison over structured data | `Genie` | Lowest custom complexity for governed analytical Q&A |
| Narrative market interpretation with provenance and policy | `Agent Framework` | Requires coded orchestration and answer rules |
| Dashboard browse and curated insights | `External frontend` + Gold-backed APIs/views | Best fit for public SaaS serving cost and controlled rendering |
| Admin and internal operational surfaces | `Databricks Apps` | Good fit for low-volume platform-adjacent tools |
| Experimental niche assistant | `Agent Bricks` | Optional acceleration only |

## Interface Contracts

### Frontend -> Routing Layer

Purpose: normalize user requests before they hit `Genie` or the coded copilot.

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

Expected behavior:

- The frontend must not call `Genie` or the copilot directly with raw workspace credentials.
- The routing layer decides whether the request is analytical NLQ, dashboard retrieval, or copilot reasoning.
- The routing layer must attach authorization context and audit metadata before forwarding.

### Routing Layer -> Genie

Purpose: send only governed structured analytical questions to `Genie`.

Request contract:

- `request_id`
- `tenant_id`
- `user_id`
- `workspace_context`
- `semantic_scope`
- `question_text`
- `filters`
- `time_range`
- `response_format`

Response contract:

- `request_id`
- `answer_text`
- `generated_query` when available
- `source_assets`
- `freshness_watermark`
- `execution_status`
- `latency_ms`

Rules:

- `Genie` responses must be labeled in the UI as analytical answers.
- `Genie` responses should avoid freeform market narrative beyond the governed analytical output.
- If the question exceeds the structured analytics scope, the routing layer must redirect to the copilot path.

### Routing Layer -> Copilot

Purpose: send richer reasoning and market-intelligence prompts to the coded `Agent Framework`.

Request contract:

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

Response contract:

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

- The copilot must always return provenance metadata when the answer is grounded.
- The copilot must refuse or downgrade unsupported trading, execution, or out-of-policy requests.
- The copilot must produce Portuguese-first output in V1 unless explicitly overridden.

### Frontend Rendering Contract

Purpose: keep the UI behavior deterministic across `Genie` and copilot responses.

Shared response envelope:

- `request_id`
- `surface_type`
- `title`
- `body`
- `citations`
- `freshness`
- `confidence`
- `actions`
- `warnings`

Rendering rules:

- `surface_type=analytics_answer` renders the `Genie` path with structured evidence emphasis.
- `surface_type=copilot_answer` renders the coded copilot path with richer citations and narrative framing.
- `warnings` must surface stale data, partial coverage, policy limits, or degraded response modes.

### Observability Contract

Purpose: provide one telemetry shape across frontend, `Genie`, and copilot flows.

Minimum event fields:

- `event_time`
- `request_id`
- `tenant_id`
- `user_id`
- `route_selected`
- `model_or_engine`
- `prompt_tokens`
- `completion_tokens`
- `total_tokens`
- `latency_ms`
- `cost_estimate`
- `freshness_watermark`
- `response_status`

Rules:

- `Genie` and copilot telemetry must be recorded separately but normalized into one analytics schema.
- Frontend events must correlate with backend request ids for auditability and cost analysis.
- Missing token fields must be explicit as `null`, not omitted, when a route does not expose token-level usage.

## Token and Cost Strategy

The project should not treat all AI requests equally.

- `Genie` usage should be tracked separately from custom copilot token usage because the operational behavior and optimization levers differ.
- The main copilot must record at least:
  - `tenant_id`
  - `user_id` when available
  - `conversation_id`
  - `request_type`
  - `model`
  - `prompt_tokens`
  - `completion_tokens`
  - `total_tokens`
  - `latency_ms`
  - `cost_estimate`
  - `evidence_asset_ids`
  - `freshness_watermark`
- Token budgets should be enforced by tenant plan and by request class.
- High-cost copilot flows should degrade gracefully:
  - reduce context window
  - reduce retrieval breadth
  - redirect simple analytical requests to Genie
  - surface clear user messaging when policy limits are hit

## Governance and Trust

- All served analytical assets must live under Unity Catalog governance.
- AI answers must expose provenance, freshness, and trace metadata.
- Tenant isolation must be enforced in both dashboard and AI paths.
- Sensitive logs and audit trails must be access-controlled and retained according to policy.
- Prompt inputs should avoid leaking cross-tenant context or unrestricted raw storage paths.

## Observability

- Product metrics:
  - daily active users
  - successful dashboard sessions
  - AI answer success rate
  - stale-answer suppression rate
- Data metrics:
  - ingestion lag
  - Gold publish latency
  - completeness score
  - quality rule pass rate
- AI metrics:
  - tokens by tenant
  - tokens by request type
  - cost by tenant
  - grounded-answer rate
  - citation coverage rate
  - hallucination review sample outcomes

## Security and Access Control

- SSO or equivalent centralized identity for workforce/admin access.
- Tenant-aware authorization boundaries for all product-facing surfaces.
- Secrets must stay in managed secret storage, never in app code or prompt artifacts.
- Admin audit access must be separated from end-user product access.

## Data Contracts

Minimum contract families for V1:

- market snapshot contract
- asset dimension contract
- analytical metric contract
- AI evidence contract
- usage telemetry contract

Each contract must define schema, freshness expectation, quality checks, lineage owner, and downstream dependencies.

## Deployment Shape

- Workspace structure aligned to environment separation: `dev`, `staging`, `prod`.
- Public frontend deployed outside Databricks on low-cost web infrastructure with CDN or edge delivery.
- CI/CD promotes data, app, and serving artifacts with environment-aware configuration.
- Production deploys must include rollback strategy for app code, serving endpoints, and data model releases.

## Build Priorities

1. Establish Gold analytical models and metric views for the highest-value dashboard and Genie use cases.
2. Define the public external frontend shell with authentication, tenant context, and Portuguese-first navigation.
3. Implement the first `Agent Framework` copilot slice with provenance, freshness, and token telemetry.
4. Add observability, cost controls, and admin audit surfaces before wider rollout.
5. Add `Databricks Apps` only for internal/admin workflows where platform-local UX is useful.
6. Evaluate `Agent Bricks` only after the core coded copilot path is operational.

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Genie does not fully cover nuanced market questions | Users may expect richer reasoning than structured analytics can provide | Route only analytical NLQ to Genie and keep narrative reasoning in the coded copilot |
| Copilot cost grows too quickly with broad context | Margins and latency degrade | Enforce request-class budgets, retrieval limits, and redirection to Genie |
| Public app serving inside Databricks would overpay for lightweight web traffic | Serving economics degrade as user traffic grows | Keep the public frontend external and use Databricks for specialized backend capabilities |
| Real-time freshness is too expensive across all datasets | Platform cost and complexity rise early | Tier freshness by dataset criticality |
| Beta dependencies change | Rework risk | Keep Agent Bricks isolated from critical flows |

## Verification Plan

- Validate that every critical user journey maps to exactly one primary serving path.
- Review whether each required AgentCodex project-standard block is represented in this design.
- Verify that token telemetry and cost controls are explicitly present before build.
- Confirm that tenant isolation applies to both dashboard and AI response flows.

## Exit Check

- [x] architecture direction selected
- [x] app layer selected
- [x] analytical NLQ path selected
- [x] copilot path selected
- [x] public serving cost posture defined
- [x] Agent Bricks posture defined
- [x] token/cost strategy captured
- [x] governance and observability included
- [x] build priorities proposed

## Next Step

**Ready for:** `build planning`, starting with Gold analytical assets, external frontend boundaries, request routing, and telemetry schema for token/cost observability.
