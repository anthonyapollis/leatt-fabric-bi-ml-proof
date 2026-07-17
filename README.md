# Leatt Fabric BI, ML and Growth Analytics Case Study

This repository is a Git-ready delivery package for an end-to-end ecommerce analytics project built around the Leatt ZA public ecommerce catalog.

Remote proof repository: https://github.com/anthonyapollis/leatt-fabric-bi-ml-proof

## Start Here

- `artifacts/reports/leatt_growth_os_master_portfolio.pdf` - combined master dossier. Open this first.
- `docs/START_HERE_LEATT_GROWTH_OS.md` - clean reading order and proof guide.
- `docs/leatt_growth_os_combined_index.html` - clickable local index for the curated package.
- `artifacts/data_samples/leatt_growth_os_combined_manifest.csv` - manifest of the curated final delivery.

## Final deliverables

- `artifacts/reports/leatt_medallion_architecture_dirty_to_clean_report.pdf` - Bronze/Silver/Gold medallion architecture, dirty-data cleansing rules, data-quality gates and Fabric implementation map.
- `artifacts/reports/leatt_growth_os_case_study.pdf` - lead portfolio case study: a single visual storyline from storefront evidence to Fabric, Power BI, ML, AI SEO, SAP reconciliation and executive action.
- `artifacts/reports/leatt_story_driven_ebook.pdf` - story-first ebook that explains the business problem, what the data says, what was learned, and which leadership actions follow.
- `artifacts/reports/leatt_story_driven_executive_report.pdf` - concise board-style report built around revenue, margin, returns, ML risk, SEO, governance and Azure/Fabric proof.
- `artifacts/reports/leatt_premium_executive_bi_report.pdf` - redesigned premium executive report, rebuilt around modern dashboard/report design patterns.
- `artifacts/reports/leatt_premium_bi_storybook.pdf` - redesigned ebook/storybook with stronger narrative and decision flow.
- `artifacts/reports/leatt_final_executive_portfolio_dossier.pdf` - executive project dossier with screenshots, KPIs, data story and handover notes.
- `artifacts/reports/leatt_fabric_bi_ml_board_presentation.pptx` - PowerPoint-compatible executive presentation.
- `artifacts/reports/leatt_ecommerce_bi_ml_ai_command_center_master.xlsx` - master Excel workbook with Fabric, ERD, Power BI, AI command-center and data-story sheets.
- `artifacts/reports/leatt_kpi_and_report_rationale.pdf` - KPI/report rationale explaining why each KPI was used, what it signals and which business action it drives.
- `artifacts/reports/leatt_decision_intelligence_playbook.pdf` - signal rules, root-cause playbook, owner actions and prioritized initiatives.
- `artifacts/reports/leatt_ai_seo_best_practices_playbook.pdf` - latest AI-era ecommerce SEO best practices, KPIs and 12-week roadmap.
- `docs/final_project_completion_report.md` - written completion report covering what was built, what the data tells us, SAP/dbt/Hybris positioning and cost handover.
- `docs/leatt_growth_os_case_study.md` - concise narrative spine for the lead Growth OS case study.
- `docs/leatt_story_driven_report_narrative.md` - plain-English data story used by the ebook and executive report.
- `docs/kpi_and_report_rationale.md` - Markdown KPI catalog and report catalog for project review.
- `docs/decision_intelligence_playbook.md` - management-system layer explaining thresholds, owners, decisions and executive storyline.
- `docs/ai_seo_best_practices_playbook.md` - AI SEO strategy, Product schema/feed guidance, visibility KPIs and sources.
- `docs/leatt_premium_report_design_system.md` - design rationale, source inspiration and report design system for the premium redesign.
- `docs/premium_dashboard_gallery.html` - local gallery for the redesigned report pages.
- `docs/powerbi_report_creation_proof.md` - live Power BI report item ID, URL, API result, export proof and screenshot paths.
- `docs/portfolio_index.html` - local clickable index for opening the deliverables.
- `docs/fabric_cost_control_and_handover.md` - Fabric F2 suspend/resume and production hardening checklist.

It demonstrates:

- Public website/catalog extraction.
- Synthetic million-row ecommerce transaction generation.
- Dimensional BI modeling.
- Medallion architecture with Bronze dirty landing, Silver cleansing, Gold marts and data-quality gates.
- ML customer scoring and revenue forecasting.
- A/B testing and marketing ROI analysis.
- Competitor and SEO analysis.
- Microsoft Fabric / Azure Data Factory implementation planning.
- Evidence screenshots and delivery-ready reports.

## What is included in Git

- `src/python/`: reproducible build scripts.
- `src/sql/`: Fabric Lakehouse/Warehouse SQL model.
- `src/powerbi/`: starter DAX measures.
- `src/powerbi/create_fabric_powerbi_reports.py`: creates the live Power BI report item through the Fabric Report Create API.
- `src/fabric/`: Fabric workspace item placeholders and metadata notes.
- `src/adf/`: Azure Data Factory export placeholder notes.
- `src/add_intelligent_command_center.py`: reproducible AI command-center and data-story generator.
- `src/add_decision_intelligence_layer.py`: reproducible signal-rule/root-cause/business-priority generator.
- `src/add_ai_seo_best_practices.py`: reproducible AI SEO best-practices, KPI and roadmap generator.
- `src/add_kpi_rationale_layer.py`: reproducible KPI/report rationale generator.
- `src/add_medallion_architecture_pack.py`: Bronze/Silver/Gold medallion architecture, dirty-data samples, quality gates and report generator.
- `src/create_premium_report_pack.py`: premium executive report, storybook and dashboard gallery generator.
- `src/create_growth_os_case_study.py`: visual case-study generator that consolidates the scattered reports into one Growth OS storyline.
- `src/create_story_driven_report.py`: story-first ebook/report generator using the modeled warehouse, screenshots and decision-intelligence outputs.
- `src/finalize_leatt_project.py`: final dossier/deck/index/handover pack generator.
- `docs/`: architecture, Azure/Fabric export, Git proof, and source-control instructions.
- `artifacts/reports/`: delivery-ready Excel/PDF reports.
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

## Cost control reminder

Suspend Fabric F2 capacity after review to protect Azure credit:

```powershell
az fabric capacity suspend --resource-group rg-leatt-fabric-bi-ml --capacity-name leattfabricf2
```
