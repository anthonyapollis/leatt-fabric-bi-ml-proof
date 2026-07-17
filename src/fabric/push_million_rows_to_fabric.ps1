param(
    [string]$WorkspaceId = "e515bafe-7290-4832-ae1d-514be43a9d87",
    [string]$LakehouseName = "Leatt_BI_ML_Lakehouse"
)

$ErrorActionPreference = "Stop"

$fabricToken = az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv
$fabricHeaders = @{
    Authorization = "Bearer $fabricToken"
    "Content-Type" = "application/json"
}

Write-Host "Listing workspace items..."
Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items" -Headers $fabricHeaders -Method Get | ConvertTo-Json -Depth 8

Write-Host "Creating lakehouse if Fabric capacity is enabled..."
$body = @{
    displayName = $LakehouseName
    description = "Leatt ecommerce BI ML lakehouse with 2M transaction rows"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/lakehouses" -Headers $fabricHeaders -Method Post -Body $body | ConvertTo-Json -Depth 8

Write-Host "If creation succeeds, upload files using OneLake File Explorer, Azure Storage Explorer, or ADLS-compatible SDK to:"
Write-Host "https://onelake.dfs.fabric.microsoft.com/<workspace>/<lakehouse>.Lakehouse/Files/Bronze/"
