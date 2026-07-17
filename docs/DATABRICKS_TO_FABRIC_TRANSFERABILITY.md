# Databricks To Microsoft Fabric Transferability

The user has prior Databricks experience. This strengthens the Senior BI Developer story because the project applies lakehouse engineering concepts in Microsoft Fabric.

## How to position it

Prior Databricks experience translates directly to Fabric through the lakehouse pattern:

| Lakehouse concept | Databricks | Microsoft Fabric |
|---|---|---|
| Unified lake storage | Cloud data lake / Delta Lake | OneLake / Lakehouse |
| Bronze layer | Raw Delta / files | OneLake `Files/Bronze` |
| Silver layer | Cleaned Delta tables | Lakehouse Silver tables/files |
| Gold layer | Curated marts | Warehouse / SQL endpoint / semantic model |
| Processing | Spark notebooks/jobs | Fabric Spark notebooks / Data Engineering |
| Pipelines | Workflows / Jobs / Delta Live Tables | Fabric Data Factory pipelines |
| BI serving | SQL Warehouse / external BI | Power BI / Direct Lake / SQL endpoint |
| ML | MLflow / Feature Store | Fabric Data Science, notebooks, ML outputs |
| Governance | Unity Catalog | Fabric workspace security, OneLake, Purview-style governance |

## Interview phrasing

> I have used Databricks before, so I understand the lakehouse architecture: Bronze/Silver/Gold data layers, scalable Spark transformations, Delta-style storage, notebooks, jobs, and ML workflows. In this project I applied that same architecture in Microsoft Fabric by landing ecommerce data into OneLake, creating a Lakehouse, designing an ERD/star schema, pushing 2M transaction rows, and preparing the data for Power BI, governance, accounting reconciliation and ML scoring.

## Why it matters

The target role asks for Microsoft Fabric, Power BI and modern data platforms. Databricks experience shows transferability across modern lakehouse tools, while this portfolio proves the same thinking in Fabric.
