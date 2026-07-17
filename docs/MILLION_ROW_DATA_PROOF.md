# Million Row Data Proof

This project includes a generated ecommerce fact table at million-row scale.

## Verified row counts

| Asset | Verified count |
|---|---:|
| `fact_transaction_lines` | 2,000,000 rows |
| `dim_customer` | 180,000 rows |
| `dim_product_variant` | 11,354 rows |

## Verified business totals

| Metric | Value |
|---|---:|
| Net revenue in generated fact table | R3,994,247,412.56 |

## Large files kept outside normal Git

These files are intentionally excluded from normal Git history because they are large generated data assets. Store them in Microsoft Fabric OneLake, Azure Storage, SharePoint, or Git LFS for production proof.

| File | Size | Purpose |
|---|---:|---|
| `outputs/leatt_ecommerce_transactions_2m.parquet` | 90,699,835 bytes | 2M-row transaction fact table |
| `outputs/leatt_ecommerce_warehouse.sqlite` | 565,112,832 bytes | Local dimensional warehouse with fact, dimensions, and aggregations |
| `outputs/leatt_customer_ml_scores.csv` | 31,034,720 bytes | Customer ML propensity/value scores |

## SHA256 proof

| File | SHA256 |
|---|---|
| `leatt_ecommerce_transactions_2m.parquet` | `AF350C0D018509C267FDAE4F507E9D20C8888DDD059317B0BBC9776BC5C8A53E` |

The SQLite warehouse row count was verified by SQL. Its file hash was not recorded because the local file was locked by another process at the time of proof generation.

## Verification SQL

```sql
SELECT COUNT(*) FROM fact_transaction_lines;
SELECT COUNT(*) FROM dim_customer;
SELECT COUNT(*) FROM dim_product_variant;
SELECT ROUND(SUM(net_revenue_zar), 2) FROM fact_transaction_lines;
```

## Why the full files are not committed

Normal Git repositories should not carry very large generated database and parquet files. The correct enterprise pattern is:

1. Commit the source code, manifests, schemas, proof documents, and small samples.
2. Store the large facts in OneLake or Azure Storage.
3. Commit Fabric workspace items, pipeline definitions, notebooks, SQL, and semantic model metadata.
4. Use manifests, hashes, row counts, and screenshots to prove the scale and lineage.

