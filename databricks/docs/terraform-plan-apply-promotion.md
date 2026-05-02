# Terraform Plan Apply Promotion

## Purpose

Provide the minimum operator runbook for Phase 1 Terraform execution across `dev`, `staging`, and `prod`.

## Preconditions

- Terraform installed
- Databricks workspace host and token available
- target principals and groups created or mapped
- target bundle root and cluster id known for the environment

## Execution Order

1. validate variables for the target environment
2. run `terraform init`
3. run `terraform plan`
4. review catalog, schema, grant, policy, and job deltas
5. apply to `dev`
6. validate Databricks workspace state
7. promote the same reviewed change set to `staging`
8. promote to `prod` only after verification evidence is captured

## Example Commands

```bash
cd /home/user/Projetos/CoinGeckoanalytical/databricks/terraform
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```

For staging and prod:

```bash
terraform plan -var-file=staging.tfvars
terraform apply -var-file=staging.tfvars
terraform plan -var-file=prod.tfvars
terraform apply -var-file=prod.tfvars
```

## Mandatory Review Points

- catalog and schema names match the intended environment
- grants do not widen end-user or backend access accidentally
- operational jobs point to the correct bundle root and cluster target
- cluster policy values match the approved ops baseline

## Promotion Rule

Do not promote the Terraform change beyond `dev` unless:

- the plan output was reviewed
- the apply succeeded
- the Databricks workspace reflects the expected namespace and grants
- operational jobs are visible with the correct names and principals

## Evidence Rule

Persist plan/apply evidence into `.agentcodex/reports/` before treating the Terraform baseline as live Phase 1 completion evidence.
