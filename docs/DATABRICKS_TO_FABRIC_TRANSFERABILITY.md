# Databricks To Microsoft Fabric Transferability

This note maps common Databricks lakehouse concepts to the Microsoft Fabric implementation pattern used by the project.

## Concept Mapping

Databricks and Fabric share a lakehouse-oriented architecture pattern:

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
