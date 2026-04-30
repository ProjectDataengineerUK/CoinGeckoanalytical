# BUILD: CoinGeckoAnalytical

> Build planning artifact for `coingeckoanalytical`, rewritten from the refreshed design for a complete-V1 product with disciplined internal sequencing.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `coingeckoanalytical` |
| **Date** | `2026-04-30` |
| **Owner** | `operator` |
| **Authoring Role** | `workflow-builder` |
| **Status** | Ready for implementation planning |
| **Baseline Input** | `.agentcodex/features/DESIGN_coingeckoanalytical.md` |

## Build Goal

Build the complete V1 product selected in `brainstorm`, specified in `define`, and architected in `design`, while enforcing internal sequencing so execution closes real product behavior instead of drifting into scaffolding.

The build must deliver:

- public external product surface
- governed analytical dashboard experience
- governed structured analytical Q&A
- coded narrative market copilot
- trust signals: provenance, freshness, confidence, telemetry
- operational and governance foundations required for a real V1 candidate

## Build Principle

This is a `complete-V1 build`, not a reduced MVP.

However, the build is only valid if it follows the design sequencing and treats each slice as product behavior, not as isolated infrastructure work.

The build must reject these failure modes:

- counting placeholders as implementation
- counting local-only helpers as shipped capability
- treating deploy preparation as product progress
- building ops surfaces before the corresponding user-facing flow exists

## Build Posture

Existing repository assets remain useful, but must be interpreted correctly:

- `contracts/` are valid build support artifacts
- `backend/telemetry_handoff.py`, `notification_handoff.py`, and related helpers remain useful support code
- `backend/copilot_mvp.py` remains prototype evidence, not delivered copilot behavior
- `frontend/README.md` remains placeholder scope, not frontend implementation
- Databricks bundle, readiness, and deployment helpers remain build-local infrastructure, not product completion

## Build Strategy

The V1 remains broad, but the build sequence is constrained.

Priority order:

1. foundational backbone
2. governed data execution baseline
3. public analytical surface
4. governed analytical NLQ
5. coded copilot
6. operational completion

No later sequence may be treated as complete if the prior sequence is still only placeholder or prototype.

The first hard dependency is explicit:

- no dashboard slice may be counted as implemented before the governed Bronze, Silver, and Gold serving chain is executable for the selected route family
- no Genie slice may be counted as implemented before the governed metric-view inputs are backed by that same data chain
- no copilot slice may be counted as implemented before its retrieval scope points to governed evidence assets instead of demo or stub payloads

## Workstreams

### WS1. Foundational Backbone

Scope:

- define mandatory source strategy for CoinGecko plus additional sources
- formalize medallion data contracts and ownership
- materialize Terraform or equivalent IaC for environment, Unity Catalog, grants, and execution identity
- define auth and tenant propagation baseline
- define governance, access control, and compliance baseline required for build
- stabilize telemetry baseline for dashboard, Genie, and copilot routes

Outputs:

- source inventory with mandatory-first ordering
- baseline Bronze, Silver, and Gold contracts
- IaC baseline for Databricks environment and governance foundation
- auth/tenant boundary notes
- governance/access-control baseline for build
- telemetry baseline tied to real user paths

### WS2. Public Analytical Surface

Scope:

- implement a real external frontend shell
- implement at least the first governed dashboard-serving views
- build backend retrieval APIs for dashboard rendering
- expose user-visible freshness posture on the served dashboard

Outputs:

- real frontend shell
- first dashboard route(s)
- real dashboard payload contract and examples
- dashboard freshness surfacing

Dependency gate:

- WS2 starts only after the first governed data family is executable beyond design-only contracts

### WS3. Governed Analytical NLQ

Scope:

- implement Genie-facing metric views and governed analytical routing
- define the first analytical questions that count as V1 behavior
- expose analytical evidence and labeling in the user-facing response

Outputs:

- Genie metric views for first user journeys
- routed structured NLQ path
- analytical response examples with evidence metadata

### WS4. Coded Copilot

Scope:

- replace prototype-only copilot behavior with a real grounded route
- implement evidence retrieval scope and provenance packaging
- expose freshness, confidence, and route policy in user-visible output
- keep the Genie versus copilot split explicit

Outputs:

- real narrative copilot path
- grounded response shape
- provenance/freshness/confidence surfacing
- token and cost telemetry tied to the copilot route

### WS5. Operational Completion

Scope:

- connect Sentinela readiness surfaces to actual built routes
- implement admin/audit review posture for the first real V1 flows
- complete the minimum runbooks and release interpretation surfaces required for a serious V1 candidate

Outputs:

- route-aware readiness checks
- admin/audit review surface definition
- operational runbook baseline
- clear distinction between local evidence and production evidence

## Initial Build Slices

### Slice 1. Source And Data Backbone

Purpose:

- create the first honest data foundation for the V1

Must include:

- mandatory source ordering
- first source onboarding posture
- first Gold-backed dashboard dataset family
- freshness and quality posture for that family
- IaC baseline for Unity Catalog, grants, and environment separation

### Slice 2. Public Dashboard Surface

Purpose:

- close the first real public dashboard flow

Must include:

- governed data family already executable for the selected route
- real frontend implementation
- backend retrieval path
- dashboard rendering from governed data
- freshness surfaced in UI

### Slice 3. Governed Analytical Q&A

Purpose:

- close the first structured analytical question flow through the governed path

Must include:

- Genie-ready metric view(s)
- governed routing
- labeled structured answer output
- evidence metadata

### Slice 4. Narrative Copilot

Purpose:

- close the first real narrative market question flow

Must include:

- coded orchestration
- governed evidence retrieval
- provenance/freshness/confidence metadata
- user-visible trust framing

### Slice 5. Operational Readiness For Real Flows

Purpose:

- close the minimum trust loop around the first implemented V1 flows

Must include:

- telemetry connected to actual routes
- Sentinela interpretation tied to actual route behavior
- admin/audit posture
- release-readiness signals for the implemented flows

## Build Acceptance Rules

The build is only healthy when:

1. the selected Bronze, Silver, and Gold serving chain is executable for the first route family
2. a real frontend exists
3. at least one dashboard flow is served from governed data
4. at least one structured analytical question works through the governed path
5. at least one narrative copilot question works through the coded path
6. freshness, provenance, and telemetry are surfaced on actual product behavior
7. operational readiness reflects those real flows rather than isolated helpers

Anything else remains `prototype`, `placeholder`, `scaffolding`, or `build-local infrastructure`.

## Deferred Until Real Product Flows Exist

- deploy hardening beyond build validation
- ship readiness sign-off
- broad Sentinela expansion unrelated to built flows
- external notification integration beyond route-backed needs
- wider enterprise rollout mechanics not yet attached to implemented behavior

## Reporting Rules

- every build slice must produce a durable report in `.agentcodex/reports/`
- every report must state whether the result is `implemented`, `prototype`, `placeholder`, or `build-local`
- no report may imply shipped product behavior unless the corresponding user-facing flow is demonstrably real
- verification must include actual relation to `brainstorm`, `define`, and `design`, not only local tests

## Immediate Next Action

Start `WS1 / Slice 1`:

1. define the mandatory first source set
2. define the first honest governed data family for dashboard and AI use
3. choose the first dashboard route
4. choose the first structured analytical question
5. choose the first narrative copilot question
6. make the selected Bronze, Silver, and Gold chain executable
7. only then build forward into dashboard, Genie, and copilot slices
