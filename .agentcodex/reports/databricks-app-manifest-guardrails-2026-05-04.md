# Databricks App Manifest Guardrails - 2026-05-04

## Objetivo

Evitar regressão do erro de deploy por manifest inválido de Databricks Apps.

## Mudanças

- ampliada a validação em `databricks/tools/validate_bundle.py`
- adicionada checagem de:
  - presença das apps `cga_analytics` e `cga_admin` no bundle
  - `source_code_path` esperado para cada app
  - existência de `app.yaml` em cada app
  - `command` não vazio em `app.yaml`
  - itens de `env` com `name` e exatamente um entre `value` ou `valueFrom`
- adicionados testes em:
  - `databricks/tests/test_validate_bundle.py`
  - `databricks/tests/test_bundle_manifest.py`

## Verificação

- `python3 databricks/tools/validate_bundle.py`
- `python3 -m unittest databricks.tests.test_validate_bundle databricks.tests.test_bundle_manifest`

Resultado:

- validação do bundle: `passed`
- testes: `11 tests`, `OK`

## Efeito prático

Se alguém voltar a introduzir padrões inválidos como:

- `env` com apenas `name`
- `env` com `value` e `valueFrom` ao mesmo tempo
- `app.yaml` ausente

o repositório passa a falhar localmente antes do próximo deploy.
