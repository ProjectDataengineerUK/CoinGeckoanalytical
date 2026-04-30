# Build Slice 5 Bundle Validation Report

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `databricks bundle validation fallback`

## Delivered

- created `databricks/validate_bundle.py`
- created `databricks/test_validate_bundle.py`
- updated `databricks/bundle-manifest.md` with local and CLI validation commands
- indexed the helper in `databricks/README.md`

## Verification

- local bundle validation passes against `databricks/databricks.yml`
- the helper checks bundle name, required jobs, schedules, environment keys, and script paths
- the bundle test suite passes locally

## Remaining Work

- run `databricks bundle validate` and `databricks bundle deploy` in an environment with the Databricks CLI
- publish the bundle into a live dev workspace target
- connect failed bundle runs to Sentinela and the ops readiness dashboard
