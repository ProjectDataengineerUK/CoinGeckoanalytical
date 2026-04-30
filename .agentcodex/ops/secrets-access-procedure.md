# Secrets And Access Procedure

## Purpose

Define the minimum Phase 1 secrets and access procedure required by the access-control and compliance baseline.

## Scope

- Databricks workspace tokens
- Terraform credentials
- service principal credentials
- backend runtime secrets
- external API credentials

## Rules

- secrets must never be committed to the repository
- example tfvars may show placeholders only
- backend code and notebooks must rely on external secret stores or environment injection
- service identity must be separated by workload domain where feasible

## Approved Secret Paths

- CI secrets for deploy and validation
- workspace-managed secret scopes or equivalent approved store
- environment variables injected by trusted execution environments

## Forbidden Patterns

- hard-coded tokens in `*.py`, `*.sql`, `*.tf`, `*.yml`, or markdown examples
- personal credentials reused as service identity
- frontend access to workspace or model-serving credentials directly

## Access Procedure

1. define the workload identity
2. assign the minimum required catalog, schema, or job access
3. store the credential in the approved secret mechanism
4. reference the secret indirectly from CI, Terraform, or runtime configuration
5. record the owner and rotation responsibility

## Rotation Rule

- operator-owned credentials should have a named rotation owner
- service credentials should be rotated on compromise, role change, or environment rebuild
- production credentials should not be shared across dev and staging
