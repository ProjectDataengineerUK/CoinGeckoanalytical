# Project AgentCodex Bootstrap

Use this file as the first project-local bootstrap note when introducing AgentCodex into a real repository.

## Project

- name:
- owner:
- primary stack:
- repository root:

## Workflow Convention

AgentCodex workflow artifacts live in:

- `.agentcodex/features/`
- `.agentcodex/reports/`
- `.agentcodex/archive/`
- `.agentcodex/history/`
- `.agentcodex/commands/`

## Project Defaults

- preferred orchestration:
- preferred transform layer:
- preferred quality tooling:
- preferred runtime:

## Initial Operating Rules

1. Start unclear work with `brainstorm`.
2. Do not move to `design` without a passing `define`.
3. Do not move to `build` without a manifest in `design`.
4. Record verification in `BUILD_REPORT`.
5. Archive meaningful completed work in `SHIPPED`.
6. Use `.agentcodex/commands/` as the project-local command procedure index.
7. Preserve resumable context in `.agentcodex/history/` using the project context history rule.
8. Do not treat the project as complete until the `AgentCodex Project Standard` blocks are implemented or explicitly justified as not applicable.

## AgentCodex Project Standard

Authoritative manifest:

- `.agentcodex/project-standard.json`
- `.agentcodex/maturity/maturity5-baseline.json` for projects that must start at high DataOps + LLMOps maturity

Reference scaffold:

- `.agentcodex/features/example-project-standard/`

Required blocks:

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

Conditional block:

- `agentes definidos (se houver)`

Additional enterprise baseline:

- run `agentcodex maturity5-check <target-project-dir> --profile <profile-id>` when the project is expected to start at high DataOps + LLMOps maturity
- available starter profiles: `data-platform`, `agentic-llm`, `regulated-enterprise`
- prefer `agentcodex install <target-project-dir> --profile <profile-id>` to materialize the matching overlay under `.agentcodex/ops/` with local `.codex/` support

## Command Procedures

Project-local command procedures live in `.agentcodex/commands/`.

Recommended starting set:

- `pipeline.md`
- `schema.md`
- `data-contract.md`
- `data-quality.md`
- `ai-pipeline.md`
- `review.md`
- `meeting.md`
- `sync-context.md`
- `create-kb.md`

## Role Preferences

- orchestration:
- schema:
- transforms:
- distributed jobs:
- quality:

## Key Constraints

- security:
- compliance:
- infra:
- release cadence:

## Notes

- add project-specific conventions here
