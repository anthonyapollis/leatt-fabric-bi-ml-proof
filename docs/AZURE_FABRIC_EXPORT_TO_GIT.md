# Azure / Fabric Export To Git Guide

## Microsoft Fabric workspace items

Use this when you build the Lakehouse, Notebook, Data Factory pipeline, semantic model, or report inside Fabric.

1. Create or open the Fabric workspace.
2. Confirm the workspace is assigned to Fabric capacity or a supported trial/capacity.
3. In workspace settings, open **Git integration**.
4. Connect to GitHub or Azure DevOps.
5. Select repository, branch, and folder.
6. Commit supported Fabric workspace items from Fabric into Git.
7. Pull the repository locally and place the exported Fabric item folders under:
   `azure-export/fabric-workspace-items/`
8. Commit the export with a message such as:
   `Add Fabric workspace export: lakehouse, pipeline, notebook, report`

Important: Fabric Git integration is mainly metadata/source-control for supported items. It does not move the Lakehouse data itself. Keep large data in OneLake/Azure Storage and reference it through documentation/manifests.

## Fabric Data Factory pipelines

Fabric Data Factory supports CI/CD through Git integration and deployment pipelines. After creating pipelines in Fabric:

1. Connect the workspace to Git.
2. Commit the pipeline item to Git from the Fabric source control panel.
3. Review changed files in GitHub/Azure DevOps.
4. Use deployment pipelines for Dev/Test/Prod promotion.

## Azure Data Factory export

Use this if you build classic Azure Data Factory in Azure Portal.

1. Open Azure Data Factory Studio.
2. Configure Git integration first if possible.
3. Author linked services, datasets, pipelines, triggers.
4. Publish changes.
5. Use **Manage > ARM template > Export ARM template** or automated publish utilities.
6. Save exported files under:
   `azure-export/adf-arm-template/`
7. Commit files to Git.

Expected ADF files:

- `ARMTemplateForFactory.json`
- `ARMTemplateParametersForFactory.json`
- pipeline JSON files if using Git mode
- linked service JSON files with secrets parameterized

## Evidence checklist

- Screenshot Fabric workspace Git integration page.
- Screenshot Data Factory pipeline canvas.
- Screenshot successful pipeline run monitor.
- Screenshot Lakehouse table list.
- Screenshot Power BI report page.
- Commit exported workspace/ADF files.
- Commit README explaining what was built and what data is synthetic.
