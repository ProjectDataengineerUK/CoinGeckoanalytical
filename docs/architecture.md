# Arquitetura

![Arquitetura CoinGeckoAnalytical](assets/coingeckoanalytical-architecture.png)

## Visao Geral

- `Experience plane`: `cga-analytics` Databricks App para analytics, charts e copilot
- `Databricks data/AI plane`: ingestao, ETL, governanca, Genie, Vector Search, model serving e assets governados
- `Sentinela operations plane`: multiagentes, freshness, qualidade, custo, tokens, alertas e auditoria
- `Databricks Apps`: `cga-analytics` como superficie principal e `cga-admin` como superficie interna de operacao

## Fluxo Principal

1. Fontes externas entram pela camada de ingestao.
2. Lakeflow Jobs e pipelines declarativos processam Bronze, Silver e Gold.
3. Unity Catalog governa tabelas, views, modelos, funcoes, volumes e lineage.
4. `Genie` atende perguntas estruturadas e dirige o estado analitico.
5. O copilot Mosaic/orquestrado atende perguntas narrativas com provenance, freshness e policy.
6. `cga-admin` expõe sinais operacionais, access management, custo e auditoria.
7. Sentinela observa e coordena o sistema.
