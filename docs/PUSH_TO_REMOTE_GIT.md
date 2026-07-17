# Push This Proof Package To GitHub Or Azure Repos

## Option 1: GitHub

Create an empty GitHub repository first, then run:

```powershell
cd "C:\Users\Anthony.DESKTOP-ES5HL78\Documents\Codex\2026-07-17\files-mentioned-by-the-user-codex-3\outputs\leatt-fabric-bi-ml-git-proof"
git remote add origin https://github.com/YOUR_USERNAME/leatt-fabric-bi-ml.git
git push -u origin main
```

## Option 2: Azure Repos

Create an empty Azure Repos repository first, then run:

```powershell
cd "C:\Users\Anthony.DESKTOP-ES5HL78\Documents\Codex\2026-07-17\files-mentioned-by-the-user-codex-3\outputs\leatt-fabric-bi-ml-git-proof"
git remote add origin https://dev.azure.com/YOUR_ORG/YOUR_PROJECT/_git/leatt-fabric-bi-ml
git push -u origin main
```

## After Fabric or Azure Data Factory export

1. Copy Fabric workspace item exports into `azure-export/fabric-workspace-items/`.
2. Copy Azure Data Factory ARM template exports into `azure-export/adf-arm-template/`.
3. Run:

```powershell
git status
git add azure-export docs artifacts
git commit -m "Add Azure Fabric workspace and Data Factory exports"
git push
```

## Proof screenshots to add after portal work

- Fabric workspace Git integration connected to this repo.
- Fabric Data Factory pipeline canvas.
- Successful Fabric pipeline run.
- Lakehouse table list.
- Power BI report connected to semantic model.
- Azure Data Factory ARM template export folder, if using classic ADF.

Do not commit secrets, access keys, connection strings, billing details, or unredacted account screenshots.
