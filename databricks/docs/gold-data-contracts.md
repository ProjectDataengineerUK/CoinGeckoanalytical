# Gold Data Contracts

## Purpose

Capture the first contract expectations for Gold analytical serving.

## Contract Rules

- every Gold asset must have a named owner
- every Gold asset must publish freshness expectation
- every Gold asset must declare critical dimensions and measures
- every Gold asset must have a quality gate before trusted serving
- every Gold asset used by `Genie` must be safe for governed analytical access

## Required Contract Fields

- `asset_name`
- `owner`
- `description`
- `freshness_target`
- `freshness_measurement`
- `primary_dimensions`
- `primary_measures`
- `quality_checks`
- `lineage_sources`
- `tenant_scope`

## Initial Quality Expectations

- null checks on critical identifiers
- timestamp presence on every served row family
- duplicate control on ranking keys where applicable
- outlier detection or bounded validation for critical numeric fields
- freshness watermark available for every tenant-facing served dataset

## Tenant Scope Rule

If a Gold asset is tenant-neutral market intelligence, document it as shared analytical reference data.

If a Gold asset includes tenant-sensitive usage or audit data, document it as tenant-scoped and protect it accordingly.
