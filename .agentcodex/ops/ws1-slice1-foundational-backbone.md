# WS1 / Slice 1 Foundational Backbone

## Purpose

Consolidate the first build-ready backbone for CoinGeckoAnalytical so the active `build` phase advances from broad design into a disciplined first V1 slice.

This artifact is the source of truth for:

- mandatory first source ordering
- first governed data family
- first dashboard route
- first structured analytical question
- first narrative copilot question
- auth and tenant propagation baseline
- governance, access-control, compliance, and telemetry expectations for the first real slice

## Build Status

- workflow_phase: `build`
- workstream: `WS1`
- slice: `Slice 1`
- slice_status: `defined`
- product_status: `no real user-facing flow closed yet`

## Mandatory First Source Set

### Source 1. CoinGecko Market API

- role: `mandatory primary market source`
- purpose: asset universe, price, market cap, volume, rank, and 24h market movement
- initial coverage: dashboard baseline, Genie baseline, copilot evidence baseline
- owner: `data-platform`
- freshness_target: `near-real-time where technically and economically viable`
- lineage_identity: `source_system = coingecko_api`

### Source 2. Internal Analytical Reference Tables

- role: `mandatory normalization source`
- purpose: canonical asset identifiers, symbol collision handling, category mapping, and stable dimensions used across Bronze, Silver, and Gold
- initial coverage: cross-source harmonization and durable asset identity
- owner: `data-platform`
- freshness_target: `updated on controlled change cadence`
- lineage_identity: `source_system = internal_reference`

### Source 3. Usage Telemetry Events

- role: `mandatory operational source`
- purpose: route health, token/cost visibility, readiness interpretation, and trust surfacing for dashboard, Genie, and copilot paths
- initial coverage: request telemetry from backend and AI routes
- owner: `platform-ops`
- freshness_target: `continuous append with operational lag monitoring`
- lineage_identity: `source_system = ops_usage_events`

### Source 4. Sentinela Alert Events

- role: `mandatory operational control source`
- purpose: readiness interpretation, freshness/quality alerting, and operator review
- initial coverage: alert landing and operational dashboarding
- owner: `platform-ops`
- freshness_target: `event-driven ingestion`
- lineage_identity: `source_system = sentinela_alerts`

## Source Ordering Rule

1. `CoinGecko Market API` must land first because the first user-facing dashboard, Genie, and copilot flows depend on governed market data.
2. `Internal Analytical Reference Tables` must be stabilized before Gold serving is treated as trustworthy, because symbol and asset identity drift would contaminate dashboard and AI outputs.
3. `Usage Telemetry Events` must be present before the first route is considered production-candidate behavior, because the design requires trust, cost, and freshness observability.
4. `Sentinela Alert Events` must be connected before operational completion, but their contract is defined now so later slices do not improvise alert semantics.

## First Governed Data Family

The first governed family is `market overview intelligence`.

It is backed by the existing Gold assets and should remain the first serving baseline for dashboard and AI use:

- `gold_market_rankings`
- `gold_top_movers`
- `gold_market_dominance`
- `gold_cross_asset_comparison`

Related governed analytical assets:

- `mv_market_rankings`
- `mv_top_movers`
- `mv_market_dominance`
- `mv_cross_asset_compare`

## Bronze / Silver / Gold Backbone

### Bronze

- raw CoinGecko snapshots
- source timestamps preserved
- provider payload preserved for replay and audit

### Silver

- canonical asset dimension
- normalized market snapshots
- normalized market change windows
- normalized dominance series
- normalized cross-asset comparison inputs

### Gold

- tenant-facing market overview datasets
- served freshness watermark on every dashboard and AI-facing asset family
- quality gate required before trusted serving

## First Real Product Targets

### First Dashboard Route

- route_id: `dashboard.market-overview`
- product_surface: `public external frontend`
- route_goal: show market rankings, top movers, dominance, and cross-asset comparison in Portuguese with visible freshness

### First Structured Analytical Question

- route_id: `genie.market-rankings`
- question: `Quais sao os 10 ativos com maior market cap agora e como variaram nas ultimas 24 horas?`
- governed_scope: `Gold market rankings and top movers only`

### First Narrative Copilot Question

- route_id: `copilot.market-interpretation`
- question: `O que explica os movimentos recentes de BTC, ETH e SOL nas ultimas 24 horas?`
- governed_scope: `Gold market rankings, top movers, dominance, cross-asset comparison, and freshness metadata`

## Auth And Tenant Propagation Baseline

- every frontend request must carry `tenant_id`, `user_id`, `session_id`, `request_id`, and `locale`
- the backend is the only layer allowed to enrich policy context before routing to Gold APIs, Genie, or copilot
- Gold market data is initially `shared analytical reference data`
- usage, audit, alert, and future customer-specific artifacts are `tenant-scoped`
- no workspace-bound analytical or AI service is called directly from the frontend

## Governance And Ownership Baseline

- `data-platform` owns market data ingestion, canonical dimensions, Silver normalization, and Gold analytical contracts
- `platform-ops` owns telemetry, Sentinela signals, readiness interpretation, and operational review baselines
- `product-analytics` owns metric semantics, dashboard intent, and the governed analytical question catalog
- every Gold asset must declare owner, freshness target, quality checks, lineage source, and tenant scope

## Access-Control Baseline

- public end users authenticate outside Databricks
- tenant context is attached in the backend before any analytical or AI execution
- Gold market views used for public intelligence are read-only and governed
- operational views, telemetry tables, alert tables, and audit surfaces are restricted to operator and admin roles
- admin and operator access is separate from end-user access

## Compliance Baseline

- AI answers must expose provenance, freshness, and confidence metadata
- audit-relevant request and route metadata must be retained in governed operational storage
- secrets must remain externalized from app code and notebooks
- stale or degraded data must be surfaced explicitly, not silently served as current
- regulated-data assumptions remain conservative until a formal compliance posture expands this baseline

## Telemetry Baseline For Real User Paths

The first route telemetry set must cover:

- `dashboard.market-overview`
- `genie.market-rankings`
- `copilot.market-interpretation`

Required telemetry fields:

- `request_id`
- `tenant_id`
- `user_id`
- `route_selected`
- `model_or_engine`
- `latency_ms`
- `response_status`
- `freshness_watermark`
- `prompt_tokens` where applicable
- `completion_tokens` where applicable
- `total_tokens` where applicable
- `cost_estimate`

## Exit Criteria For WS1 / Slice 1

- the source ordering is explicit and durable
- the first governed data family is named and constrained
- the first dashboard, Genie, and copilot targets are explicitly chosen
- auth and tenant propagation rules are fixed for later implementation
- governance, access control, compliance, and telemetry baselines exist as repo-local references

## Next Build Move

After this backbone, implement in order:

1. executable source and contract materialization for the `market overview intelligence` family
2. real frontend shell and dashboard route for `dashboard.market-overview`
3. governed Genie path for `genie.market-rankings`
4. grounded copilot path for `copilot.market-interpretation`
