# Freshness And Quality Baseline

## Purpose

Define the first acceptance posture for data freshness and quality before trusted serving.

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

## Quality Gate Before Gold Serving

- source ingestion completed
- schema compatibility passed
- critical metric null checks passed
- freshness watermark computed
- completeness status computed

## User-Facing Rule

No Gold asset should be presented as trusted current intelligence without visible freshness semantics.
