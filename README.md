# Leatt Fabric BI, ML and Growth Analytics Case Study

This repository is a Git-ready proof package for an end-to-end ecommerce analytics project built around the Leatt ZA public ecommerce catalog.

Remote proof repository: https://github.com/anthonyapollis/leatt-fabric-bi-ml-proof

## Final leave-behind deliverables

- `artifacts/reports/leatt_final_executive_portfolio_dossier.pdf` - board/interview dossier with screenshots, KPIs, data story and handover notes.
- `artifacts/reports/leatt_fabric_bi_ml_board_presentation.pptx` - PowerPoint-compatible executive presentation.
- `artifacts/reports/leatt_ecommerce_bi_ml_ai_command_center_master.xlsx` - master Excel workbook with Fabric, ERD, Power BI, AI command-center and data-story sheets.
- `docs/final_project_completion_report.md` - written completion report covering what was built, what the data tells us, SAP/dbt/Hybris positioning and cost handover.
- `docs/portfolio_index.html` - local clickable index for opening the deliverables.
- `docs/fabric_cost_control_and_handover.md` - Fabric F2 suspend/resume and production hardening checklist.

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
- `src/add_intelligent_command_center.py`: reproducible AI command-center and data-story generator.
- `src/finalize_leatt_project.py`: final dossier/deck/index/handover pack generator.
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

## Senior BI Developer Role Alignment

This repository now includes a role-alignment pack for a Senior Business Intelligence Developer position covering Microsoft Fabric, Azure Data Factory, Power BI, SQL, DAX, Python, AI-driven BI, governance, SAP/accounting integration, stakeholder consulting and training.

See `docs/SENIOR_BI_DEVELOPER_JOB_ALIGNMENT.md`.


The exact target Senior BI Developer job specification is preserved in `docs/TARGET_JOB_SPEC.md`.

## Cost control reminder

Suspend Fabric F2 capacity after review to protect Azure credit:

```powershell
az fabric capacity suspend --resource-group rg-leatt-fabric-bi-ml --capacity-name leattfabricf2
```
