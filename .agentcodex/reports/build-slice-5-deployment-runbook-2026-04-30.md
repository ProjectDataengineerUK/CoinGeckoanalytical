# Build Slice 5 Deployment Runbook Report

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `databricks deployment runbook`

## Delivered

- created `databricks/deployment_runbook.md`
- indexed the runbook in `databricks/README.md`
- linked the runbook from `databricks/bundle-manifest.md`

## Verification

- the runbook defines the preflight, deploy, verification, and rollback order
- the commands are aligned with the bundle and scheduled jobs already in the repo
- the runbook covers telemetry, bundle-run, and Sentinela alert surfaces

## Remaining Work

- execute the runbook in a Databricks-enabled environment
- wire the steps into CI/CD or a release checklist
- confirm workspace permissions and rollback paths against the live target
