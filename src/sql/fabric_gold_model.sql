-- Fabric Lakehouse/Warehouse gold model starter SQL.
-- Adapt table names to the Lakehouse or Warehouse generated in Fabric.

CREATE OR ALTER VIEW gold.vw_sales_summary_monthly AS
SELECT
    month,
    SUM(quantity) AS units_sold,
    SUM(gross_revenue_zar) AS gross_revenue_zar,
    SUM(discount_amount_zar) AS discount_amount_zar,
    SUM(net_revenue_zar) AS net_revenue_zar,
    SUM(gross_margin_zar) AS gross_margin_zar,
    SUM(return_amount_zar) AS return_amount_zar,
    SUM(gross_margin_zar) / NULLIF(SUM(net_revenue_zar), 0) AS gross_margin_rate,
    SUM(return_amount_zar) / NULLIF(SUM(net_revenue_zar), 0) AS return_value_rate
FROM silver.fact_transaction_lines
GROUP BY month;

CREATE OR ALTER VIEW gold.vw_category_performance AS
SELECT
    category,
    SUM(quantity) AS units_sold,
    SUM(net_revenue_zar) AS net_revenue_zar,
    SUM(gross_margin_zar) AS gross_margin_zar,
    SUM(return_amount_zar) AS return_amount_zar,
    SUM(gross_margin_zar) / NULLIF(SUM(net_revenue_zar), 0) AS gross_margin_rate
FROM silver.fact_transaction_lines
GROUP BY category;

CREATE OR ALTER VIEW gold.vw_channel_roi_base AS
SELECT
    channel,
    SUM(quantity) AS units_sold,
    SUM(net_revenue_zar) AS net_revenue_zar,
    SUM(gross_margin_zar) AS gross_margin_zar
FROM silver.fact_transaction_lines
GROUP BY channel;
