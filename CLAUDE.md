# CLAUDE.md

## Project

- name: `CoinGeckoAnalytical`
- repository_root: `/home/user/Projetos/CoinGeckoanalytical`
- workflow_system: `AgentCodex`

## Current Product Direction

CoinGeckoAnalytical is being designed as a public SaaS crypto market intelligence platform with:

- `external web frontend` as the public product surface
- `Databricks` as the backend data and AI platform
- `AI/BI Genie` for structured analytical NLQ over governed Gold data
- `Mosaic AI Agent Framework` for the main market copilot
- `Databricks Apps` only for internal tools, admin surfaces, and operational workflows

## Source Of Truth

Use these files in this order:

1. `AGENTS.md`
2. `.agentcodex/features/DEFINE_coingeckoanalytical.md`
3. `.agentcodex/features/DESIGN_coingeckoanalytical.md`
4. `README.md`

## Mandatory Workflow

Follow the AgentCodex flow unless the repository state clearly justifies a later step:

1. `brainstorm`
2. `define`
3. `design`
4. `build`
5. `ship`

Record verification artifacts under `.agentcodex/reports/`.

## Architecture Rules

- Do not make `Databricks Apps` the primary public product frontend.
- Optimize public serving cost with an external frontend and keep Databricks focused on specialized backend capabilities.
- Keep all governed analytical assets under `Unity Catalog`.
- Keep `Genie` scoped to structured analytics, not broad freeform market reasoning.
- Keep the main copilot in coded orchestration, not hidden in opaque prompt-only flows.
- Treat `Agent Bricks` as optional and non-foundational.

## Data And AI Rules

- Primary initial data source: `CoinGecko API`
- Plan for future multi-source market intelligence rather than permanent single-provider dependence.
- Every grounded AI answer should expose provenance, freshness, and confidence context.
- Token and cost telemetry are required for copilot flows.
- Tenant isolation applies to dashboards, telemetry, and AI responses.

## CI/CD And Auth Guidance

- Prefer `Databricks Asset Bundles` for deployment automation.
- Use `service principal` authentication for CI/CD.
- Prefer `OAuth M2M` or workload identity federation over user PAT-based automation.
- Do not rely on interactive `databricks auth login` flows in CI.

## Project Standard Blocks

Do not consider the project complete until these are implemented or explicitly marked not applicable:

- `contexto`
- `arquitetura`
- `dados`
- `governanca`
- `lineage`
- `execucao`
- `validacao`
- `observabilidade`
- `access control`
- `data contracts`
- `operacao`
- `deploy`
- `custo`
- `compliance`

## Current Repository State

Current state is design-heavy and pre-build:

- `.agentcodex/features/BRAINSTORM_coingeckoanalytical.md`
- `.agentcodex/features/DEFINE_coingeckoanalytical.md`
- `.agentcodex/features/DESIGN_coingeckoanalytical.md`
- `docs/assets/coingeckoanalytical-architecture.png`
- `README.md`

There is not yet an implementation of:

- production code
- sentinela runtime
- maturity 5 operational baseline
- DataOps / LLMOps operating stack

## Expected Next Steps

When continuing from the current repo state, prioritize:

1. build planning
2. project-standard materialization
3. DataOps + LLMOps operating model
4. sentinela and observability baseline
5. interface payload schemas and backend contracts

## Avoid

- Do not collapse the architecture into a single Databricks-hosted UI layer for the public product.
- Do not assume the public API source mix is solved permanently by one provider.
- Do not skip telemetry, cost controls, or auditability for AI features.
- Do not treat design artifacts as implementation completion.
