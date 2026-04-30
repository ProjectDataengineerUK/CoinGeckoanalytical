# Ops Readiness Dashboard Surface

## Purpose

Provide a notebook- and dashboard-friendly view over Databricks telemetry observability and Gold serving readiness.

## Implementation Asset

- executable surface: `ops_readiness_dashboard.sql`

## Dashboard Tiles

- `ops_ready_overview`: overall readiness summary across routes
- `ops_route_readiness_latest`: latest readiness state per route
- `ops_alert_backlog`: alert backlog grouped by kind and route
- `ops_cost_latency_trend`: route-level cost and latency trend by hour

## Operational Use

- review whether the platform is globally `ready` or still in `hold`
- inspect the latest status per route for `genie`, `copilot`, `dashboard_api`, and `internal_app`
- scan alert backlog to see which operational issue is accumulating
- correlate cost, latency, and freshness drift over time

## Next Step

- render these queries in a Databricks dashboard or notebook
- connect the dashboard to the actual telemetry landing table and release-readiness checks
