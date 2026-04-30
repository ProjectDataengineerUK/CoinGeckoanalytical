# Daily Flow

## Purpose

Define the repo-local daily operating ritual for building CoinGeckoAnalytical with AgentCodex.

## Start Of Day

1. Read `.agentcodex/history/CONTEXT-HISTORY.md`.
2. Read the active design artifact.
3. Confirm the current priority slice.
4. Record any scope or architecture shift in `.agentcodex/history/CONTEXT-HISTORY.md`.

## Planning Sequence

1. Check the active phase: `brainstorm`, `define`, `design`, `build`, or `ship`.
2. Select the relevant specialists from `.agentcodex/reports/specialist-routing-matrix-2026-04-29.md`.
3. Confirm whether the task changes architecture, contracts, governance, or observability.
4. Prefer durable artifacts over chat-only conclusions.

## Build-Day Flow

1. Pick one implementation slice.
2. Define expected inputs, outputs, and verification.
3. Update or create the relevant report in `.agentcodex/reports/`.
4. Keep telemetry, cost, and freshness implications visible in the work item.
5. Do not count placeholders, design boundaries, or local-only deploy helpers as delivered product behavior.
6. Do not resume `deploy` or `ship` work before one real user-facing slice is closed end to end.

## Workflow Selection

Use the dedicated workflow that matches the change being made:

1. `terraform.yml` for infrastructure and governance changes.
2. `ci.yml` for code validation, bundle validation, deploy, and live SQL evidence.
3. `workflow_dispatch` on `terraform.yml` with `confirm_apply=true` for controlled `dev` apply after plan review.
4. `deploy` in `ci.yml` only for Databricks bundle delivery and post-deploy evidence, not for Terraform.

## End Of Day

1. Update `.agentcodex/history/CONTEXT-HISTORY.md`.
2. Write or update a concise report under `.agentcodex/reports/`.
3. Capture blockers, open risks, and next action.
4. Do not end the day with architecture drift only in chat.

## Delivery Flow

When a change is validated and the user has not asked to hold back publication:

1. Commit the change set with a clear message.
2. Push to `origin/main` when the change is meant to update the shared repo state.
3. Use the resulting push to trigger the relevant GitHub Actions workflow.
4. Record the commit or push in the active report when it matters for later handoff.

## Required Daily Questions

- what changed in the architecture or scope?
- what was implemented versus only designed?
- what is real product behavior versus scaffolding or prototype?
- what new risk appeared in security, cost, or operations?
- what is the next smallest high-value slice?
