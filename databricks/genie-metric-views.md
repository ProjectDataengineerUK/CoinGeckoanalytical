# Genie Metric Views Baseline

## Purpose

Define the first metric-view layer that makes structured analytical NLQ easier for `AI/BI Genie`.

## Initial Metric Views

### `mv_market_rankings`

Measures:

- market cap
- price
- volume 24h
- market cap rank

Filters:

- category
- symbol
- rank range
- observation date

### `mv_top_movers`

Measures:

- change 1h
- change 24h
- change 7d
- volume 24h

Filters:

- positive or negative move
- time window
- minimum market cap
- minimum volume

### `mv_market_dominance`

Measures:

- dominance percentage
- market cap by dominance group

Filters:

- date
- dominance group

### `mv_cross_asset_compare`

Measures:

- price
- market cap
- volume
- 24h change
- 7d change

Filters:

- selected asset set
- date
- comparison group

## Naming Rule

Metric-view names should remain explicit and business-readable to improve NLQ grounding and admin discoverability.
