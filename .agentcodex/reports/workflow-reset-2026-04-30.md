# Workflow Reset

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- phase: `build`
- status: `reset in progress`

## Why This Reset Exists

The repository accumulated valid technical scaffolding, but the active build drifted away from the intended workflow logic.

The main failure was sequencing:

- `brainstorm`, `define`, and `design` describe a real product
- the current build produced contracts, helpers, jobs, telemetry, and deploy readiness
- but it still did not close a real end-to-end user-facing product slice

That means the repo looked more advanced than it really was.

## What Was Misclassified

- `frontend/` was being read as part of product progress, but it is still placeholder scope only
- `backend/copilot_mvp.py` was useful prototype work, but not a real delivered copilot flow
- Databricks bundle, preflight, and readiness assets were useful build infrastructure, but not evidence that the product reached `deploy` or `ship`

## Preserved Value

The reset does not discard the existing technical work.

The following remain valid:

- request and telemetry contracts
- backend handoff writers
- Sentinela analysis logic
- Databricks SQL starter surfaces
- Databricks bundle helpers and deployment notes
- CI and local validation surfaces

## Active Slice

The active V1 slice is now explicitly:

`dashboard publico + pergunta analitica + pergunta narrativa + observabilidade minima`

This slice is only complete when:

1. a real frontend exists
2. one dashboard flow is backed by governed data
3. one structured analytics question works through the governed path
4. one narrative copilot question works with freshness/provenance metadata
5. telemetry is tied to the real user path

## Immediate Rules

- do not count scaffolding as delivered product behavior
- do not start `ship` work from local-only helpers
- do not resume deploy hardening until the active slice is real
- keep build reports explicit about whether they represent `prototype`, `placeholder`, `build-local`, or `implemented`

## Verified During Reset

- `python3 -m unittest discover -s backend/tests -p 'test_*.py'`
- `python3 databricks/validate_bundle.py`
- `python3 -m unittest discover -s repo_tests -p 'test_*.py'`
- `python3 -m unittest discover -s databricks -p 'test_*.py'` originally revealed a real drift in `test_bundle_manifest.py` versus `databricks.yml`

## Next Practical Move

Rewrite execution around one honest V1 slice and implement it before returning to deploy or ship concerns.
