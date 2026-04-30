# Cost Controls Policy

## Purpose

Define the minimum Phase 1 cost-control posture for CoinGeckoAnalytical across dashboard, Genie, copilot, and operations workloads.

## Cost Domains

- `dashboard route cost`
- `Genie analytical route cost`
- `copilot route cost`
- `operational jobs and refresh cost`

## Route Threshold Baseline

These thresholds must stay aligned with the Sentinela policy layer:

- `dashboard.market-overview`: `max_cost_estimate = 0.005`
- `genie.market-rankings`: `max_cost_estimate = 0.02`
- `copilot.market-interpretation`: `max_cost_estimate = 0.05`
- `internal ops route`: `max_cost_estimate = 0.03`

## Budget Control Rules

- every routed request must emit `cost_estimate` when the route can measure it
- cost anomalies must surface as reviewable Sentinela events
- cost spikes should not remain only in logs; they must affect readiness posture
- product-facing routes should prefer deterministic governed retrieval before expensive narrative expansion

## Operator Action Thresholds

### Review

Trigger review when:

- a route crosses its single-request threshold
- route cost trend rises for three consecutive observation windows

### Hold

Trigger hold when:

- route cost and latency both breach target
- copilot cost anomaly repeats without policy adjustment
- operational refresh cost makes readiness monitoring itself unstable

## Environment Rule

- dev may tolerate exploratory spikes briefly
- staging should approximate release thresholds
- prod must use the strictest thresholds and alerting

## Evidence Rule

Do not claim Phase 1 cost control is complete unless route thresholds, telemetry fields, and operator actions are all present in repo artifacts and later visible in live usage evidence.
