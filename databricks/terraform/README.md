# Terraform

Terraform baseline for Phase 1 governed Databricks infrastructure.

This area should own:

- environment-level Databricks foundation
- Unity Catalog namespace creation
- grants and execution identities
- environment variable separation
- Terraform-managed job and policy baseline for operational workloads

The goal is not to replace `databricks.yml`.

The goal is to complement bundle deployment with reproducible infrastructure-as-code for maturity-oriented controls.
