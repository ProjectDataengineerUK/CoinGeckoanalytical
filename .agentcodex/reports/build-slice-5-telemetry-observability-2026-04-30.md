# Build Slice 5 Telemetry Observability Report

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `telemetry observability baseline`

## Delivered

- created `databricks/telemetry-observability.sql`
- created `databricks/telemetry-observability.md`
- aligned Sentinela route thresholds with `usage_event` telemetry routes
- extended Sentinela readiness checks to cover `dashboard_api` and `internal_app`

## Verification

- the observability baseline expresses a governed landing table for usage telemetry
- route summaries and readiness checks are now definable inside Databricks
- release readiness can be reasoned about from the telemetry layer plus Gold readiness
- Sentinela unit tests pass with route-specific readiness coverage

## Remaining Work

- connect the landing table to actual backend event emission
- surface `ops_release_readiness` in a Databricks dashboard or notebook
- add a retention and partitioning policy for operational telemetry
