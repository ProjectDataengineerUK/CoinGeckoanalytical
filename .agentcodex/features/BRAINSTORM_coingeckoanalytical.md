# BRAINSTORM_COINGECKOANALYTICAL

## Metadata

- feature: `coingeckoanalytical`
- phase: `brainstorm`
- status: `completed`
- owner: `operator`
- updated_at: `2026-04-29T21:05:00-03:00`

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

- rebuild_direction: `production-ready product from scratch`
- primary_deliverable: `production-ready analytical product with dashboard, pipelines, and AI chat`
- target_users: `public end users who want self-service market insights`
- v1_scope: `full data platform plus dashboard, with AI chat included`
- deployment_model: `cloud-first production deployment on Databricks`
- business_priority: `advanced AI experience and differentiation`
- ai_chat_scope: `full crypto research copilot with explanations, comparisons, and recommendations`
- data_freshness: `real-time streaming where possible`
- main_constraint: `security, scalability, and production robustness`
- rebuild_source_of_truth: `new product spec from scratch using the PDF only as inspiration`
- out_of_scope_v1:
  - `portfolio management`
  - `trading and execution`
  - `social or community features`
  - `user-generated content`
- success_validation: `user-facing product validation plus production-grade technical validation`
- market_language_target: `Brazil-first, Portuguese-first`
- product_position: `data platform product for analysts and institutions`
- adoption_model: `hybrid self-serve entry with enterprise expansion`
- key_differentiator: `AI-assisted market intelligence on top of a robust data platform`
- preferred_architecture: `Databricks lakehouse with streaming and analytical serving`
- public_experience_direction: `external web frontend for the public SaaS surface, with Databricks Apps reserved for internal or operational surfaces`
- governance_posture: `enterprise-grade governance, lineage, access control, and auditability by default`
- data_scope_v1: `broad crypto intelligence coverage including advanced cross-asset analytics`
- release_optimization: `bold product vision with staged technical hardening`
- tenancy_model: `multi-tenant SaaS platform`
- ai_trust_mechanism: `full provenance with sources, query trace, confidence, and freshness metadata`
- monetization_model: `hybrid self-serve subscriptions plus enterprise plans`
- delivery_strategy: `launch a flagship end-to-end product, even if some internals mature later`
- launch_success_signal: `sustained product usage plus trusted AI-assisted decision support`

## Candidate Product Shape

Build a cloud-first, multi-tenant crypto intelligence platform on Databricks that combines a production-grade lakehouse, real-time analytical serving, a cost-optimized external public frontend, Portuguese-first dashboard experiences, and an AI research copilot grounded in governed market data.

## Define Handoff

The `define` phase should turn this into a new product specification rather than a port of the prior implementation. It should prioritize:

1. Product requirements for a Portuguese-first crypto intelligence SaaS with Databricks as the core platform.
2. Core user journeys for dashboard exploration and AI-assisted research.
3. Trust, provenance, freshness, and governance requirements for AI outputs.
4. Multi-tenant platform boundaries, security model, and enterprise controls.
5. V1 scope boundaries and staged hardening plan.
6. Public frontend versus internal Databricks-native surfaces.

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
