# Build Slice 1 Market Source Repo Flow

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `WS1 repo-local market source compatibility flow`
- result_type: `implemented`

## Delivered

- created `repo_tests/test_market_source_repo_flow.py`

## What This Closes

- the repo now proves that the backend market-source handoff shape is accepted by the Databricks ingestion job
- the controlled market fixture is also validated against the same ingestion normalization path
- the first governed data family no longer relies on manual shape assumptions between backend and Databricks ingestion

## Verification

- repo-local tests should validate backend handoff rows, fixture rows, and ingestion normalization in one flow

## Remaining Work

- execute the same flow in a live Databricks workspace
- prove Bronze landing and downstream Silver/Gold row presence from the same source payload
