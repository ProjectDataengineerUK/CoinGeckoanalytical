# CoinGeckoAnalytical

Plataforma de crypto market intelligence operando nativamente em Databricks, com duas superfícies principais:

- `cga-analytics` Databricks App para a experiência do usuário final
- `cga-admin` Databricks App para operações, governança, custo e auditoria

## Arquitetura

[![Arquitetura CoinGeckoAnalytical](docs/assets/coingeckoanalytical-architecture.png)](docs/architecture.md)

## Estrutura Atual

- `Databricks Apps` como superfície primária do produto
- `Databricks` para ingestão, ETL, governança, serving analítico e IA
- `Genie` para perguntas estruturadas sobre dados Gold
- `Mosaic AI Agent Framework` para o copilot de mercado
- `Sentinela` para coordenação multiagente e observabilidade
- `cga-analytics/` com painel Genie, charts dinâmicos, freshness bar e copilot
- `cga-admin/` com Sentinela, health, cost, access e audit review

## Documentação

- [Arquitetura completa](docs/architecture.md)

## Artefatos do Projeto

- brainstorm: `.agentcodex/features/BRAINSTORM_coingeckoanalytical.md`
- define: `.agentcodex/features/DEFINE_coingeckoanalytical.md`
- design: `.agentcodex/features/DESIGN_coingeckoanalytical.md`
- build: `.agentcodex/features/BUILD_coingeckoanalytical.md`

## Workflows

- `terraform.yml`: infra and governance plan/apply
- `ci.yml`: validation and manual Databricks deploy approval
- `bronze-migration.yml`: manual Bronze schema remediation approval

## Approval Model

- [Approval policy](.agentcodex/ops/approval-gate-policy.md)
- [Current approval status](.agentcodex/reports/approval-gate-status.md)

## Direcao Atual

- fonte principal inicial: `CoinGecko API`
- arquitetura alvo: `Databricks Apps primary surface + Databricks data/AI plane + sentinela ops plane`
- observabilidade: tokens, custo, freshness, qualidade e trilha de auditoria
- fase ativa: `ship`
- postura atual: `baseline final validado e online, com runtime governado, CI verde e deploy gates manuais para futuras mutacoes`
- proximo passo: `hardening de producao residual: rate limiting, webhooks de notificacao, DR, promocao staging/prod e integracao live fora do caminho de deploy`
