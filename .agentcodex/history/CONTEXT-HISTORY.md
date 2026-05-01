# Context History

## Purpose

Preserve resumable project context in repo files instead of relying on chat memory only.

## Current State

- project: `CoinGeckoAnalytical`
- status: `build-started`
- active_phase: `build`
- primary_architecture: `external frontend + Databricks data/AI plane + sentinela ops plane`
- generated_at: `2026-04-30`

## Canonical Artifacts

- brainstorm: `.agentcodex/features/BRAINSTORM_coingeckoanalytical.md`
- define: `.agentcodex/features/DEFINE_coingeckoanalytical.md`
- design: `.agentcodex/features/DESIGN_coingeckoanalytical.md`
- build: `.agentcodex/features/BUILD_coingeckoanalytical.md`
- architecture image: `docs/assets/coingeckoanalytical-architecture.png`
- architecture doc: `docs/architecture.md`
- routing matrix: `.agentcodex/reports/specialist-routing-matrix-2026-04-29.md`
- latest build report: `.agentcodex/reports/build-planning-refresh-2026-04-30.md`
- delivery forecast: `.agentcodex/reports/delivery-forecast-2026-04-30.md`
- design-flow alignment: `.agentcodex/reports/design-flow-alignment-2026-04-30.md`
- latest data-baseline report: `.agentcodex/reports/build-slice-1-market-source-ingestion-2026-04-30.md`
- latest chain-validation report: `.agentcodex/reports/build-slice-1-market-overview-chain-validation-2026-04-30.md`
- latest market-handoff report: `.agentcodex/reports/build-slice-1-market-source-handoff-2026-04-30.md`
- latest repo-flow report: `.agentcodex/reports/build-slice-1-market-source-repo-flow-2026-04-30.md`
- latest live-checklist report: `.agentcodex/reports/dev-live-validation-checklist-2026-04-30.md`
- latest github-actions-live report: `.agentcodex/reports/build-slice-5-github-actions-databricks-cli-2026-04-30.md`
- latest live-sql report: `.agentcodex/reports/build-slice-5-live-sql-validation-2026-04-30.md`
- latest workflow state: `brainstorm, define, and design completed; natural workflow restarted into build on 2026-04-30 and WS1 / Slice 1 backbone was materialized`
- latest workflow state: `brainstorm, define, and design completed; natural workflow restarted into build on 2026-04-30, WS1 / Slice 1 backbone was materialized, Bronze/Silver executable contracts were added, the dashboard backend route foundation was implemented, BFF routing was added, Unity Catalog foundation artifacts were materialized, Terraform became an explicit Phase 1 baseline, the Terraform scope was expanded to identities, jobs, policies, and promotion guidance, and the Project Standard manifest plus Phase 1 cost/secrets/audit policies were materialized`
- latest workflow state: `build remains the active phase; backend routing, copilot MVP envelope, Sentinela checks, and Databricks build assets are locally validated, but frontend implementation, real Databricks bindings, and live deploy evidence remain open`
- latest workflow state: `the design-aligned data chain now has an executable market source ingestion job wired into the bundle, Terraform, CI, and local tests, but the live Bronze -> Silver -> Gold execution path still needs workspace evidence`
- latest workflow state: `the market overview intelligence chain is now structurally validated in CI from source-ingestion entrypoint through Bronze, Silver, Gold, and Genie metric views, but still lacks live workspace execution evidence`
- latest workflow state: `the market overview intelligence family now also has a backend-side market-source handoff and repo-local fixture, so the first data path can be exercised without inventing payload shape later`
- latest workflow state: `the backend market-source handoff, repo fixture, and Databricks ingestion normalization are now proven compatible through repo-level tests`
- latest workflow state: `the next gating move is explicit dev workspace validation for Bronze, Silver, Gold, and Genie metric-view row presence before any dashboard work resumes`
- latest workflow state: `GitHub Actions can now install the Databricks CLI and pass the market fixture payload directly to the live market ingestion job during deploy`
- latest workflow state: `GitHub Actions can now optionally execute live SQL row-count checks against a Databricks SQL warehouse when DATABRICKS_SQL_WAREHOUSE_ID is configured`
- latest workflow state: `deployment docs, checklist, and handoff now explicitly state that deploy uses DATABRICKS_HOST plus DATABRICKS_TOKEN, while full live SQL validation and artifact upload additionally depend on DATABRICKS_SQL_WAREHOUSE_ID`
- latest workflow state: `the native next infrastructure step is Terraform plan for dev, but the current local environment does not have the Terraform CLI installed and no real Databricks dev inputs are loaded`
- latest workflow state: `a native Terraform execution attempt now exists; init succeeded after local CLI bootstrap, but validate is blocked by the Databricks provider schema handshake in this environment before plan can run`
- latest workflow state: `the repository now compensates for that local Terraform limitation with a dedicated GitHub Actions terraform workflow that keeps plan/apply separate from ci deploy execution`
- latest workflow state: `the Bronze schema remediation now has a dedicated manual GitHub Actions workflow so the operator can approve and trigger it without enabling automatic deploys`
- latest workflow state: `approval state is now tracked explicitly in repo-local policy/status artifacts so Databricks and Terraform mutations stay operator-approved rather than push-driven`
- latest workflow state: `ci deploy, terraform apply, and bronze migration are now all explicitly approved in the repo-local approval status artifact`
- latest workflow state: `the default publication flow now includes commit and push after validation when the user is ready to publish the change set`

