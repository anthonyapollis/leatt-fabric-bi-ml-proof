# Source Control Strategy

## Recommended branch flow

- `main`: stable portfolio version.
- `dev`: active Fabric/ADF development.
- `feature/fabric-pipeline`: Data Factory and Lakehouse work.
- `feature/powerbi-report`: semantic model and report work.
- `feature/ml-scoring`: notebooks, model scoring, and forecast work.

## What belongs in Git

- Python/SQL/DAX code.
- Fabric workspace item metadata exports.
- ADF pipeline JSON and ARM templates.
- Documentation.
- Source registers.
- Screenshots and small evidence files.
- Small sample CSV outputs.

## What should not be normal Git

- Large parquet/sqlite/CSV extracts.
- Secrets, tokens, connection strings, passwords.
- Personal account details and billing screenshots without redaction.

Use OneLake, Azure Storage, SharePoint, or Git LFS for large artifacts.
