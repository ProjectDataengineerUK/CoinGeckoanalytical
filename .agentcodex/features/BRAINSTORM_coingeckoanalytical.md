# BRAINSTORM_COINGECKOANALYTICAL

## Metadata

- feature: `coingeckoanalytical`
- phase: `brainstorm`
- status: `completed`
- owner: `operator`
- updated_at: `2026-04-30T00:00:00-03:00`

## Grounding

- source_of_truth: `Requisitos.pdf`
- supporting_files:
  - `context.md`
  - `.agentcodex/reports/start-brainstorm-prompt.md`
- multimodal_evidence_reviewed:
  - technical architecture diagram
  - dashboard screenshot
  - AI chat screenshot

## Decisions

- rebuild_direction: `recreate the prior product almost entirely, but on a new and more mature architecture`
- primary_deliverable: `complete V1 product ready for use, with dashboard, pipelines, and AI chat`
- target_users: `public self-serve users plus analysts and institutional teams from the start`
- v1_scope: `full platform scope without meaningful scope cuts in V1`
- deployment_model: `cloud-first production deployment on Databricks`
- business_priority: `advanced AI experience and differentiation`
- ai_chat_scope: `full crypto research copilot with explanations, comparisons, and recommendations`
- data_freshness: `real-time streaming where possible`
- main_constraint: `security, compliance, governance, lineage, access control, auditability, scalability, and production robustness from the start`
- rebuild_source_of_truth: `recreate the prior product direction with a stronger architecture and broader production maturity`
- out_of_scope_v1: `no meaningful cuts were accepted during brainstorm`
- success_validation: `near-production validation with end-to-end product behavior, operational readiness, and strong controls`
- market_language_target: `Brazil-first, Portuguese-first`
- product_position: `data platform product for analysts and institutions`
- adoption_model: `hybrid self-serve entry with enterprise expansion`
- key_differentiator: `AI-assisted market intelligence on top of a robust data platform`
- preferred_architecture: `Databricks lakehouse with streaming and analytical serving`
- public_experience_direction: `external web frontend for the public SaaS surface, with Databricks Apps reserved for internal or operational surfaces`
- governance_posture: `enterprise-grade governance, lineage, access control, and auditability by default`
- data_scope_v1: `broad crypto intelligence coverage including CoinGecko plus additional data sources from the start`
- release_optimization: `bold product vision with staged technical hardening`
- tenancy_model: `multi-tenant SaaS platform`
- ai_trust_mechanism: `full provenance with sources, query trace, confidence, and freshness metadata`
- monetization_model: `hybrid self-serve subscriptions plus enterprise plans`
- delivery_strategy: `launch a flagship end-to-end product, even if some internals mature later`
- launch_success_signal: `sustained product usage plus trusted AI-assisted decision support`
- chosen_approach: `complete platform-oriented product build, Databricks-first, with multi-source data, dashboard, AI chat, governance, and observability integrated from the beginning`

## Candidate Product Shape

Build a cloud-first, multi-tenant crypto intelligence platform on Databricks that recreates the prior product ambition almost in full, but with stronger architecture, broader production maturity, multi-source market data, a cost-optimized external public frontend, Portuguese-first dashboard experiences, and an AI research copilot grounded in governed market data.

## Define Handoff

The `define` phase should turn this into a strict product specification for a complete V1, not a narrow technical slice. It should prioritize:

1. Product requirements for a Portuguese-first crypto intelligence SaaS with Databricks as the mandatory platform core.
2. Full V1 journeys for public self-serve users, analysts, and institutional teams.
3. Multi-source market data strategy from day one, starting with CoinGecko but not limited to it.
4. Trust, provenance, freshness, governance, compliance, and auditability requirements as foundational V1 behavior.
5. Multi-tenant platform boundaries, access-control model, and enterprise controls from the beginning.
6. Dashboard, AI copilot, pipelines, observability, and operational readiness as one integrated V1 product.
7. Explicit acknowledgement that no meaningful YAGNI cuts were accepted, so define must surface delivery risk and sequencing pressure clearly.

## Exit Check

- [x] PDF text reviewed
- [x] PDF visuals reviewed
- [x] product direction selected
- [x] target users selected
- [x] architecture direction selected
- [x] AI scope selected
- [x] out-of-scope cuts selected
- [x] validation criteria selected
- [x] define handoff prepared
