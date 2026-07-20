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

---

## Update: 2026-07-20/21 — subscription re-enabled, capacity briefly resumed, re-suspended

### Context

The Azure subscription's free trial credit had expired between the last proof
capture and this session, putting the subscription into a billing-locked,
read-only state (`az fabric capacity resume` failed with
`ReadOnlyDisabledSubscription`). Anthony upgraded the subscription via the
Azure portal (Upgrade -> add payment method), which restored write access.

### What happened while resumed

1. Verified the upgrade actually restored write access: `az fabric capacity
   resume --resource-group rg-leatt-fabric-bi-ml --capacity-name leattfabricf2`
   succeeded (exit 0), capacity confirmed `state: Active` shortly after.
2. Attempted to capture live portal/workspace screenshots for this proof
   pack. Browser automation was unavailable both ways: the Chrome-extension
   navigation tool was blocked for `portal.azure.com` /
   `app.fabric.microsoft.com` in this session, and the OS-level screenshot
   tool is read-only for browsers (cannot click/navigate) and Edge was not
   in focus when checked.
3. Rather than leave paid capacity running while screenshot capture was
   blocked, the capacity was suspended immediately:
   `az fabric capacity suspend --resource-group rg-leatt-fabric-bi-ml
   --capacity-name leattfabricf2`, confirmed `state: Paused` within ~30
   seconds of the check loop.
4. Total Active window: approximately 3-4 minutes of F2 capacity time
   (a fraction of a US cent at F2's public hourly rate).

### Independent corroboration

Anthony separately screenshotted the Azure portal himself at 2026-07-20
23:56-23:57 (after the suspend), showing:

- Fabric capacities list: `leattfabricf2`, type Fabric Capacity, resource
  group `rg-leatt-fabric-bi-ml`, location South Africa North.
- Resource detail blade: **Status: Paused**, SKU **F2**, subscription ID
  `cea67e6f-62b2-4b2f-83e8-9af31093d8c8`, tags visible on the resource itself:
  `project: leatt-bi-ml`, `purpose: portfolio-proof`,
  `cost-control: delete-or-pause-after-upload`.

This matches the CLI-reported state exactly and confirms the cost-control
tags were applied directly on the Azure resource (not just in documentation).

### Fresh CLI re-verification (2026-07-21)

```text
az resource list --resource-group rg-leatt-fabric-bi-ml --output table
  -> leattfabricf2 | rg-leatt-fabric-bi-ml | southafricanorth
     | Microsoft.Fabric/capacities | Succeeded

az fabric capacity show --resource-group rg-leatt-fabric-bi-ml
  --capacity-name leattfabricf2 --output json
  -> state: Paused, sku: F2, tags: {cost-control: delete-or-pause-after-upload,
     project: leatt-bi-ml, purpose: portfolio-proof}

az resource list --output table (subscription-wide)
  -> only leattfabricf2 returned

az vm list --show-details --output table
  -> no virtual machines

az group exists --name rg-pargoparcels   (unrelated project, same subscription)
  -> false (already torn down)
```

### Conclusion

- Fabric F2 capacity is paused (re-confirmed by both CLI and portal UI).
- The one brief resume was time-boxed to a few minutes and ended in an
  explicit suspend, not left running.
- No other cost-incurring resources exist anywhere in the subscription.
- Live in-portal screenshot capture for Fabric/Data Factory workspace pages
  is still outstanding — needs either the Chrome extension granted access to
  the Azure/Fabric domains, or a short manual navigation pass with Anthony
  at the keyboard while screenshots are captured.
