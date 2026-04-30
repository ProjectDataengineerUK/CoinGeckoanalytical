# Delivery Forecast

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- workflow_reference:
  - `.agentcodex/features/BRAINSTORM_coingeckoanalytical.md`
  - `.agentcodex/features/DEFINE_coingeckoanalytical.md`
  - `.agentcodex/features/DESIGN_coingeckoanalytical.md`
  - `.agentcodex/features/BUILD_coingeckoanalytical.md`
- planning_status: `aligned to workflow artifacts`
- confidence: `medium`

## Phase Reading

- `brainstorm`: completed
- `define`: completed
- `design`: completed
- `build`: active
- `ship`: blocked until build closes real user-facing flows and live deploy evidence

## Alignment Summary

- `brainstorm` fixes the ambition: broad complete-V1 product, external public frontend, Databricks-first backend, Portuguese-first experience, and strong trust/governance from day one.
- `define` converts that into product acceptance criteria: dashboard, grounded AI, tenant isolation, freshness visibility, governance traceability, and operational readiness.
- `design` constrains the architecture into three planes and makes the route split explicit: dashboard, Genie, copilot, and Sentinela.
- `build` forces disciplined sequencing and explicitly forbids counting placeholders or local-only helpers as product completion.

## Practical Current Position

- WS1 is materially advanced in repo artifacts through contracts, Bronze/Silver/Gold SQL, Terraform baseline, and project-standard baseline docs.
- the first governed data family is structurally defined, but not yet proven as the executable dependency baseline for served product flows.
- WS2 is partial because the frontend is still not a real app and the backend dashboard route still uses demo rows.
- WS3 is partial because governed routing exists, but no real Genie-backed question flow is proven end to end.
- WS4 is partial because copilot envelope, route split, and telemetry exist, but the narrative response is still MVP/stub.
- WS5 is partial because Sentinela and observability assets exist, but they are not yet tied to fully real product flows or live deploy evidence.

## Delivery Forecast

1. `2026-04-30` to `2026-05-02`
   Deliver the first governed data execution baseline: executable Bronze, Silver, and Gold chain for the `market overview intelligence` family, ready to back served flows.
2. `2026-05-03` to `2026-05-05`
   Deliver the first real dashboard flow: real governed retrieval in the backend, stable dashboard contract, and freshness surfaced through the served response.
3. `2026-05-06` to `2026-05-08`
   Deliver the first governed analytical NLQ flow: Genie-ready metric view usage, labeled analytical answer path, and evidence metadata.
4. `2026-05-09` to `2026-05-12`
   Deliver the first grounded copilot flow: real evidence retrieval scope, provenance packaging, freshness metadata, and confidence surfacing.
5. `2026-05-13` to `2026-05-14`
   Deliver operational completion for the implemented flows: Sentinela route-aware readiness, bundle/deploy wiring for `dev`, `staging`, and `prod`, and operator-facing release interpretation.
6. `2026-05-15` to `2026-05-16`
   Deliver end-to-end validation evidence and decide whether `ship` can start.

## Forecast Assumptions

- current backend routing, envelope, and telemetry code will be reused rather than replaced
- current Databricks SQL, bundle, and Terraform artifacts are the base for live integration
- the first real V1 cut will focus on the `market overview intelligence` family already present in repo artifacts
- no major architecture pivot happens between `2026-04-30` and `2026-05-14`

## Main Risks

- frontend work can slip because the repo still lacks a real public application surface
- live Databricks binding can uncover schema, auth, or environment gaps that local tests do not catch
- project-standard `validacao`, `operacao`, and `deploy` are still partial, so ship-readiness may extend beyond the forecast window
- if the product insists on onboarding additional sources before the first real slice is accepted, WS1/WS2 may reopen

## Acceptance Gate For Starting Ship

Do not start `ship` before all of the following are true:

- one selected governed data family is executable from Bronze through Gold for the served route family
- one dashboard flow is served from governed data
- one structured analytical question works through the governed path
- one narrative copilot question works through the coded path
- freshness, provenance, and telemetry are visible on real responses
- `dev/staging/prod` deployment wiring is defined and locally validated
- live Databricks evidence exists for the claimed build status
