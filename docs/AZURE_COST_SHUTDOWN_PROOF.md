# Azure Cost Shutdown Proof

Date: 2026-07-17

## Result

Cost-incurring Azure compute for this project has been stopped/paused.

## Verified Azure Subscription

- Subscription name: Azure subscription 1
- Tenant: SINGLE POINT OF TRUTH (PTY) LTD
- Tenant domain: the-spot.tech

## Project Resource Scan

Command used:

```powershell
az resource list --resource-group rg-leatt-fabric-bi-ml --output table
```

Only one project resource was found:

| Name | Resource group | Location | Type | Provisioning status |
|---|---|---|---|---|
| leattfabricf2 | rg-leatt-fabric-bi-ml | southafricanorth | Microsoft.Fabric/capacities | Succeeded |

## Fabric Capacity State

Command used:

```powershell
az fabric capacity show --resource-group rg-leatt-fabric-bi-ml --capacity-name leattfabricf2 --output json
```

Verified state:

```text
state: Paused
sku: F2
location: South Africa North
```

## Subscription-Wide Resource Scan

Command used:

```powershell
az resource list --output table
```

The scan returned only the Fabric capacity `leattfabricf2`.

## Virtual Machine Check

Command used:

```powershell
az vm list --show-details --output table
```

No virtual machines were returned.

## Cost-Control Conclusion

- Fabric F2 capacity is paused.
- No Azure VMs are running.
- No additional Azure resources were visible in the subscription scan.
- No Azure Data Factory, Databricks, SQL Database, App Service, Synapse, OpenAI, or other paid compute resources were visible in the Azure CLI scan.

This preserves the project proof while stopping the main Azure cost risk.
