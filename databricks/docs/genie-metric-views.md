# Genie Metric Views Baseline

## Purpose

Define the metric-view layer that makes structured analytical NLQ easier for `AI/BI Genie`.

## Implementation Asset

- executable metric-view DDL: `genie_metric_views.sql`

## Published Metric Views

### `mv_market_rankings`

Backs:

- market cap
- price
- volume 24h
- market cap rank

Source:

- `gold_market_rankings`

Useful filters:

- category
- symbol
- observation date

### `mv_top_movers`

Backs:

- change 1h
- change 24h
- change 7d
- volume 24h

Source:

- `gold_top_movers`

Useful filters:

- positive or negative move
- time window
- minimum market cap
- minimum volume

### `mv_market_dominance`

Backs:

- dominance percentage
- market cap by dominance group

Source:

- `gold_market_dominance`

Useful filters:

- date
- dominance group

### `mv_cross_asset_compare`

Backs:

- price
- market cap
- volume
- 24h change
- 7d change

Source:

- `gold_cross_asset_comparison`

Useful filters:

- selected asset set
- date
- comparison group

## Naming Rule

Metric-view names should remain explicit and business-readable to improve NLQ grounding and admin discoverability.

## Publication Rule

Use the YAML DDL form supported by Databricks metric views:

```sql
CREATE OR REPLACE VIEW <name> WITH METRICS LANGUAGE YAML AS
$$
  version: 1.1
  comment: "..."
  source: <gold_view>
  ...
$$;
```
