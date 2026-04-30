# Freshness And Quality Baseline

## Purpose

Define the first acceptance posture for data freshness and quality before trusted serving.

## Implementation Asset

- executable baseline: `freshness_quality_baseline.sql`

## Freshness Tiers

### Tier A

Use for:

- market rankings
- top movers
- dominance snapshots

Expectation:

- near-real-time or best available high-frequency refresh

### Tier B

Use for:

- comparative analytics
- enriched summary views

Expectation:

- frequent refresh with documented lag tolerance

### Tier C

Use for:

- secondary enrichment views
- lower-priority supporting datasets

Expectation:

- scheduled refresh with explicit warning when stale

## Concrete Serving Checks

The SQL baseline turns the policy into three operational views:

- `gold_freshness_status`
- `gold_quality_status`
- `gold_serving_readiness`

The freshness view records:

- latest observation time
- freshness age in minutes
- target minutes by asset
- freshness state (`within_target` or `stale`)

The quality view records:

- row count
- critical null rows
- duplicate key rows
- numeric outlier rows
- quality state (`pass` or `review`)

The readiness view joins both and emits:

- `serve` when freshness and quality are both green
- `hold` otherwise

## Quality Gate Before Gold Serving

- source ingestion completed
- schema compatibility passed
- critical metric null checks passed
- freshness watermark computed
- completeness status computed

## User-Facing Rule

No Gold asset should be presented as trusted current intelligence without visible freshness semantics.
