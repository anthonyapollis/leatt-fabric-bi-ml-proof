# Fabric Cost Control And Handover

The Fabric Fabric capacity is the main ongoing cost item. Keep it running only while proving or refreshing the project.

Final handover status on 2026-07-17: `fabric-capacity-redacted` verified as `Paused` in Azure CLI after project completion.

Suspend:

```powershell
az fabric capacity suspend --resource-group <resource-group> --capacity-name <capacity-name>
```

Resume:

```powershell
az fabric capacity resume --resource-group <resource-group> --capacity-name <capacity-name>
```

Recommended next production hardening:

- Convert Lakehouse `Files/Bronze` parquet/CSV files to Delta tables.
- Add Data Factory pipeline activity logging and scheduled refresh.
- Add row-count, null-check and reconciliation tests.
- Restrict access with workspace roles and PII minimization.
- Create a monthly close evidence pack with source paths, row counts, Git commit and semantic model refresh time.
