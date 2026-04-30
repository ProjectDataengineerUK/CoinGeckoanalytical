# Sentinela

Operational baseline for the CoinGeckoAnalytical multi-agent plane.

## Watch List

- pipeline freshness failures
- data quality degradation
- missing or partial Gold publishes
- copilot error spikes
- token-cost anomalies
- missing provenance or freshness fields in AI answers
- tenant-isolation or access-control anomalies

## Current Behavior

- analyze usage telemetry events
- summarize the operational state
- emit alert records for latency, cost, freshness, errors, and token spikes
- evaluate release readiness with route-specific thresholds and escalation policies

## Next Step

- wire the analyzer to dashboard or notebook output
- connect the readiness checks to actual telemetry ingestion
