# Gold Market Views Baseline

## Purpose

Define the governed Gold analytical assets for dashboard serving and `AI/BI Genie`.

## Source Contract

- executable implementation: `gold_market_views.sql`
- freshness and quality posture: `freshness_quality_baseline.sql`
- metric-view layer: `genie_metric_views.sql`

## Gold Assets

### `gold_market_rankings`

Grain:

- one row per `asset_id` and `observed_at`

Source:

- `bronze_market_snapshots`

Serving intent:

- rank exploration
- market-cap and liquidity comparisons

Governed semantics:

- deduplicated with `ROW_NUMBER()`
- freshness tier `tier_a`
- quality status derived from basic numeric sanity checks

### `gold_top_movers`

Grain:

- one row per `asset_id`, `window_id`, and `observed_at`

Source:

- `silver_market_changes`

Serving intent:

- strongest positive and negative asset moves
- short-horizon motion analysis

Governed semantics:

- move direction and band are normalized in the view
- freshness tier `tier_a`
- quality checks guard against extreme percentage corruption

### `gold_market_dominance`

Grain:

- one row per `dominance_group` and `observed_at`

Source:

- `silver_market_dominance`

Serving intent:

- BTC, ETH, stablecoin, and long-tail structure analysis

Governed semantics:

- dominance band is derived for more readable NLQ and dashboard grouping
- freshness tier `tier_a`
- dominance percentage must stay within 0 to 100

### `gold_cross_asset_comparison`

Grain:

- one row per `asset_id`, `observed_at`, and `correlation_bucket`

Source:

- `silver_cross_asset_comparison`

Serving intent:

- side-by-side comparison for selected assets
- dashboard and copilot evidence support

Governed semantics:

- comparison bucket is normalized to `general` when missing
- price-change direction is derived in-view
- freshness tier `tier_b`

## Genie Suitability

The baseline supports:

- rankings
- movers
- filtered comparisons
- market summaries
- repeatable metric-style questions

The baseline should not be stretched to replace narrative reasoning that belongs in the coded copilot.
