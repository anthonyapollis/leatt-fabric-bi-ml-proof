# Decision Intelligence Playbook

Generated: 2026-07-17 20:37

This layer turns the BI project into a management system. It defines what each signal means, when to act, who owns the action, and how to explain the decision.

## Signal Rules

| signal | current_reading | health | threshold_or_rule | what_it_means | owner | recommended_decision |
| --- | --- | --- | --- | --- | --- | --- |
| Revenue momentum | R3,994,247,413 | Healthy scale | If monthly movement exceeds +/-12%, explain by category, channel and stock. | 2025-12 moved 12.6% versus 3-month signal | BI Ops | Trigger exception commentary in the monthly trading pack. |
| Margin quality | 48.5% | Strong but must be protected | If margin rate falls below 45%, inspect discounting, COGS and channel mix. | Growth is valuable because modeled margin is still high. | CFO / Merchandising | Protect margin-positive product mix and bundle high-margin items. |
| Return leakage | 4.9% | Watchlist | If return rate exceeds 5%, prioritize category root-cause work before scaling media. | Footwear has the highest return-rate signal. | COO / CX | Improve sizing, delivery promise, PDP content and post-purchase guidance. |
| Hero category concentration | Apparel R1,759,430,045 | Strategic dependency | If one category exceeds 35% share, manage stockout and campaign dependency risk. | Apparel is a growth engine but also a concentration risk. | CEO / Supply | Create availability alerts and category-specific SEO/story pages. |
| Channel efficiency | Direct 100.0x ROAS | Scale carefully | Scale only when ROAS, margin and conversion all stay above threshold. | Paid Social is the lowest-ROAS channel and should stay experimental. | CMO | Move spend toward efficient journeys; keep paid experiments controlled. |
| Data completeness | 2,000,000 rows | Audit-ready | If row counts differ from expected load by >1%, block semantic model promotion. | Million-row scale is loaded and traceable to OneLake/Git proof. | Data Governance | Publish source, target, row count and commit ID in every close pack. |
| Cloud cost | Fabric F2 paused | Controlled | If no active demo or refresh, capacity must be paused. | Capacity was paused after handover to protect remaining credit. | BI Platform Owner | Resume only for refresh/demo, then pause again. |

## Prioritized Business Initiatives

| initiative | hypothesis | evidence | estimated_value | confidence | effort | priority_score | owner | next_step |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Return leakage reduction sprint | Footwear returns can be reduced with fit guidance, PDP content and post-purchase education. | Portfolio return leakage is 4.9%; Footwear is the highest-risk category. | R19,750,642 | Medium | Medium | 92 | COO / CX | Create return-reason taxonomy and product-level return dashboard. |
| Hero category availability and SEO program | Apparel deserves protected stock, SEO hubs and executive tracking. | Apparel contributes R1,759,430,045 modeled revenue. | R12,808,359 | High | Medium | 90 | CEO / Ecommerce | Build category scorecard with stockout, ranking, margin and landing page signals. |
| Margin-positive bundle testing | Bundling Jacket ADV FlowTour 5.5 - Women with accessories can increase AOV without margin dilution. | AOV and gross margin are the cleanest basket-quality measures. | R19,384,973 | Medium | Low | 88 | Merchandising / CMO | Run A/B test: product page bundle versus normal recommendation carousel. |
| Channel budget guardrails | Direct is efficient, but paid budget should expand only through controlled tests. | Best observed ROAS signal is 100.0x. | R7,753,989 | Medium | Low | 84 | CMO | Set campaign guardrails: minimum ROAS, conversion lift and margin contribution. |
| SAP close reconciliation automation | Order/refund/VAT/payment exceptions can be reduced by automated SAP B1/BW reconciliation. | Finance pack already maps ecommerce facts to accounting controls and exception registers. | Risk reduction / faster close | High | Medium | 82 | CFO / BI Lead | Schedule monthly exception pack with owner, SLA and SAP account mapping. |

## Root-Cause Playbook

| problem | diagnostic_branch | question_to_ask | data_needed | likely_interpretation |
| --- | --- | --- | --- | --- |
| Revenue down | Category demand | Which categories moved versus 3-month average? | MonthlyTrend + CategoryKPI | Campaign issue, product availability, seasonality or assortment gap. |
| Revenue down | Channel mix | Did traffic/revenue shift away from efficient channels? | ChannelROI | Media allocation, SEO ranking or landing-page relevance issue. |
| Margin down | Discounting | Did discount depth increase by category/channel? | Fact transactions + ProductKPI | Promo overuse or weak pricing control. |
| Margin down | Returns | Are returns rising in a specific category/product? | MLReturnRisk + Accounting Pack | Sizing, content, fulfillment or quality leakage. |
| Returns up | Product fit | Are high-risk items clustered by category, size or product line? | ML scores + ProductKPI | Improve size guide, PDP detail and customer education. |
| Returns up | Fulfillment | Are return rates linked to fulfillment days or province? | Fact transactions + ProvinceKPI | Delivery promise or regional service gap. |
| ROAS down | Traffic quality | Is revenue falling while spend remains high? | MarketingROI | Creative fatigue, wrong audience, poor landing page. |
| Audit exception | Data lineage | Do source/target row counts reconcile? | Source Register + Fabric Proof | Duplicate, missing or stale pipeline load. |

## Executive Storyline

| story_moment | intelligent_position | how_to_say_it |
| --- | --- | --- |
| Board message | The project has moved beyond reporting into an operating model: every KPI has a signal rule, owner and decision. | Use this to demonstrate senior BI leadership, not dashboard production. |
| Commercial message | Growth is meaningful only if margin, return leakage and channel economics stay healthy. | Open with revenue, then immediately explain margin and returns. |
| ML message | The return-risk model is a recall-focused watchlist, not a magic answer. | This is mature: it says how the model should and should not be used. |
| Governance message | The row counts, OneLake paths, Git commits and paused capacity make the work auditable. | This answers 'prove it' and 'what did it cost?' in the same story. |
| Next decision | Return leakage reduction sprint | Create return-reason taxonomy and product-level return dashboard. |
