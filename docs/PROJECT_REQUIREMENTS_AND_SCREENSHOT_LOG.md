# Project Requirements And Screenshot / Evidence Log

This file tracks the user requirements, completed proof artifacts, and screenshots/evidence that should be captured during Azure/Fabric work.

## Must-have proof

- ERD and data model.
- Millions of rows generated.
- Data pushed to Azure/Fabric OneLake.
- Fabric Lakehouse and Data Factory item.
- BI/ML reports.
- Accounting reconciliation, governance and SAP source mapping.
- Ecommerce platform research.
- Git commits and source-control proof.

## Completed Fabric deployment

| Item | Value |
|---|---|
| Workspace | `Apollis` |
| Capacity | `fabric-capacity-redacted` |
| SKU | `F2` |
| Region | `Azure region redacted` |
| Lakehouse | `Leatt_BI_ML_Lakehouse` |
| Lakehouse ID | `dca60749-eaef-410e-9121-ea16eedbc975` |
| SQL endpoint ID | `433371a2-1f06-4053-999e-7f8ee95ba5c9` |
| Data Factory pipeline | `pipeline name redacted for public sharing` |
| Pipeline ID | `pipeline-id-redacted` |

## Uploaded data

- `Files/Bronze/leatt_ecommerce_transactions_2m.parquet` - 2,000,000 rows, 90,699,835 bytes.
- `Files/Bronze/leatt_product_catalog.csv` - 11,354 product variants.
- `Files/Bronze/leatt_synthetic_customers.csv` - 180,000 customers.
- `Files/Silver/leatt_customer_ml_scores.csv` - customer ML scoring output.

## Screenshot checklist

Capture screenshots for:

1. Azure resource group.
2. Fabric capacity and SKU.
3. Workspace assigned to capacity.
4. Workspace item list.
5. Lakehouse overview.
6. Lakehouse `Files/Bronze` folder.
7. `leatt_ecommerce_transactions_2m.parquet` file details.
8. Lakehouse `Files/Silver` folder.
9. Data Factory pipeline item.
10. SQL endpoint.
11. Power BI report pages.
12. Git commit history.

## Screenshot naming

```text
YYYYMMDD_HHMM_context_short-description.png
```

## Cost control

Capacity `fabric-capacity-redacted` is active. Pause when done:

```powershell
az fabric capacity suspend --resource-group <resource-group> --capacity-name <capacity-name>
```
