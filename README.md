# Leatt Fabric BI, ML and Growth Analytics Case Study

This repository is a Git-ready proof package for an end-to-end ecommerce analytics project built around the Leatt ZA public ecommerce catalog.

It demonstrates:

- Public website/catalog extraction.
- Synthetic million-row ecommerce transaction generation.
- Dimensional BI modeling.
- ML customer scoring and revenue forecasting.
- A/B testing and marketing ROI analysis.
- Competitor and SEO analysis.
- Microsoft Fabric / Azure Data Factory implementation planning.
- Evidence screenshots and portfolio-ready reports.

## What is included in Git

- `src/python/`: reproducible build scripts.
- `src/sql/`: Fabric Lakehouse/Warehouse SQL model.
- `src/powerbi/`: starter DAX measures.
- `src/fabric/`: Fabric workspace item placeholders and metadata notes.
- `src/adf/`: Azure Data Factory export placeholder notes.
- `docs/`: architecture, Azure/Fabric export, Git proof, and source-control instructions.
- `artifacts/reports/`: portfolio-ready Excel/PDF reports.
- `artifacts/data_samples/`: small CSV samples, source register, and manifests.
- `artifacts/evidence_images/`: screenshots and process diagrams.

Large generated data is intentionally excluded from Git:

- `leatt_ecommerce_warehouse.sqlite` (~539 MB)
- `leatt_ecommerce_transactions_2m.parquet` (~87 MB)
- `leatt_customer_ml_scores.csv` (~30 MB)
- full product/customer CSV extracts if Git size becomes a concern

For production, store these in OneLake, Azure Storage, or Git LFS rather than normal Git history.

## Official Microsoft references

- [Microsoft Fabric Git integration overview](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration)
- [Get started with Fabric Git integration](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started)
- [Fabric Data Factory CI/CD pipelines](https://learn.microsoft.com/en-us/fabric/data-factory/cicd-pipelines)
- [Fabric deployment pipelines overview](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/intro-to-deployment-pipelines)
- [Azure Data Factory source control](https://learn.microsoft.com/en-us/azure/data-factory/source-control)
- [Azure Data Factory CI/CD automated publish](https://learn.microsoft.com/en-us/azure/data-factory/continuous-integration-delivery-improvements)

## Quick proof commands

```powershell
git log --oneline --decorate
git status
Get-ChildItem artifacts/reports
Get-ChildItem artifacts/evidence_images
```

Generated on 2026-07-17 17:06.
