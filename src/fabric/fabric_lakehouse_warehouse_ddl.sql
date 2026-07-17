-- Fabric Lakehouse/Warehouse starter DDL for the Leatt ecommerce BI/ML model.
-- In Fabric Lakehouse, create Delta tables from uploaded parquet/CSV files using Notebook or Load Table.
-- In Fabric Warehouse, adapt this DDL for relational views/tables.

CREATE TABLE gold.dim_customer (
    customer_id INT NOT NULL,
    first_seen_date DATE,
    province VARCHAR(100),
    city VARCHAR(100),
    rider_type VARCHAR(50),
    acquisition_channel VARCHAR(100),
    loyalty_tier VARCHAR(50),
    age_band VARCHAR(20),
    email_opt_in BIT
);

CREATE TABLE gold.dim_product_variant (
    variant_id BIGINT NOT NULL,
    product_id BIGINT,
    title VARCHAR(500),
    variant_title VARCHAR(255),
    handle VARCHAR(255),
    vendor VARCHAR(100),
    product_type VARCHAR(255),
    category VARCHAR(100),
    sku VARCHAR(100),
    available BIT,
    price_zar DECIMAL(18, 2),
    compare_at_price_zar DECIMAL(18, 2),
    source_url VARCHAR(1000)
);

CREATE TABLE gold.fact_transaction_lines (
    transaction_line_id BIGINT NOT NULL,
    order_id BIGINT,
    order_date DATE,
    month VARCHAR(7),
    customer_id INT,
    product_id BIGINT,
    variant_id BIGINT,
    product_title VARCHAR(500),
    category VARCHAR(100),
    channel VARCHAR(100),
    device VARCHAR(50),
    province VARCHAR(100),
    city VARCHAR(100),
    quantity INT,
    unit_price_zar DECIMAL(18, 2),
    discount_pct DECIMAL(9, 4),
    gross_revenue_zar DECIMAL(18, 2),
    discount_amount_zar DECIMAL(18, 2),
    net_revenue_zar DECIMAL(18, 2),
    estimated_unit_cost_zar DECIMAL(18, 2),
    gross_margin_zar DECIMAL(18, 2),
    return_flag BIT,
    return_amount_zar DECIMAL(18, 2),
    fulfillment_days INT,
    payment_method VARCHAR(100),
    campaign VARCHAR(100)
);

CREATE VIEW gold.vw_revenue_reconciliation AS
SELECT
    month,
    SUM(net_revenue_zar) AS sales_incl_vat_zar,
    SUM(net_revenue_zar) / 1.15 AS sales_ex_vat_zar,
    SUM(net_revenue_zar) - SUM(net_revenue_zar) / 1.15 AS output_vat_zar,
    SUM(return_amount_zar) AS refunds_incl_vat_zar,
    SUM(gross_margin_zar) AS gross_margin_zar
FROM gold.fact_transaction_lines
GROUP BY month;
