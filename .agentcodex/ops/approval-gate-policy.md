# Approval Gate Policy

## Purpose

Keep every mutable Databricks or Terraform action explicitly approved by the operator in chat before execution.

## Policy

- no push-triggered Databricks execution
- no push-triggered Terraform apply
- all mutable workspace actions require a manual approval gate
- approval state must be visible in repo-local artifacts before execution

## Approved Actions

Use `workflow_dispatch` only for:

- `ci.yml` with `confirm_deploy=true`
- `terraform.yml` with `confirm_apply=true`
- `bronze-migration.yml` with `confirm_migration=true`

## Approval States

- `pending`: the action is prepared but not approved yet
- `approved`: the operator has explicitly approved the action in chat
- `rejected`: the operator declined or deferred the action
- `executed`: the workflow already ran successfully

## Operator Rule

- treat chat approval as the source of truth
- update the durable approval status artifact when an action is prepared, approved, or executed
- do not infer approval from a push event

## Implementation Note

The workflows stay manual, but the repo can keep a companion status report under `.agentcodex/reports/` so approval intent is visible right after each publish/update.
