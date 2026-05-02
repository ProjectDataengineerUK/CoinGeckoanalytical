# Notification Policy

## Purpose

Define the notification contract for bundle failures, runtime alerts, and readiness blockers.

## Handoff

- backend notification records are emitted through `backend/notification_handoff.py`
- the handoff format is a JSON array of notification objects
- the content should be ingested into a governed alert table or routed to an external notifier

## Notification Classes

- `bundle_failure`
- `bundle_cancelled`
- `error_spike`
- `latency_breach`
- `cost_anomaly`
- `freshness_gap`
- `token_spike`

## Operational Targets

- on-call notification for release blockers
- dashboard visibility for backlog and status
- explicit source and timestamp metadata on every notification

## Next Step

- connect the notification handoff to the chosen external notifier or Databricks alert sink
- keep the notification contract in sync with `contracts/sentinela_alert_event.schema.json`
