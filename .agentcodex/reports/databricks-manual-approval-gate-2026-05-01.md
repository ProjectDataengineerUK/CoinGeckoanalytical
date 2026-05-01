# Databricks Manual Approval Gate

## Summary

The repository no longer allows automatic Databricks bundle deployment on `push`. Databricks execution now requires explicit `workflow_dispatch` approval in `ci.yml`.

## What Changed

- `ci.yml` now exposes `confirm_deploy`
- the `deploy` job now runs only when `workflow_dispatch` is used with `confirm_deploy=true`
- the repo-local daily flow now documents the manual deployment gate
- the context history records the approval-only policy for Databricks actions

## Why

- the operator wants to approve every Databricks action explicitly before execution
- this removes accidental workspace-side changes from push-driven automation

## Validation

- `python3 -m unittest discover -s backend/tests -p 'test_*.py'` passed
- `python3 -m unittest discover -s databricks -p 'test_*.py'` passed
- `python3 -m unittest discover -s repo_tests -p 'test_*.py'` passed
- `python3 databricks/validate_bundle.py` passed

## Current Policy

- `push` validates code and contracts only
- `workflow_dispatch` with `confirm_deploy=true` is required for Databricks deploy
- `workflow_dispatch` with `confirm_apply=true` is required for Terraform apply
