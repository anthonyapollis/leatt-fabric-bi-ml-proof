# Fabric Cost Control And Handover

The Fabric F2 capacity is the main ongoing cost item. Keep it running only while proving or refreshing the project.

Suspend:

```powershell
az fabric capacity suspend --resource-group rg-leatt-fabric-bi-ml --capacity-name leattfabricf2
```

Resume:

```powershell
az fabric capacity resume --resource-group rg-leatt-fabric-bi-ml --capacity-name leattfabricf2
```

Recommended next production hardening:

- Convert Lakehouse `Files/Bronze` parquet/CSV files to Delta tables.
- Add Data Factory pipeline activity logging and scheduled refresh.
- Add row-count, null-check and reconciliation tests.
- Restrict access with workspace roles and PII minimization.
- Create a monthly close evidence pack with source paths, row counts, Git commit and semantic model refresh time.
