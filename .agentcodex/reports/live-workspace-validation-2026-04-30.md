# Live Workspace Validation - 2026-04-30

## Scope

- project: `CoinGeckoAnalytical`
- commit: `9e0e299993f10491e54e59093853531c428d05b3`
- workflow: `ci`
- run: `25198087949`
- run URL: `https://github.com/ProjectDataengineerUK/CoinGeckoanalytical/actions/runs/25198087949`
- validation time: `2026-05-01T01:36:20Z` to `2026-05-01T01:41:08Z`

## CI Job Evidence

GitHub Actions API confirmed these jobs for the run:

| Job | Status | Conclusion | Started | Completed |
|---|---|---|---|---|
| `lint` | `completed` | `success` | `2026-05-01T01:36:28Z` | `2026-05-01T01:36:37Z` |
| `contract` | `completed` | `success` | `2026-05-01T01:36:38Z` | `2026-05-01T01:36:50Z` |
| `deploy` | `completed` | `success` | `2026-05-01T01:36:52Z` | `2026-05-01T01:41:08Z` |

The `deploy` job steps also completed successfully:

- install Databricks CLI
- check deploy prerequisites
- validate bundle
- deploy bundle
- run live SQL validation
- upload live SQL validation artifact

## Artifact Evidence

GitHub Actions API confirmed one artifact:

- artifact name: `databricks-live-sql-validation`
- artifact id: `6743687233`
- digest: `sha256:9668ef9fe53be44598227a862bd91c4fee22eaf8f528ee2a46506e5a0419dc9b`
- size: `635` bytes
- created_at: `2026-05-01T01:41:06Z`
- expires_at: `2026-07-30T01:36:20Z`

The artifact download endpoint requires authenticated GitHub access from this environment, so the row-count JSON was not available locally during this pass.

## Live Validation Status

Confirmed:

- bundle deploy reached the Databricks workspace
- deploy job completed successfully after the previous `data_platform` principal failure was remediated
- live SQL validation step completed successfully
- `databricks-live-sql-validation` artifact was uploaded

Pending:

- inspect the artifact JSON
- record Bronze, Silver, Gold, and Genie metric view row counts
- classify zero-row checks, if any
- capture Databricks run URLs from authenticated Actions logs if needed

## Project Standard Decision

- `deploy`: can move from `partial` to `implemented` because the live Databricks deploy job completed successfully and uploaded validation evidence.
- `validacao`: remains `partial` until the artifact JSON row counts are inspected and persisted.
- `operacao`: remains `partial` because incident/runbook/operator evidence is not yet complete, even though operational jobs now pass in the deploy path.

## Next Step

Download the `databricks-live-sql-validation` artifact from the authenticated GitHub UI or CLI and paste or persist the JSON into this report.

After row counts are captured, update:

- `.agentcodex/ops/project-standard-status.md`
- this report's pending row-count section
- `.agentcodex/reports/status-handoff-2026-04-30.md`
