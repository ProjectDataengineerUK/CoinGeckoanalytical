# Context

- generated_at: `2026-04-29T23:57:27.897795+00:00`
- root: `/home/user/Projetos/CoinGeckoanalytical`

## Directory Scan

- top_level_entries: AGENTS.md, Requisitos.pdf
- base_files: 1
- markdown_files: 1
- pdf_files: 1
- video_files: 0

## Markdown Evidence

- `AGENTS.md`
  - excerpt: This project is initialized with AgentCodex.

## PDF Evidence

- multimodal review rule: PDFs must be reviewed as multimodal evidence: extract text, then render pages for visual inspection/OCR when diagrams, screenshots, architecture drawings, tables, or low text yield are present.
- `Requisitos.pdf`
  - extracted text: ​
Desenvolvi o CoinGecko Analytical Dashboard, um ecossistema completo de Data Lakehouse
operando em arquitetura Medallion (Bronze, Silver, Gold) via Docker. Uma boa base de estudos!
Tudo local e Open Source!​
​
A plataforma utiliza Apache Iceberg como formato de tabela, garantindo transações ACID, Time
Travel e evolução de schema automatizada.​
​
O coração da orquestração é o Framework ADE (Airflow DAG Engine), que desenvolvi para
abstrair a complexidade do Airflow através de metadados em YAML (DAG-as-Code).​
​
Implementei pipelines em PySpark com lógica de Smart Load, que detecta automaticamente
entre cargas Full e Incremental via MERGE INTO otimizado.​
​
A qualidade dos dados é assegurada por mecanismos de Schema Healing e 12 regras de
validação (DQ) executadas de forma síncrona via Trino.​
​
Para a camada de consumo, construí um dashboard analítico em Flask integrado a um chat de
IA com RAG (Retrieval-Augmented Generation) via API do Claude e Gemini.​
​
A infraestrutura é robusta, contando com MinIO (S3), Hive Metastore e HashiCorp Vault para
gestão centralizada de secrets.​
​
Apliquei padrões de design de software, como Facade, Factory e Strategy, elevando o código ao
nível de produção enterprise.​
​
O fluxo de desenvolvimento é sustentado por CI/CD via GitHub Actions, com testes
automatizados e linting (Pytest e Lint) para garantir a integridade do monorepo.​
​
Um projeto de ponta que une a robustez da Engenharia de Dados clássica com a agilidade
analítica da IA Generativa.​
​
​
Juliano Mendes, seu texto está excelente, mas ele passa uma sensação de arquitetura quase

  - visual inspection: render pages and inspect images, diagrams, tables, and architecture flows before treating the PDF as complete

## Video Evidence

- [none]

## Brainstorm Prompt

You are the AgentCodex workflow-brainstormer.
Use the context in this file to start a structured brainstorm in English.
Ask one question at a time, prefer multiple-choice prompts when possible, and keep the first phase focused on problem framing, users, constraints, samples, and candidate approaches.
