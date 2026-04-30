# Build Slice 1 Market Overview Chain Validation

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `WS1 market overview chain validation`
- result_type: `implemented`

## Delivered

- created `databricks/validate_market_overview_chain.py`
- created `databricks/test_validate_market_overview_chain.py`
- updated `.github/workflows/ci.yml`

## What This Closes

- the repo now has a structural validator for the first governed data family from source-ingestion entrypoint through Bronze, Silver, Gold, and Genie metric views
- CI now fails if the canonical `market overview intelligence` dependency chain drifts
- the active build no longer depends only on prose lineage to claim the first governed family is wired coherently

## Verification

- local validation passes for the current repository state
- the validator checks Bronze, Silver, Gold, metric-view definitions, key dependencies, lineage markers, and the market-source ingestion target

## Remaining Work

- execute the validated chain in a live Databricks workspace
- materialize real data into Bronze and confirm downstream rows in Silver and Gold
- bind backend retrieval and Genie execution to the served governed assets
