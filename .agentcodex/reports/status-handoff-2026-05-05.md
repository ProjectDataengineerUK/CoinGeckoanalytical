# Status Handoff

- date: `2026-05-05`
- project: `CoinGeckoAnalytical`
- workflow_phase: `ship`
- status: `live-online`

## Current Position

- the final Databricks Apps baseline is considered online
- `cga-analytics` is the primary user-facing surface
- `cga-admin` is the internal operations/governance surface
- 22 Databricks jobs cover data, enrichment, MLOps, governance, compliance, and Sentinela operations
- CI structural validation is green and the current local validation sweep is clean
- future live mutations remain approval-gated through `workflow_dispatch`

## Verified Locally On 2026-05-05

- `python3 -m compileall backend databricks apps -q`
- `python3 databricks/tools/validate_bundle.py`
- `python3 databricks/tools/validate_market_overview_chain.py`
- `python3 databricks/tools/validate_enrichment_chain.py`
- `python3 -m unittest discover -s backend/tests -p 'test_*.py'`
- `python3 -m unittest discover -s databricks/tests -p 'test_*.py'`
- `python3 -m unittest discover -s repo_tests -p 'test_*.py'`
- total tests in this sweep: `355`

## Hardening Applied In This Pass

- reconciled documentation from the old external-frontend posture to the Databricks Apps primary-surface posture
- aligned project-standard and handoff/status artifacts to the live-online scenario
- added Databricks host allowlisting to credentialed backend clients to prevent accidental credential exfiltration to untrusted hosts
- added BFF rate limiting, explicit `api_version` handling, and stronger tenant/runtime identifier validation
- added a manual live-validation workflow outside the full deploy path
- added DR and model-promotion rollback runbooks

## Residual Risks

- notification webhooks for Sentinela are still pending
- environment evidence in staging/prod can still be expanded over time

## Resume Pointers

- `AGENTS.md`
- `.agentcodex/history/CONTEXT-HISTORY.md`
- `.agentcodex/ops/project-standard-status.md`
- `.agentcodex/reports/general-audit-2026-05-05.md`
