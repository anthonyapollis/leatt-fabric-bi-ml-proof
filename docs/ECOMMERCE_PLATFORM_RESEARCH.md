# Ecommerce Platform Research

## Conclusion

`za.leatt.com` is running on **Shopify / Shopify-hosted storefront infrastructure**.

Confidence: **High**

## Evidence

| Signal | Finding |
|---|---|
| HTTP response header | `powered-by: Shopify` |
| Product endpoint | `https://za.leatt.com/products.json?limit=1` returns Shopify-style product/variant JSON |
| Cart endpoint | `https://za.leatt.com/cart.js` returns cart JSON including token, item count, items, totals and `currency: ZAR` |
| CDN/assets | HTML uses `https://cdn.shopify.com` and `/cdn/shop/t/2/assets/...` |
| Prior catalog extraction | `11,354` product variants were extracted from the public product JSON endpoint |

## SAP Hybris / SAP Commerce Cloud

SAP Hybris is now SAP Commerce Cloud. It is **possible** as an enterprise ecommerce platform, but there is no public evidence from the tested Leatt ZA storefront that it is the live ecommerce platform for `za.leatt.com`.

For this project:

```text
Shopify storefront
  -> Fabric Data Factory REST extraction
  -> OneLake/Lakehouse
  -> BI, ML, SEO, A/B testing and governance
  -> SAP Business One or SAP BW finance reconciliation if available
```

SAP Commerce Cloud would fit only if the business actually runs its commerce platform on SAP:

```text
SAP Commerce Cloud / Hybris
  -> product, catalog, cart, order, promotion and customer APIs
  -> Fabric Data Factory
  -> Lakehouse / Warehouse
  -> Power BI and ML
  -> SAP finance reconciliation
```

## Recommended data-source stance

- Use Shopify as the ecommerce/catalog source.
- Use authorized Shopify Admin exports/API for real order/customer data.
- Use SAP Business One or SAP BW as the accounting/finance source of record if available.
- Use Fabric as the governed analytics, ML and reporting layer.