## Important Decisions

- public SaaS surface uses `external web frontend`
- `Databricks` is the backend platform for data, governance, analytics, AI, and model versioning
- `AI/BI Genie` handles structured analytical NLQ
- `Mosaic AI Agent Framework` handles the main market copilot
- `Sentinela` handles multi-agent coordination and observability
- `Databricks Apps` is not the primary public frontend
- initial source of truth for market data is `CoinGecko API`
- current architecture image is the detailed enterprise diagram in `docs/assets/coingeckoanalytical-architecture.png`
- the product direction was re-grounded through a fresh `brainstorm -> define -> design` pass
- the natural workflow restart is now anchored in the feature artifacts themselves, with `build` as the active phase
- `WS1 / Slice 1` now has a durable backbone artifact covering source ordering, first governed data family, and first real route targets
- the `market overview intelligence` family now has an executable Bronze/Silver baseline that feeds the existing Gold layer
- the `market overview intelligence` family now also has a bundle-managed market source ingestion entrypoint for `bronze_market_snapshots`
- the `market overview intelligence` family now has a repo-local chain validator that guards Bronze -> Silver -> Gold -> Genie structural drift
- the `market overview intelligence` family now has a backend handoff writer and a controlled source fixture for repo-local smoke validation
- the `market overview intelligence` family now has repo-level compatibility tests that bridge backend handoff and Databricks ingestion normalization
- the first governed backend response for `dashboard.market-overview` now exists with payload and telemetry shaping
- the backend now has a unified BFF routing foundation for dashboard, Genie, and copilot request paths
- the Phase 1 Unity Catalog namespace, ownership, boundary, and lineage posture is now explicit in repo-local artifacts
- the project now treats Terraform IaC as a required part of Phase 1 rather than a later hardening concern
- the Terraform baseline now includes operational job, policy, and promotion scaffolding instead of catalog-only scope
- the repository now has a single Project Standard status manifest and explicit Phase 1 policies for cost control, secrets/access, and retention/audit
- Terraform has been split into a separate workflow so plan/apply are not mixed into the deploy job
- Databricks bundle deploy now requires explicit `workflow_dispatch` approval in `ci.yml` instead of running automatically on push
- the frontend shell is now materialized as a real static surface with BFF-ready request/response rendering instead of placeholder documentation only
- commit and push are now treated as the normal publication path after validation, unless the user asks to hold back publication
- the deploy evidence path now explicitly distinguishes base deploy credentials from the additional warehouse secret needed for automated live SQL row-count validation
- the next native execution step before claiming live environment progress is `terraform init` plus `terraform plan` for `dev`, not another repo-only documentation pass
- the selected direction remains a broad complete-V1 product, not a narrow MVP
- `deploy` and `ship` remain paused until build closes real user-facing product behavior
- `frontend/` now has a real shell implementation, but it still needs live BFF binding and delivery validation
- `backend/copilot_mvp.py` is currently prototype evidence, not delivered product behavior
- the current phase map is `brainstorm completed -> define completed -> design completed -> build active -> ship blocked`
- the next valid delivery sequence remains `governed data execution baseline -> real dashboard flow -> real governed analytical NLQ -> real grounded copilot -> operational completion -> deploy evidence -> ship decision`
- dashboard, Genie, and copilot are now treated explicitly as dependents of the same first governed data family rather than parallel starting points
- the design flow is now explicitly normalized as `source ingestion -> Bronze -> Silver -> Gold -> serving routes -> frontend experience -> ops interpretation`

