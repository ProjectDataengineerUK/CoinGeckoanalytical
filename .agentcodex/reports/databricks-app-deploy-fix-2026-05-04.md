# Databricks App Deploy Fix - 2026-05-04

## Contexto

O deploy da app falhou em `2026-05-04 12:42-12:45 GMT-3` com dois sintomas:

- `error loading app spec from app.yml` / `error reading app.yaml file`
- antes disso, uma tentativa iniciou `python __init__.py` e terminou com `app exited unexpectedly`

## Causa raiz confirmada

1. Os manifests `apps/cga-analytics/app.yaml` e `apps/cga-admin/app.yaml` estavam em formato inválido para Databricks Apps:
   - `valueFrom` foi definido como estrutura `secretRef`, mas a documentação atual de Databricks Apps exige um identificador simples de recurso.
   - no app admin havia entradas `env` com apenas `name`, sem `value` nem `valueFrom`, o que também invalida o schema.
2. Os entrypoints Dash estavam fixando portas locais (`8050` e `8051`) em vez de respeitar `PORT` / `DATABRICKS_APP_PORT`, o que tende a quebrar no runtime gerenciado.

## Correções aplicadas

- `apps/cga-analytics/app.yaml`
  - removidas entradas inválidas de `valueFrom`
  - mantido apenas `COINGECKO_CATALOG` com valor estático válido
- `apps/cga-admin/app.yaml`
  - removidas entradas `env` inválidas sem valor
  - definidos `COINGECKO_CATALOG` e `COINGECKO_OPS_CATALOG`
- `apps/cga-analytics/app.py`
  - app passa a ler `PORT` e `DATABRICKS_APP_PORT`
- `apps/cga-admin/app.py`
  - app passa a ler `PORT` e `DATABRICKS_APP_PORT`

## Verificação local

- `python3 -m py_compile apps/cga-analytics/app.py apps/cga-admin/app.py apps/cga-analytics/services/*.py apps/cga-admin/services/*.py`
- resultado: sucesso

## Próximo ponto no workspace

Se o deploy avançar além da leitura do `app.yaml`, o próximo comportamento esperado é:

- a app sobe mesmo sem `DATABRICKS_SQL_WAREHOUSE_ID` e `DATABRICKS_GENIE_SPACE_ID`
- porém Genie/SQL podem aparecer como indisponíveis até esses recursos serem configurados corretamente no workspace

Para habilitar esses recursos do jeito suportado pelo Databricks Apps, o próximo passo é declarar e mapear recursos de app com chaves simples, por exemplo:

```yaml
env:
  - name: DATABRICKS_SQL_WAREHOUSE_ID
    valueFrom: sql-warehouse
  - name: DATABRICKS_GENIE_SPACE_ID
    valueFrom: genie-space
```

Isso depende de os recursos correspondentes existirem e serem configurados no deploy da app.
