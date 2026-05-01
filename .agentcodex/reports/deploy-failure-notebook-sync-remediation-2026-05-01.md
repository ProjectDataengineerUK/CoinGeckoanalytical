# Deploy Failure Notebook Sync Remediation

- date: `2026-05-01`
- workflow_phase: `build`
- status: `build-local remediation`
- related_ci_run: `25215006212`
- related_commit: `231b17495719b25f3063d39a4cf64aca528770bf`

## Summary

The CI run for `Add Databricks notebook entrypoints` completed `lint` and `contract`, but failed in the `deploy` job during `Deploy bundle`.

GitHub Actions public job metadata confirmed:

- workflow: `ci`
- run: `25215006212`
- job `lint`: `success`
- job `contract`: `success`
- job `deploy`: `failure`
- failed step: `Deploy bundle`
- skipped after failure: live SQL validation and artifact upload

The job log endpoint requires repository admin access, so the exact Databricks CLI stderr was not available from this environment.

## Root Cause Hypothesis

The only material deploy-surface change in the failed commit was adding Databricks source-format notebooks under `databricks/notebooks/`.

The deploy path packages scheduled production jobs through Databricks Asset Bundles. Those jobs run versioned `spark_python_task` files. The notebooks are workspace-facing review and operator entrypoints, not scheduled job assets.

The likely failure mode is the bundle file sync attempting to upload source-format notebooks as ordinary job bundle files during deploy.

## Remediation

The bundle now excludes notebooks from job file sync:

```yaml
sync:
  exclude:
    - notebooks/**
```

This keeps the production deploy path deterministic:

- scheduled jobs deploy from tested Python and SQL assets
- notebooks remain source-controlled Databricks workspace assets
- notebook import/attachment is an explicit workspace action instead of an implicit job deploy side effect

The bundle validator now enforces that `notebooks/**` remains excluded from job file sync while still requiring the notebook assets to exist in the repository.

## Verification

Executed locally:

```bash
python3 databricks/validate_bundle.py
python3 -m unittest databricks.test_validate_bundle
python3 -m unittest databricks.test_notebook_assets
python3 -m unittest discover -s databricks -p 'test_*.py'
```

Result:

- bundle validation passed
- notebook asset validation passed
- Databricks helper test suite passed with `45` tests

## Next Evidence Step

Commit and push this remediation, then confirm the next GitHub Actions `ci` run completes the `deploy` job successfully before continuing into `WS2 / Slice 2 Public Dashboard Surface`.
