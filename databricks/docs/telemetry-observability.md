# Telemetry Observability Baseline

## Purpose

Normalize usage telemetry for `Genie`, copilot, dashboard API, and internal operational surfaces into Databricks so Sentinela can evaluate readiness from governed data instead of ad hoc runtime state.

## Implementation Asset

- executable baseline: `telemetry-observability.sql`

## Surface

- `ops_usage_events`: Delta landing table for normalized usage telemetry
- `ops_usage_events_normalized`: enriched view with time buckets and bands
- `ops_route_health`: hourly route summary for latency, cost, tokens, and freshness
- `ops_release_readiness`: cross-check of telemetry health and Gold readiness
- `ops_alert_queue`: alert-style projection for dashboards and notebook inspection

## Operational Rules

- every usage event must carry request, tenant, route, engine, latency, and response status
- freshness metadata should be visible for all AI-assisted answers
- route-specific thresholds are encoded for Genie, copilot, dashboard API, and internal app traffic
- Gold readiness must be green before release readiness can go green

## Next Step

- connect the landing table to actual telemetry ingestion from backend and Databricks serving events
- render `ops_release_readiness` in a dashboard or notebook for operations review
