# Leatt Fabric BI/ML Project Completion Report

Generated: 2026-07-17 20:16

## Executive conclusion

This project is now a complete senior BI portfolio case study: website extraction, million-row ecommerce modeling, Azure/Fabric Lakehouse upload, Data Factory proof, Power BI semantic model, ML return-risk scoring, accounting reconciliation, SAP integration design, governance controls, A/B testing, marketing/SEO analysis, AI agents, Git proof and executive reporting.

## What was built

- Extracted real Leatt ZA public catalog/product evidence and confirmed the storefront platform pattern.
- Generated and modeled 2,000,000 ecommerce transaction lines, 11,354 product records and 180,000 synthetic customers.
- Uploaded the data estate to Microsoft Fabric OneLake under the `Apollis` workspace and `Leatt_BI_ML_Lakehouse`.
- Created a Fabric Data Factory pipeline item and Power BI semantic model proof.
- Built Excel/PDF/eBook deliverables, evidence screenshots, ERD, data governance register, accounting reconciliation pack and AI command-center layer.
- Pushed the Git proof package to GitHub: `https://github.com/anthonyapollis/leatt-fabric-bi-ml-proof`.

## What the data tells us

- **Scale**: The modeled ecommerce estate is large enough for enterprise BI: R3,994,247,413 revenue and R1,938,497,252 gross margin across the analytical period.
- **Category economics**: Apparel is the hero growth engine at R1,759,430,045; it deserves board-level tracking, product storytelling and protected availability.
- **Margin leakage**: Returns absorb 4.9% of modeled revenue, with Footwear carrying the highest return-rate signal. Fit, sizing, delivery promises and PDP content should be inspected before scaling spend.
- **Marketing efficiency**: Direct is the efficiency engine with ROAS 100.0x. Paid channels should be optimized with creative testing, landing-page relevance and bundle-led offers before budget expansion.
- **Merchandising action**: Jacket ADV FlowTour 5.5 - Women is a strong margin candidate for bundles, recommendations and attach-rate testing.
- **Monitoring**: 2025-12 moved 12.6% versus the 3-month signal and should be explained in the trading pack.
- **Governance**: Every insight is tied to a source register, row count, ERD, OneLake upload path, Power BI semantic model and Git commit so the work can survive audit review.

## Business optimisation thesis

- Protect hero categories with stock, price, SEO and executive alerts.
- Use A/B tests to prove bundles, free shipping thresholds and lifecycle offers before scaling spend.
- Treat returns as a margin problem, not only an operations problem: improve fit guidance, product detail pages, delivery promises and post-purchase education.
- Reconcile ecommerce orders, refunds, VAT, payment settlement and SAP postings in the monthly close pack.
- Promote Fabric/Power BI as the trusted semantic layer and keep source lineage, row counts, file hashes and Git commits visible.

## Azure/Fabric proof

- Resource group: `rg-leatt-fabric-bi-ml`
- Fabric capacity: `leattfabricf2`
- Capacity SKU: `F2`
- Workspace: `Apollis`
- Lakehouse: `Leatt_BI_ML_Lakehouse`
- Pipeline: `pl_leatt_million_row_lakehouse_load`
- Power BI semantic model ID: `9ee6f8a0-aec0-48ff-a44c-15985f3bd4bc`
- Power BI semantic model URL: `https://app.powerbi.com/groups/e515bafe-7290-4832-ae1d-514be43a9d87/datasets/9ee6f8a0-aec0-48ff-a44c-15985f3bd4bc`

## ML proof

- Return-risk model AUC: `0.589`
- Return-risk model recall: `0.718`
- Interpretation: the model is useful as an early recall-focused watchlist, but precision should be improved with real return reasons, size/fit attributes, delivery events and customer service signals.

## SAP and platform positioning

- The live storefront evidence points to Shopify, so SAP Commerce Cloud / Hybris is not required for this specific Leatt ZA storefront proof.
- SAP Business One or SAP BW still fits as the downstream source for finance, inventory, VAT, COGS, customer/accounting reconciliation and audit extracts.
- SAP Commerce Cloud / Hybris would fit if the company wanted a larger enterprise commerce platform with deep SAP ERP integration, complex catalogs, B2B pricing and global multi-site orchestration.
- dbt is optional for this proof. It becomes valuable later for versioned SQL transformations, automated tests and CI/CD around the semantic warehouse layer.

## Cost and handover

Final handover status on 2026-07-17: Fabric F2 capacity `leattfabricf2` was suspended and verified as `Paused`.

Suspend Fabric capacity when review is complete:

```powershell
az fabric capacity suspend --resource-group rg-leatt-fabric-bi-ml --capacity-name leattfabricf2
```

Resume only when refreshing Fabric/Power BI proof:

```powershell
az fabric capacity resume --resource-group rg-leatt-fabric-bi-ml --capacity-name leattfabricf2
```
