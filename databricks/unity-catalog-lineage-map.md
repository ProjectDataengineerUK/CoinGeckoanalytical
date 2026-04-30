# Unity Catalog Lineage Map

## Purpose

Expose the first operational lineage map required to treat Phase 1 as a governed base instead of a design-only posture.

## Market Overview Intelligence Lineage

### Source To Bronze

- `CoinGecko API`
  - lands into `market_bronze.bronze_market_snapshots`
  - preserved fields include source identity, observed time, ingestion time, ranking, price, volume, and market cap context

### Bronze To Silver

- `market_bronze.bronze_market_snapshots`
  -> `market_silver.silver_market_snapshots`
  - deduplication and canonicalization

- `market_silver.silver_market_snapshots`
  -> `market_silver.silver_market_changes`
  - 1h, 24h, and 7d derived changes

- `market_silver.silver_market_snapshots`
  -> `market_silver.silver_market_dominance`
  - grouped dominance semantics

- `market_silver.silver_market_snapshots`
  -> `market_silver.silver_cross_asset_comparison`
  - comparison bucket and movement context

### Silver To Gold

- `market_bronze.bronze_market_snapshots`
  -> `market_gold.gold_market_rankings`

- `market_silver.silver_market_changes`
  -> `market_gold.gold_top_movers`

- `market_silver.silver_market_dominance`
  -> `market_gold.gold_market_dominance`

- `market_silver.silver_cross_asset_comparison`
  -> `market_gold.gold_cross_asset_comparison`

### Gold To Serving

- `market_gold.gold_market_rankings`
  -> `ai_serving.mv_market_rankings`
  -> `Genie analytical scope`

- `market_gold.gold_top_movers`
  -> `ai_serving.mv_top_movers`
  -> `Genie analytical scope`

- `market_gold.gold_market_dominance`
  -> `ai_serving.mv_market_dominance`
  -> `dashboard.market-overview`

- `market_gold.gold_cross_asset_comparison`
  -> `ai_serving.mv_cross_asset_compare`
  -> `dashboard.market-overview` and `copilot.market-interpretation`

### Operational Lineage

- `backend/dashboard_market_overview.py`
  -> `ops_observability.ops_usage_events`

- `backend/copilot_mvp.py`
  -> `ops_observability.ops_usage_events`

- `backend/sentinela_alert_handoff.py`
  -> `ops_observability.ops_sentinela_alerts`

## Operational Verification Rule

For Phase 1, lineage is sufficient only when:

- each central asset has a governed namespace
- each serving route points to cataloged assets
- operational telemetry and alert datasets are also inside governed namespaces
