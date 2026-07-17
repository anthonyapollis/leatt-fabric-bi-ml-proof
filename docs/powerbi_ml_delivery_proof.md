# Power BI And ML Delivery Proof

Generated: 2026-07-17

## Power BI semantic model

| Field | Value |
|---|---|
| Workspace | `Apollis` |
| Workspace ID | `e515bafe-7290-4832-ae1d-514be43a9d87` |
| Dataset / semantic model | `Leatt Fabric BI ML Semantic Model 202607171909` |
| Dataset ID | `9ee6f8a0-aec0-48ff-a44c-15985f3bd4bc` |
| Web URL | `https://app.powerbi.com/groups/e515bafe-7290-4832-ae1d-514be43a9d87/datasets/9ee6f8a0-aec0-48ff-a44c-15985f3bd4bc` |
| Configured by | `anthony@the-spot.tech` |
| Add rows API enabled | `true` |

## Tables loaded into Power BI semantic model

- `ExecutiveKPI`
- `MonthlyTrend`
- `CategoryKPI`
- `ChannelROI`
- `MLReturnRisk`
- `MLMetrics`
- `FabricProof`

## ML model

| Metric | Value |
|---|---:|
| Model | Return Risk Logistic Regression |
| Training rows | 90,000 |
| Test rows | 30,000 |
| AUC | 0.589 |
| Accuracy | 0.465 |
| Precision | 0.075 |
| Recall | 0.718 |

The return-risk model is intentionally recall-oriented: it catches a high share of potential returns but has low precision, which is typical for an early operational risk screen. It should be improved with real return reason codes, sizing data, delivery events, product reviews and support tickets.

## Screenshots created

- `outputs/screenshots/powerbi_executive_overview.png`
- `outputs/screenshots/powerbi_ml_monitoring.png`
- `outputs/screenshots/powerbi_marketing_fabric_proof.png`

## Relationship to the full dataset

The full 2,000,000-row fact table is stored in Microsoft Fabric OneLake:

```text
Apollis/Leatt_BI_ML_Lakehouse.Lakehouse/Files/Bronze/leatt_ecommerce_transactions_2m.parquet
```

The Power BI push semantic model contains curated reporting/ML aggregates and proof tables. In a production build, Power BI should connect directly to the Fabric Lakehouse/SQL endpoint or Direct Lake semantic model for the full dataset.
