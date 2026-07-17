# Leatt Fabric Medallion Architecture: Dirty To Clean

## Why This Was Added

The project now includes a proper medallion architecture. This matters because a senior BI/Fabric project must prove how dirty operational data becomes trusted reporting data.

## Layer Design

- **Bronze:** raw append-only landing zone. Keep source defects, raw file name, source system and ingestion timestamp.
- **Silver:** cleaned and conformed data. Fix types, dates, discounts, revenue math, duplicates, casing and missing catalog mappings.
- **Gold:** business-ready marts for Power BI, ML, finance reconciliation and executive KPIs.

## Dirty Data Handled

- Missing product titles.
- Negative quantities.
- Invalid discounts above approved business threshold.
- Invalid dates.
- Revenue math mismatches.
- Duplicate transaction lines.
- Province/city standardisation issues.

## Quality Gate Result

Total dirty-rule failures in the sample: 387. All are either corrected or flagged in Silver before Gold tables are built.

## Gold Insight Example

Top Gold category in the medallion sample: **Apparel**, with R4.3m revenue and 51.8% gross margin rate.

## Fabric Fit

Data Factory lands files into Bronze. Fabric Lakehouse notebooks or Dataflow Gen2 apply Silver quality rules. Gold tables/views feed Power BI semantic models, ML scoring, SAP reconciliation and governance reports.

Generated 2026-07-17 23:39.
