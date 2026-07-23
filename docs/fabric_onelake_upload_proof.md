# Fabric OneLake Upload Proof

Generated: 2026-07-17

## Azure / Fabric resources created or used

| Resource | Value |
|---|---|
| Azure subscription | `Azure subscription 1` |
| Tenant | `SINGLE POINT OF TRUTH (PTY) LTD` |
| Resource group | `rg-leatt-fabric-bi-ml` |
| Fabric capacity | `fabric-capacity-redacted` |
| Fabric capacity SKU | `F2` |
| Capacity region | `Azure region redacted` |
| Power BI/Fabric capacity ID | `4137aea9-adf5-4759-9a49-20de9c246633` |
| Workspace | `Apollis` |
| Workspace ID | `e515bafe-7290-4832-ae1d-514be43a9d87` |
| Lakehouse | `Leatt_BI_ML_Lakehouse` |
| Lakehouse ID | `dca60749-eaef-410e-9121-ea16eedbc975` |
| SQL endpoint item | `Leatt_BI_ML_Lakehouse` |
| SQL endpoint ID | `433371a2-1f06-4053-999e-7f8ee95ba5c9` |
| Data Factory pipeline item | `pipeline name redacted for public sharing` |
| Data Factory pipeline ID | `pipeline-id-redacted` |

## Uploaded OneLake files

| Layer | OneLake path | Bytes | Purpose |
|---|---|---:|---|
| Bronze | `Apollis/Leatt_BI_ML_Lakehouse.Lakehouse/Files/Bronze/leatt_ecommerce_transactions_2m.parquet` | `90,699,835` | 2,000,000-row ecommerce transaction fact table |
| Bronze | `Apollis/Leatt_BI_ML_Lakehouse.Lakehouse/Files/Bronze/leatt_product_catalog.csv` | `8,928,066` | Shopify/Leatt product catalog, 11,354 variants |
| Bronze | `Apollis/Leatt_BI_ML_Lakehouse.Lakehouse/Files/Bronze/leatt_synthetic_customers.csv` | `13,464,222` | 180,000 synthetic customers |
| Silver | `Apollis/Leatt_BI_ML_Lakehouse.Lakehouse/Files/Silver/leatt_customer_ml_scores.csv` | `31,034,720` | Customer propensity/value ML scores |

## Verified local source counts

| Table/file | Count |
|---|---:|
| `fact_transaction_lines` | `2,000,000` rows |
| `dim_customer` | `180,000` rows |
| `dim_product_variant` | `11,354` rows |

## Upload method

Files were uploaded with the ADLS Gen2-compatible OneLake API using Azure CLI authentication and append/flush file operations.

Uploader script:

```text
work/upload_to_onelake.py
```

Example:

```powershell
python work\upload_to_onelake.py --workspace "Apollis" --lakehouse "Leatt_BI_ML_Lakehouse" --local-file outputs\leatt_ecommerce_transactions_2m.parquet --remote-path "Files/Bronze/leatt_ecommerce_transactions_2m.parquet"
```

## Data Factory item

A production Fabric Data Factory pipeline design is documented for implementation:

```text
pipeline name redacted for public sharing
```

This item documents the managed Fabric Data Factory layer for the Lakehouse load. The physical files were already pushed into OneLake `Files/Bronze` and `Files/Silver`.

## Cost control note

Fabric capacity details are redacted for public sharing. Cost control was verified separately.

```powershell
az fabric capacity suspend --resource-group <resource-group> --capacity-name <capacity-name>
```

or delete the resource group when no longer needed:

```powershell
az group delete --name rg-leatt-fabric-bi-ml
```

