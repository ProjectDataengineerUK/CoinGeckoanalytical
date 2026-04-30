# Unity Catalog Foundation

## Purpose

Materialize the Phase 1 Unity Catalog baseline so the project has explicit governed structure, ownership, environment separation, and consumption boundaries.

## Implementation Asset

- executable baseline: `unity_catalog_foundation.sql`

## Environment Layout

The baseline uses one catalog per environment:

- `cgadev`
- `cgastaging`
- `cgaprod`

This prevents build, validation, and production serving from sharing one governance boundary.

## Schema Layout

### `market_bronze`

- raw provider landing
- source timestamps and provider metadata preserved
- writable by ingestion services only

### `market_silver`

- canonicalization, normalization, and derived intermediate views
- writable by market pipeline services

### `market_gold`

- tenant-facing governed analytical views
- readable by the product backend
- source for dashboard and downstream governed analytical serving

### `ai_serving`

- Genie metric views
- governed AI support views
- no raw provider landing

### `ops_observability`

- usage telemetry
- Sentinela alerts
- readiness and operational health views

### `audit_control`

- audit-sensitive traces and review assets
- tighter access boundary than product-facing datasets

### `reference_data`

- canonical asset mapping and durable dimensions
- shared normalization support

## Ownership Model

- `data_platform` owns `market_bronze`, `market_silver`, `market_gold`, and `reference_data`
- `product_analytics` owns `ai_serving`
- `platform_ops` owns `ops_observability`
- `governance_admin` owns `audit_control`

## Access Boundary

### Product Backend

- can read `market_gold`
- can read governed views from `ai_serving`
- cannot write raw operational tables directly

### Genie

- must read only governed views in `ai_serving`
- should not query Bronze or Silver directly

### Copilot

- should retrieve evidence from `market_gold` and governed AI support assets
- should not retrieve from uncataloged or ad hoc notebook outputs

### Platform Ops

- can read `ops_observability`
- can review readiness, route health, alerts, and telemetry

### Governance Admin

- can read `audit_control`
- can review policy-sensitive traces and release posture

## First Asset Mapping

- `cgadev.market_bronze.bronze_market_snapshots`
- `cgadev.market_silver.silver_market_snapshots`
- `cgadev.market_silver.silver_market_changes`
- `cgadev.market_silver.silver_market_dominance`
- `cgadev.market_silver.silver_cross_asset_comparison`
- `cgadev.market_gold.gold_market_rankings`
- `cgadev.market_gold.gold_top_movers`
- `cgadev.market_gold.gold_market_dominance`
- `cgadev.market_gold.gold_cross_asset_comparison`
- `cgadev.ai_serving.mv_market_rankings`
- `cgadev.ai_serving.mv_top_movers`
- `cgadev.ai_serving.mv_market_dominance`
- `cgadev.ai_serving.mv_cross_asset_compare`
- `cgadev.ops_observability.ops_usage_events`
- `cgadev.ops_observability.ops_sentinela_alerts`

## Phase 1 Rule

Phase 1 is not complete unless:

- the namespace boundary is explicit
- asset ownership is explicit
- read and write roles are explicit
- Genie and copilot consumption boundaries are explicit
- operational and audit datasets are governed, not left outside the catalog model
