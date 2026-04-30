# Terraform Phase 1 Baseline

## Purpose

Define the minimum Terraform scope required for CoinGeckoAnalytical to claim a serious Phase 1 base aligned with DataOps, MLOps, and LLMOps maturity expectations.

## Why Terraform Is In Phase 1

Databricks bundles are useful for deploying bundle-scoped assets, but they do not replace governed infrastructure-as-code for:

- Unity Catalog structure
- grants and principal binding
- environment separation
- service principals and execution identity
- workspace-level policies and shared foundations

For this project, a maturity-5 claim is weak unless Terraform or equivalent IaC materializes those controls.

## Required Terraform Scope

### 1. Environment Foundation

- dev, staging, and prod workspace target separation
- environment variables and shared naming conventions
- remote state posture

### 2. Unity Catalog Foundation

- catalogs per environment
- schemas for Bronze, Silver, Gold, AI, ops, audit, and reference data
- ownership assignment

### 3. Access And Grants

- product backend read posture
- Genie governed-view posture
- copilot evidence-read posture
- platform-ops access to observability assets
- governance-admin access to audit assets

### 4. Execution Identity

- service principals for ingestion, pipelines, ops, and audit jobs
- role-to-workload mapping

### 5. Databricks Runtime Foundation

- cluster or compute policies where required
- shared job configuration baseline
- secret or external-reference wiring posture

## Phase 1 Acceptance Rule

Phase 1 is not complete if:

- Unity Catalog exists only as SQL and docs but not as IaC
- grants are manual
- principals are manual
- environment separation is convention-only
- deploy reproducibility depends on workspace clicking

## Minimum Deliverables

- Terraform root for Databricks environment setup
- environment-specific variable files
- Unity Catalog Terraform resources
- principal and grant Terraform resources
- Terraform-managed baseline for operational jobs and cluster policy
- operator guidance for plan/apply and promotion
