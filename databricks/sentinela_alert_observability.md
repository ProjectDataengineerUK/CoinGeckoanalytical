# Sentinela Alert Observability Baseline

## Purpose

Land normalized Sentinela alerts into Databricks and expose a governed backlog and readiness view.

## Implementation Asset

- executable baseline: `sentinela_alert_observability.sql`

## Surface

- `ops_sentinela_alerts`: landing table for normalized alert events
- `ops_sentinela_alerts_normalized`: normalized alert classification
- `ops_sentinela_alert_backlog`: backlog grouped by alert kind and family
- `ops_sentinela_alert_readiness`: alert-state summary for ops readiness

## Operational Rules

- bundle and runtime alerts are both first-class release signals
- alert backlog should be visible to Sentinela and the dashboard
- alert families help separate runtime noise from bundle/control-plane failures

## Next Step

- ingest Sentinela alert handoff files into `ops_sentinela_alerts`
- surface the alert backlog in the readiness dashboard
- connect bundle/job failures to alert handoff generation
