# AI Commerce Command Center

This layer turns the Leatt Fabric BI/ML project into an intelligent operating model, not just a dashboard.

## Concept

The platform watches sales, margin, returns, marketing, product, finance and governance signals, then turns them into next-best-actions for executives, marketing, merchandising, finance and BI operations.

## What the data tells us

| theme | what_the_data_tells_us |
| --- | --- |
| Scale | The modeled ecommerce estate is large enough for enterprise BI: R3,994,247,413 revenue and R1,938,497,252 gross margin across the analytical period. |
| Category economics | Apparel is the hero growth engine at R1,759,430,045; it deserves board-level tracking, product storytelling and protected availability. |
| Margin leakage | Returns absorb 4.9% of modeled revenue, with Footwear carrying the highest return-rate signal. Fit, sizing, delivery promises and PDP content should be inspected before scaling spend. |
| Marketing efficiency | Direct is the efficiency engine with ROAS 100.0x. Paid channels should be optimized with creative testing, landing-page relevance and bundle-led offers before budget expansion. |
| Merchandising action | Jacket ADV FlowTour 5.5 - Women is a strong margin candidate for bundles, recommendations and attach-rate testing. |
| Monitoring | 2025-12 moved 12.6% versus the 3-month signal and should be explained in the trading pack. |
| Governance | Every insight is tied to a source register, row count, ERD, OneLake upload path, Power BI semantic model and Git commit so the work can survive audit review. |

## What we learned

- The project is not only a Power BI exercise. It is an operating model: Fabric stores the governed data estate, Power BI explains the performance, ML highlights return risk, and AI agents turn signals into action.
- The real Leatt storefront runs on Shopify signals rather than SAP Commerce/Hybris, so SAP Commerce is not needed for this case. SAP Business One or SAP BW still fits downstream as the finance and inventory source for reconciliation, VAT, COGS, stock and audit controls.
- dbt is optional. It would be useful later for versioned SQL transformations and tests, but Fabric Data Factory, notebooks, SQL models and semantic-model measures are enough for this proof.
- The most valuable business angle is not "more data"; it is governed decisions: which categories to protect, which products to bundle, where return leakage is eroding margin, and where marketing spend should be scaled or constrained.

## How to optimise the business

- Protect the hero category with availability alerts, executive KPI tracking and SEO/product-story content.
- Build margin-positive bundles around high gross-margin products and test them through A/B experiments.
- Reduce return leakage with size guidance, richer product detail pages, post-purchase education and exception reporting by product/category.
- Move channel budget toward efficient journeys while keeping paid media in controlled experiments until landing pages and creative prove lift.
- Reconcile ecommerce orders, refunds, VAT, payment settlement and SAP postings in a monthly close pack with exception owners.
- Convert OneLake files into governed Delta tables, add Fabric Data Factory refresh monitoring, and publish the Power BI semantic model as the trusted layer for executives.

## Agent design

| agent_name | purpose | input_tables | output |
| --- | --- | --- | --- |
| Revenue Sentinel | Monitors revenue, margin, returns and anomaly signals; creates executive alerts. | MonthlyTrend, CategoryKPI, FabricProof | Power BI alert + Teams/Email summary |
| Merchandising Copilot | Recommends hero products, bundles, PDP copy fixes and attach items. | ProductKPI, MLReturnRisk, SEO roadmap | Product backlog and campaign briefs |
| Finance Reconciler | Compares ecommerce revenue, VAT, refunds and SAP posted finance extracts. | Finance Reconciliation, SAP B1/BW extracts | Audit exception register |
| Growth Experimenter | Designs A/B tests, reads results, and recommends rollouts. | AB Test Plan/Results, ChannelROI | Experiment decision memo |
| Governance Steward | Checks source freshness, PII minimization, row counts, lineage and Git proof. | Source Register, Requirements Log | Governance scorecard |

## Next best actions

| owner | action | rationale | priority | business_outcome |
| --- | --- | --- | --- | --- |
| CEO | Protect hero category | Make Apparel the board-level growth theme; it contributes R1,759,430,045 revenue. | High | Revenue growth |
| CMO | Scale efficient acquisition | Use Direct as always-on efficiency engine with ROAS 100.0x. | High | Marketing efficiency |
| COO | Reduce return leakage | Investigate Footwear return-rate drivers before increasing media spend. | Medium | Margin protection |
| Merchandising | Build margin bundle | Bundle Jacket ADV FlowTour 5.5 - Women with compatible accessories and protection products. | High | AOV and margin |
| Data Governance | Operationalize evidence | Publish source register, row counts, file hashes, capacity status and refresh runbook into monthly close pack. | High | Auditability |
| BI Ops | Investigate revenue anomaly | 2025-12 changed 12.6% versus 3-month average. | Medium | Monitoring |

## Portfolio positioning

This shows senior BI capability across architecture, data engineering, ML, AI agents, Power BI, governance, accounting reconciliation, marketing analytics and business strategy.