## Open Gaps

- real frontend implementation beyond placeholder scope
- one real dashboard flow backed by governed data
- one real analytical question flow
- one real narrative copilot flow with trust metadata
- end-to-end verification for the active V1 slice
- project-standard materialization across remaining governance and compliance blocks
- deploy evidence only after the slice is real

## Delivery Forecast

- forecast_date: `2026-04-30`
- planning_basis: `brainstorm completed, define completed, design completed, build active`
- confidence: `medium`
- assumption: `no architecture reset, no major source/provider change, and current backend plus Databricks assets are reused instead of rebuilt`

### Phase Status

- `brainstorm`: completed
- `define`: completed
- `design`: completed
- `build`: active
- `ship`: not started and still blocked by missing real product flows plus live deploy evidence

### Forecast Window

1. `2026-04-30` to `2026-05-02`
   Close the first governed data execution baseline by making the selected Bronze, Silver, and Gold chain executable for the market-overview family and ready for served consumption.
2. `2026-05-03` to `2026-05-05`
   Close the first real dashboard slice by replacing demo dashboard payload assembly with governed Databricks-backed retrieval, while keeping the existing BFF contract.
3. `2026-05-06` to `2026-05-08`
   Close the first governed analytical NLQ slice through Genie-facing metric views and labeled analytical responses.
4. `2026-05-09` to `2026-05-12`
   Close the first grounded copilot slice by replacing MVP-only narrative output with evidence-backed response assembly, provenance, freshness, and confidence metadata.
5. `2026-05-13` to `2026-05-14`
   Close operational completion for the first real flows: Sentinela route-aware checks, release-readiness interpretation, and `dev/staging/prod` deploy wiring.
6. `2026-05-15` to `2026-05-16`
   Run end-to-end validation, reconcile project-standard partial blocks, and decide whether the repo can enter `ship` preparation.

### Forecast Risks

- the frontend is still documentation-only, so WS2 can slip if a real app shell must be created from zero
- current backend dashboard routing still depends on demo payloads, which means live Databricks integration may expose contract gaps
- `deploy` and `operacao` remain partial in the project-standard manifest, so environment wiring can expand beyond the nominal window
- if additional mandatory data sources beyond CoinGecko are enforced before the first real slice closes, the forecast likely extends

## Resume Rule

When resuming work, read this file first, then review:

1. `.agentcodex/features/BRAINSTORM_coingeckoanalytical.md`
2. `.agentcodex/features/DEFINE_coingeckoanalytical.md`
3. `.agentcodex/features/DESIGN_coingeckoanalytical.md`
4. `.agentcodex/features/BUILD_coingeckoanalytical.md`

## Update Rule

Update this file whenever a major architecture, workflow, or operating-model decision changes.
