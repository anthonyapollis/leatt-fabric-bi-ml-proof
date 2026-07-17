# Leatt ZA Fabric and Power BI Implementation Guide

## Is Fabric in Azure?

Yes. Microsoft Fabric can be bought as Azure F SKU capacity from the Azure portal. The practical deployment path is:

1. Azure portal > search for Microsoft Fabric.
2. Create Fabric Capacity.
3. Choose subscription, resource group, region, size, and capacity admin.
4. Create a Fabric workspace and assign it to the capacity.
5. Load this package into a Lakehouse or Warehouse and publish a Power BI semantic model.

## Delivered local package

- Product catalog source: `https://za.leatt.com/products.json`
- Transaction fact rows generated: `2,000,000`
- Revenue period: `2024-01` to `2026-06`
- Repurchase model AUC: `0.810`
- Six month forecast file sheet: `Forecast`

## Fabric architecture

Bronze: raw product JSON, raw generated parquet, raw customer/order extracts.

Silver: cleaned Delta tables for products, customers, transaction lines, dates, channels, and geography.

Gold: star schema semantic tables with business-friendly names, certified metrics, and row-level security if needed.

ML: customer repurchase propensity, value segmentation, six-month revenue forecast, return-risk model, and next-best-category recommendations.

Power BI report pages:

1. Executive overview: revenue, margin, return rate, units, customer count, forecast.
2. Category performance: revenue, gross margin, return rate, ASP, discount depth.
3. Product drilldown: top products, sales mix, margin leakage, inventory/proxy demand.
4. Customer intelligence: RFM, ML segment, province, rider type, cohort, propensity.
5. Operations: fulfillment days, return value, payment mix, regional pressure.
6. ML monitor: AUC, score distribution, segment movement, forecast vs actual.

## Recommended next data sources

- Shopify orders and customers
- GA4 traffic and conversion paths
- Google Ads / Meta Ads spend
- Payment provider settlements
- Inventory and stock availability
- Returns/refunds reason codes
- Email/SMS campaign engagement

## Immediate business plays

- Build protection and helmet bundles for high-intent MTB/Moto buyers.
- Use accessories as margin-positive attach items.
- Run VIP early access campaigns before peak season.
- Create province-specific delivery and returns monitoring.
- Retarget high-propensity customers with rider-type-specific landing pages.
