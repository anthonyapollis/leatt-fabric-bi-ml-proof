# SAP Accounting, Data Auditing and Governance Integration

## Recommended accounting pattern

Use SAP Business One or SAP BW as the finance/accounting system of record, and use Microsoft Fabric for extraction, reconciliation, governance, ML and reporting.

The ecommerce web/catalog data is useful operational data, but posted accounting values should reconcile back to SAP invoices, credit notes, payments, journal entries and VAT accounts.

## SAP Business One datasource

SAP Business One Service Layer exposes business objects over HTTP/OData. Useful objects:

- `Invoices`
- `CreditNotes`
- `IncomingPayments`
- `JournalEntries`
- `ChartOfAccounts`
- `BusinessPartners`
- `Items`

Example Fabric Data Factory extraction pattern:

```text
SAP Business One Service Layer /b1s/v2/Invoices
  -> Fabric Data Factory REST/OData copy
  -> OneLake Bronze JSON
  -> Lakehouse Silver invoice tables
  -> Gold finance reconciliation model
```

## SAP BW datasource

SAP BW queries can be exposed as OData queries through SAP Gateway. Use BW when finance, sales, inventory or profitability cubes are already trusted and governed by SAP.

## SAP Hybris / SAP Commerce Cloud

Hybris is now SAP Commerce Cloud. It is not required for this demo, but it is possible and valuable if the ecommerce site is actually running on SAP Commerce Cloud.

Where it fits:

- Upstream commerce platform.
- Source for products, catalog, pricing, promotions, customers, carts, orders and web journeys.
- Feeds Fabric analytics and ERP/accounting posting flows.

Where it does not fit:

- It should not be treated as the statutory accounting ledger.
- Use SAP Business One, SAP ERP/S/4HANA or SAP BW for accounting reconciliation and posted finance.

## VAT

South African VAT is modeled at 15% for this demo. Consumer ecommerce revenue is treated as VAT-inclusive and split into sales excluding VAT plus output VAT.

Generated on 2026-07-17 17:50.
