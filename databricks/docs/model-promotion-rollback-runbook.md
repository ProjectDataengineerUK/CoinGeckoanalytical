# Model Promotion And Rollback Runbook

## Purpose

Make model promotion and rollback explicit enough for a Level 5 MLOps posture.

## Promotion Flow

1. Train a new version through `train_market_model_job`.
2. Validate offline metrics and drift posture.
3. Assign or refresh the `candidate` alias.
4. Perform controlled verification against the active data/serving contract.
5. Re-point `champion` only after approval.
6. Record the promoted version, alias change, and evidence in `.agentcodex/reports/`.

## Rollback Flow

1. Identify the last known-good `champion` version.
2. Re-point the `champion` alias to that version.
3. Re-run batch scoring if required by the incident.
4. Confirm downstream tables and serving endpoints reflect the rolled-back alias.
5. Record the rollback cause, version ids, and validation evidence.

## Operational Rules

- Never delete the prior champion until rollback risk is closed.
- Never promote directly from `draft` to `champion`.
- Treat alias updates as approval-gated operations.
- Keep validation evidence tied to the exact version promoted or rolled back.

## Required Evidence

- model version id
- alias state before and after
- offline evaluation summary
- drift status
- post-change validation result
