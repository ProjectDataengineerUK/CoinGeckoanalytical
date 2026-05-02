# Model And Version Governance

## Purpose

Define the operational contract for Unity Catalog model versions, aliases, and promotion rules for the Databricks-side slice.

## Registry Pattern

- Keep the registered model name in Unity Catalog form: `<catalog>.<schema>.<model_name>`
- Treat the numeric version as immutable once registered
- Treat aliases as mutable pointers to a version
- Use aliases to signal deployment status, not the catalog name itself

## Required Model Metadata

Every registered model version should carry:

- owner
- training data reference
- feature set or input contract
- evaluation summary
- approval timestamp
- lineage source references
- serving intent

## Promotion States

- `draft`: trained but not validated
- `validated`: passed offline checks
- `candidate`: ready for controlled comparison
- `champion`: production target
- `archived`: superseded by a later version

## Promotion Rules

1. Register a new model version.
2. Validate the version against the current Gold contract and offline evaluation set.
3. Assign a `Candidate` alias for controlled testing.
4. Reassign `Champion` only after the candidate is approved.
5. Keep the prior champion available only until rollback risk is closed.
6. Remove or repoint aliases before deleting or archiving a version.

## Access Control

- Restrict model ownership to the platform or ML engineering group that owns the lifecycle
- Grant the minimum `USE CATALOG` and `USE SCHEMA` privileges required for model management
- Limit alias updates to the same governance group that approves promotions
- Prefer governed review over ad hoc alias changes from notebooks

## Operational Commands

Databricks model aliases are managed through Catalog Explorer or the MLflow client. The Databricks docs describe aliases as the mutable reference used to indicate deployment status, and note that alias changes require model ownership plus `USE CATALOG` and `USE SCHEMA` privileges.

Example:

```python
from mlflow import MlflowClient

client = MlflowClient()
client.set_registered_model_alias(
    name="prod.analytics.market_risk_model",
    alias="Champion",
    version="17",
)
```

## Governance Notes

- Use audit logs for traceability of model lifecycle events
- Keep model descriptions and tags aligned with the serving contract
- Use aliases in inference workloads instead of hard-coded version numbers
- Refresh the approval record whenever a model version is re-promoted
