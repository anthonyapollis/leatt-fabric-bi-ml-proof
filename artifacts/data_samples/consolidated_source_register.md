# Consolidated Source Register

Updated: 2026-07-17

## Leatt ZA product JSON
- URL/File: https://za.leatt.com/products.json
- Type: Public ecommerce catalog endpoint
- Used for: Product, variant, price, SKU, availability, tags, category classification seed.

## Leatt ZA About Us
- URL/File: https://za.leatt.com/pages/about-us
- Type: Public website page
- Used for: Brand and business context in the ebook narrative.

## Leatt ZA Moto Boots collection
- URL/File: https://za.leatt.com/collections/moto-boots
- Type: Public website page and user screenshot
- Used for: Visual proof of product assortment/pricing and portfolio evidence.

## Microsoft Fabric Data Factory documentation
- URL/File: https://learn.microsoft.com/en-us/fabric/data-factory/
- Type: Official Microsoft documentation
- Used for: Fabric ingestion, transformation, and orchestration process design.

## Azure Data Factory documentation
- URL/File: https://learn.microsoft.com/en-us/azure/data-factory/
- Type: Official Microsoft documentation
- Used for: Azure ETL/data integration positioning and ADF process evidence.

## Azure Data Factory Copy Activity overview
- URL/File: https://learn.microsoft.com/en-us/azure/data-factory/copy-activity-overview
- Type: Official Microsoft documentation
- Used for: Copy activity pattern for source-to-cloud movement.

## Microsoft Fabric OneLake overview
- URL/File: https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview
- Type: Official Microsoft documentation
- Used for: Unified data lake and OneLake architecture explanation.

## Microsoft Fabric Lakehouse overview
- URL/File: https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview
- Type: Official Microsoft documentation
- Used for: Lakehouse, Delta, Spark/SQL, Power BI integration design.

## Microsoft Fabric subscription / Azure F SKUs
- URL/File: https://learn.microsoft.com/en-us/fabric/enterprise/buy-subscription
- Type: Official Microsoft documentation
- Used for: Confirming Fabric capacity can be purchased through Azure portal.

## Power BI Direct Lake overview
- URL/File: https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-overview
- Type: Official Microsoft documentation
- Used for: Power BI semantic model design for high-volume Delta tables in OneLake.

## Generated synthetic ecommerce transactions
- URL/File: outputs/leatt_ecommerce_transactions_2m.parquet
- Type: Generated dataset
- Used for: Million-row transaction fact table for BI/ML modeling; synthetic, not Leatt actual sales.

## Generated SQLite warehouse
- URL/File: outputs/leatt_ecommerce_warehouse.sqlite
- Type: Generated local warehouse
- Used for: Dimensional model, fact table, and BI aggregations.

## Fox Racing Moto Gear
- URL/File: https://www.foxracing.com/moto.html
- Type: Competitor official site
- Used for: Competitor category and positioning analysis.

## Fox Racing MTB Gear
- URL/File: https://www.foxracing.com/mtb.html
- Type: Competitor official site
- Used for: Competitor MTB category analysis.

## 100% Goggles
- URL/File: https://www.100percent.com/pages/100-goggles
- Type: Competitor official site
- Used for: Eyewear/goggle positioning analysis.

## Oakley MX Goggles
- URL/File: https://www.oakley.com/en-us/category/goggles/motocross
- Type: Competitor official site
- Used for: Optics and motocross eyewear positioning.

## SCOTT MTB Goggles
- URL/File: https://www.scott-sports.com/us/en/products/bike-equipment-mw-goggles
- Type: Competitor official site
- Used for: Goggle product/pricing range comparison.

## Leatt eyewear screenshot
- URL/File: outputs/evidence_images/leatt_lifestyle_eyewear_collection.png
- Type: User-provided screenshot
- Used for: Evidence for eyewear product and pricing context.

## SAP Business One Service Layer
- URL/File: https://help.sap.com/docs/SAP_BUSINESS_ONE/f110a154dd0f4c20bf7f3ebca9eeb794/60c7a0b745bd486589f05a1da77041f3.html?locale=en-US
- Type: Official SAP documentation
- Used for: SAP Business One OData/HTTP extraction design.

## SAP Business One Service Layer API Reference
- URL/File: https://help.sap.com/doc/056f69366b5345a386bb8149f1700c19/10.0/en-US/Service%20Layer%20API%20Reference.html
- Type: Official SAP documentation
- Used for: Business object and OData endpoint mapping.

## SAP BW OData Queries
- URL/File: https://help.sap.com/docs/SUPPORT_CONTENT/bwplaolap/3361382894.html
- Type: Official SAP documentation
- Used for: SAP BW query extraction option through OData.

## SAP Commerce / Hybris
- URL/File: https://www.sap.com/products/acquired-brands/what-is-hybris.html
- Type: Official SAP page
- Used for: Explains Hybris is now SAP Commerce Cloud and where it fits.

## SARS VAT rate
- URL/File: https://www.sars.gov.za/types-of-tax/value-added-tax/
- Type: Official SARS page
- Used for: VAT rate assumption for South African ecommerce accounting model.

## Leatt ZA live Shopify platform check
- URL/File: https://za.leatt.com
- Type: Live endpoint/header inspection
- Used for: Confirmed powered-by Shopify header and Shopify CDN/theme asset usage.

## Leatt ZA products JSON
- URL/File: https://za.leatt.com/products.json?limit=1
- Type: Live public endpoint
- Used for: Confirmed Shopify-style product JSON endpoint.

## Leatt ZA cart JSON
- URL/File: https://za.leatt.com/cart.js
- Type: Live public endpoint
- Used for: Confirmed Shopify Ajax cart endpoint and ZAR cart object.

## Shopify Ajax API documentation
- URL/File: https://shopify.dev/docs/api/ajax
- Type: Official Shopify documentation
- Used for: Validated /cart.js behavior and Shopify-hosted Ajax API context.

## Shopify Liquid product object documentation
- URL/File: https://shopify.dev/docs/api/liquid/objects/product
- Type: Official Shopify documentation
- Used for: Validated product/variant/handle/price concepts used in extraction.
