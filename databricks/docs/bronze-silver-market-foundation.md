# Bronze Silver Market Foundation

## Purpose

Define the first executable Bronze and Silver layer contract that supports the active `WS1 / Slice 1` build baseline.

## Implementation Asset

- executable baseline: `bronze_silver_market_foundation.sql`

## Bronze Contract

### `bronze_market_snapshots`

Purpose:

- land CoinGecko market observations with minimal transformation

Required fields:

- `source_system`
- `source_record_id`
- `asset_id`
- `symbol`
- `name`
- `category`
- `observed_at`
- `ingested_at`
- `market_cap_usd`
- `price_usd`
- `volume_24h_usd`
- `circulating_supply`
- `market_cap_rank`
- `payload_version`

Rules:

- raw provider timing must be preserved in `observed_at`
- ingestion timing must be preserved in `ingested_at`
- provider identity must remain visible through `source_system`

## Silver Contracts

### `silver_market_snapshots`

Purpose:

- normalize and deduplicate the latest usable market snapshot per asset and observation timestamp

Semantics:

- symbols are normalized to uppercase
- missing names and categories are filled with controlled defaults
- duplicate raw observations are resolved by latest `ingested_at`

### `silver_market_changes`

Purpose:

- derive repeatable change windows used by Gold movers and structured analytics

Semantics:

- computes 1h, 24h, and 7d percentage change proxies
- keeps a stable `window_id` for the baseline route

### `silver_market_dominance`

Purpose:

- derive grouped dominance views for BTC, ETH, stablecoins, and long-tail market structure

Semantics:

- dominance is grouped by category-like market role
- dominance is computed as share of market cap at each observation time

### `silver_cross_asset_comparison`

Purpose:

- expose normalized cross-asset comparison inputs for dashboard and copilot use

Semantics:

- assigns a comparison bucket by market-cap rank
- computes comparable 24h and 7d movement context

## Dependency Chain

1. `bronze_market_snapshots`
2. `silver_market_snapshots`
3. `silver_market_changes`
4. `silver_market_dominance`
5. `silver_cross_asset_comparison`
6. `gold_market_views.sql`
7. `genie_metric_views.sql`

## First Slice Alignment

This baseline supports:

- `dashboard.market-overview`
- `genie.market-rankings`
- `copilot.market-interpretation`

It does not yet implement ingestion orchestration or a live Databricks job schedule for the market source itself.
