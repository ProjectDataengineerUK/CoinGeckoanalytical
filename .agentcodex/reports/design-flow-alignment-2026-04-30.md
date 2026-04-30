# Design Flow Alignment

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- source: `.agentcodex/features/DESIGN_coingeckoanalytical.md`
- intent: `normalize build execution to the actual design flow`

## Canonical Design Flow

The design defines the product in this order:

1. `source ingestion layer`
2. `Bronze layer`
3. `Silver layer`
4. `Gold layer`
5. `serving routes`
6. `backend-for-frontend`
7. `external web frontend`
8. `Sentinela operations plane`

This means the first valid execution chain for the active product family is:

1. ingest source observations
2. land them in `bronze_market_snapshots`
3. normalize them in Silver views
4. publish governed Gold assets
5. expose those assets to:
   - `dashboard.market-overview`
   - `genie.market-rankings`
   - `copilot.market-interpretation`
6. only then close user-facing routes and readiness interpretation

## Selected First Product Family

The active family remains `market overview intelligence`.

Canonical dependency chain:

1. `CoinGecko Market API`
2. `bronze_market_snapshots`
3. `silver_market_snapshots`
4. `silver_market_changes`
5. `silver_market_dominance`
6. `silver_cross_asset_comparison`
7. `gold_market_rankings`
8. `gold_top_movers`
9. `gold_market_dominance`
10. `gold_cross_asset_comparison`
11. `mv_market_rankings`
12. `mv_top_movers`
13. `mv_market_dominance`
14. `mv_cross_asset_compare`
15. `backend/routing_bff.py`
16. consuming routes: `dashboard`, `Genie`, `copilot`

## Build Rule Derived From Design

- `dashboard` is not a starting point; it is a consumer of governed Gold assets
- `Genie` is not a starting point; it is a consumer of governed Gold metric views
- `copilot` is not a starting point; it is a consumer of governed evidence assets plus policy-aware orchestration
- `Sentinela` is not a substitute for product completion; it interprets the health of already-real routes

## Current Position Against Design

- `source ingestion`: partially defined, not yet proven as a live executed path
- `Bronze`: structurally defined in SQL, but missing live ingestion execution evidence
- `Silver`: structurally defined in SQL, but missing live execution evidence
- `Gold`: structurally defined in SQL, but missing live serving evidence
- `serving routes`: partially implemented in backend, still using demo or stub behavior in key paths
- `frontend`: still placeholder
- `ops interpretation`: materially implemented in repo artifacts, but not yet tied to fully real served flows

## Immediate Design-Aligned Next Move

Close the first executable `data and AI plane` chain before treating any user-facing surface as delivered:

1. prove ingestion shape for the first source
2. prove Bronze materialization
3. prove Silver normalization
4. prove Gold serving assets
5. bind backend retrieval to those governed assets
6. only after that treat `dashboard.market-overview` as an implementation target

## Resulting Delivery Order

1. `data execution baseline`
2. `dashboard`
3. `Genie`
4. `copilot`
5. `Sentinela route-aware operations`
6. `deploy evidence`
7. `ship decision`
