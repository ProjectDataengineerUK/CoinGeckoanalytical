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

## Next Step

- wire the analyzer to dashboard or notebook output
- add concrete thresholds by dataset family and route
