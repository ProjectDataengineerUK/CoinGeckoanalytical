# Project AGENTS

## Purpose

This project is initialized with AgentCodex.

Use AgentCodex as the workflow and domain guidance layer for Codex-based development.

Current stack direction:

- external frontend for the public product surface
- Databricks for ingestion, ETL, governance, analytics, model lifecycle, and AI
- Sentinela for multi-agent coordination and observability
- Portuguese-first UI and responses in V1

## Operating Rules

1. Use `AGENTS.md` as the project instruction baseline.
2. Keep workflow artifacts in `.agentcodex/`.
3. Prefer local knowledge in `.agentcodex/kb/` before external sources when the topic is covered there.
4. Use the workflow in this order unless there is a good reason not to:
   - brainstorm
   - define
   - design
   - build
   - ship
5. Record verification in `.agentcodex/reports/`.
6. Use `.agentcodex/commands/` for project-local procedure docs that replace slash-command assumptions.

## AgentCodex Project Standard

Do not treat the project as complete until the AgentCodex Project Standard blocks are implemented or explicitly justified as not applicable:

- contexto
- arquitetura
- dados
- governanca
- lineage
- execucao
- validacao
- observabilidade
- access control
- data contracts
- operacao
- deploy
- custo
- compliance

Reference scaffold:

- `.agentcodex/features/example-project-standard/`

## Working Directories

- `.agentcodex/features/`
- `.agentcodex/reports/`
- `.agentcodex/archive/`
- `.agentcodex/templates/`
- `.agentcodex/commands/`
- `.agentcodex/kb/`
- `.agentcodex/routing/`

## Routing

Primary routing reference:

- `.agentcodex/routing/routing.json`

Human-readable guide:

- `.agentcodex/PROJECT_AGENTSCODEX.md`
- `.agentcodex/commands/`

## Recommended Roles

- `explorer` for investigation and evidence
- `reviewer` for bug/risk/test review
- domain-specific roles according to the workflow and routing guide

## Notes

- keep the architecture aligned with the current Databricks-first design and update this file when the stack changes
