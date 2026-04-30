# Gold Market Views Baseline

## Purpose

Define the first governed Gold analytical assets for dashboard serving and `AI/BI Genie`.

## Initial Gold Views

### 1. `gold_market_rankings`

Purpose:

- top assets by market cap
- rank-based exploration
- market-cap and liquidity-oriented comparisons

Core dimensions:

- `asset_id`
- `symbol`
- `name`
- `category`
- `observed_at`

Core metrics:

- `market_cap_usd`
- `price_usd`
- `volume_24h_usd`
- `circulating_supply`
- `market_cap_rank`

### 2. `gold_top_movers`

Purpose:

- strongest positive and negative asset moves
- short-horizon market motion analysis

Core dimensions:

- `asset_id`
- `symbol`
- `name`
- `observed_at`
- `window_id`

Core metrics:

- `price_change_pct_1h`
- `price_change_pct_24h`
- `price_change_pct_7d`
- `volume_24h_usd`
- `market_cap_usd`

### 3. `gold_market_dominance`

Purpose:

- dominance trends for BTC, ETH, stablecoins, and other major groupings
- macro market structure analysis

Core dimensions:

- `observed_at`
- `dominance_group`

Core metrics:

- `market_cap_usd`
- `dominance_pct`

### 4. `gold_cross_asset_comparison`

Purpose:

- side-by-side comparison for selected assets
- dashboard and copilot evidence support

Core dimensions:

- `asset_id`
- `symbol`
- `observed_at`

Core metrics:

- `price_usd`
- `market_cap_usd`
- `volume_24h_usd`
- `price_change_pct_24h`
- `price_change_pct_7d`
- `correlation_bucket`

## Genie Suitability

The first Gold baseline should support these query classes well:

- rankings
- movers
- filtered comparisons
- market summaries
- repeatable metric-style questions

The first Gold baseline should not be stretched to replace narrative reasoning that belongs in the coded copilot.
