-- Databricks Genie Metric Views Baseline
-- Purpose: governed metric views that expose reusable business semantics
-- for AI/BI Genie, dashboards, and SQL consumers.

CREATE OR REPLACE VIEW mv_market_rankings
WITH METRICS LANGUAGE YAML AS
$$
  version: 1.1
  comment: "Market cap, price, and liquidity metrics for market ranking analysis."
  source: cgadev.market_gold.gold_market_rankings
  filter: observed_at IS NOT NULL

  dimensions:
    - name: asset_id
      expr: asset_id
      display_name: Asset ID
    - name: symbol
      expr: symbol
      display_name: Symbol
    - name: category
      expr: category
      display_name: Category
    - name: observed_at
      expr: observed_at
      display_name: Observed At

  measures:
    - name: market_cap_usd
      expr: MAX(market_cap_usd)
      display_name: Market Cap USD
    - name: price_usd
      expr: MAX(price_usd)
      display_name: Price USD
    - name: volume_24h_usd
      expr: MAX(volume_24h_usd)
      display_name: Volume 24h USD
    - name: market_cap_rank
      expr: MIN(market_cap_rank)
      display_name: Market Cap Rank
$$;

CREATE OR REPLACE VIEW mv_top_movers
WITH METRICS LANGUAGE YAML AS
$$
  version: 1.1
  comment: "Short-horizon move metrics for positive and negative market motion."
  source: cgadev.market_gold.gold_top_movers
  filter: observed_at IS NOT NULL

  dimensions:
    - name: asset_id
      expr: asset_id
      display_name: Asset ID
    - name: symbol
      expr: symbol
      display_name: Symbol
    - name: window_id
      expr: window_id
      display_name: Window ID
    - name: move_direction_24h
      expr: move_direction_24h
      display_name: 24h Direction
    - name: observed_at
      expr: observed_at
      display_name: Observed At

  measures:
    - name: price_change_pct_1h
      expr: MAX(price_change_pct_1h)
      display_name: 1h Change Percent
    - name: price_change_pct_24h
      expr: MAX(price_change_pct_24h)
      display_name: 24h Change Percent
    - name: price_change_pct_7d
      expr: MAX(price_change_pct_7d)
      display_name: 7d Change Percent
    - name: volume_24h_usd
      expr: MAX(volume_24h_usd)
      display_name: Volume 24h USD
    - name: market_cap_usd
      expr: MAX(market_cap_usd)
      display_name: Market Cap USD
$$;

CREATE OR REPLACE VIEW mv_market_dominance
WITH METRICS LANGUAGE YAML AS
$$
  version: 1.1
  comment: "Dominance metrics for BTC, ETH, stablecoins, and other market groups."
  source: cgadev.market_gold.gold_market_dominance
  filter: observed_at IS NOT NULL

  dimensions:
    - name: observed_at
      expr: observed_at
      display_name: Observed At
    - name: dominance_group
      expr: dominance_group
      display_name: Dominance Group
    - name: dominance_band
      expr: dominance_band
      display_name: Dominance Band

  measures:
    - name: market_cap_usd
      expr: MAX(market_cap_usd)
      display_name: Market Cap USD
    - name: dominance_pct
      expr: MAX(dominance_pct)
      display_name: Dominance Percent
$$;

CREATE OR REPLACE VIEW mv_cross_asset_compare
WITH METRICS LANGUAGE YAML AS
$$
  version: 1.1
  comment: "Side-by-side comparison metrics for selected assets."
  source: cgadev.market_gold.gold_cross_asset_comparison
  filter: observed_at IS NOT NULL

  dimensions:
    - name: asset_id
      expr: asset_id
      display_name: Asset ID
    - name: symbol
      expr: symbol
      display_name: Symbol
    - name: observed_at
      expr: observed_at
      display_name: Observed At
    - name: correlation_bucket
      expr: correlation_bucket
      display_name: Correlation Bucket

  measures:
    - name: price_usd
      expr: MAX(price_usd)
      display_name: Price USD
    - name: market_cap_usd
      expr: MAX(market_cap_usd)
      display_name: Market Cap USD
    - name: volume_24h_usd
      expr: MAX(volume_24h_usd)
      display_name: Volume 24h USD
    - name: price_change_pct_24h
      expr: MAX(price_change_pct_24h)
      display_name: 24h Change Percent
    - name: price_change_pct_7d
      expr: MAX(price_change_pct_7d)
      display_name: 7d Change Percent
$$;
