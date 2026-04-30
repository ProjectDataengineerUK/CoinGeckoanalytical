# Governance And Ownership

## Purpose

Define ownership and governance responsibilities for the first governed CoinGeckoAnalytical build slice.

## Ownership Matrix

### Data Platform

- owns CoinGecko ingestion posture
- owns canonical asset dimensions and Silver normalization
- owns Gold analytical contract fields and freshness publication

### Product Analytics

- owns dashboard semantic intent
- owns governed analytical question catalog
- owns the meaning of market ranking, movers, dominance, and comparison outputs

### Platform Ops

- owns telemetry ingestion posture
- owns Sentinela alert interpretation inputs
- owns readiness and degraded-mode review baselines

### Governance Admin

- owns approval posture for policy-sensitive changes
- owns audit-review escalation path
- owns future retention and control-mapping decisions

## Asset Ownership Rules

- every Gold asset must have one named owner group
- every metric view must declare the product question it supports
- every telemetry route must map to one operational owner
- every alert rule must map to an operator review path

## Required Governance Metadata

- `owner`
- `source_system`
- `lineage_sources`
- `freshness_target`
- `quality_checks`
- `tenant_scope`
- `serving_surface`
- `review_owner`

## Initial Review Gates

- no Gold asset is trusted without freshness and quality semantics
- no governed AI route is trusted without telemetry and provenance
- no operational alert is trusted without source and timestamp metadata
- no route is treated as production-candidate behavior without a named owner
