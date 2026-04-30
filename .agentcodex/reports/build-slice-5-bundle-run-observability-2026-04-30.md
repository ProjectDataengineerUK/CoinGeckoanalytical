# Build Slice 5 Bundle Run Observability Report

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `bundle run observability`

## Delivered

- extended `backend/sentinela.py` to analyze Databricks bundle run events
- added `contracts/bundle_run_event.schema.json`
- updated `backend/tests/test_sentinela.py` with bundle failure and cancel coverage
- documented bundle failure handling in `databricks/bundle-manifest.md`, `databricks/ops_jobs_manifest.md`, and `databricks/README.md`

## Verification

- bundle failures now block release readiness
- cancelled bundle runs are treated as release blockers
- bundle alerts are returned alongside telemetry alerts
- the local backend and bundle validation suites still pass

## Remaining Work

- wire real Databricks job run results into the bundle run event contract
- connect alerts to the active notification channel used by Sentinela
- surface bundle run failures in the ops readiness dashboard
