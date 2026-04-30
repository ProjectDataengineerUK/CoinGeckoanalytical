# Sentinela Baseline

## Purpose

Define the first operational sentinela layer for CoinGeckoAnalytical.

## What Sentinela Watches

- pipeline freshness failures
- data quality degradation
- missing or partial Gold publishes
- copilot error spikes
- token-cost anomalies
- missing provenance or freshness fields in AI answers
- tenant-isolation or access-control anomalies

## Minimum Signals

- dataset freshness watermark
- Gold publish success or failure
- quality rule pass rate
- request latency
- token usage by route
- cost estimate by tenant
- grounded-answer coverage
- policy refusal count

## Minimum Outputs

- alert events
- anomaly summary
- operator-facing runbook pointers
- audit trail references

## Phase Guidance

- before build: define the event model and thresholds
- during build: instrument the telemetry sources
- before ship: validate alerts, dashboards, and operator workflows
