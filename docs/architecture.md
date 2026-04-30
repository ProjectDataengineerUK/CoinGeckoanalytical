# Arquitetura

![Arquitetura CoinGeckoAnalytical](assets/coingeckoanalytical-architecture.png)

## Visao Geral

- `Experience plane`: frontend externo, BFF, cache, auth e UI em portugues
- `Databricks data/AI plane`: ingestao, ETL, governanca, Genie, Vector Search, model serving e assets governados
- `Sentinela operations plane`: multiagentes, freshness, qualidade, custo, tokens, alertas e auditoria
- `Databricks Apps`: apenas admin e operacao interna

## Fluxo Principal

1. Fontes externas entram pela camada de ingestao.
2. Lakeflow Jobs e pipelines declarativos processam Bronze, Silver e Gold.
3. Unity Catalog governa tabelas, views, modelos, funcoes, volumes e lineage.
4. Genie atende perguntas estruturadas.
5. O copilot atende perguntas com narrativa, provenance e policy.
6. Sentinela observa e coordena o sistema.
