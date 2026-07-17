-- Leatt Fabric Medallion Architecture Blueprint
-- Use in Fabric Lakehouse/Warehouse after landing files in OneLake.

-- BRONZE: append-only raw data. Keep source columns and ingestion metadata.
create schema if not exists bronze;
create table if not exists bronze.orders_raw (
    transaction_line_id bigint,
    order_id bigint,
    order_date varchar(50),
    product_id bigint,
    product_title varchar(500),
    category varchar(100),
    channel varchar(80),
    province varchar(120),
    city varchar(120),
    quantity int,
    unit_price_zar decimal(18,2),
    discount_pct decimal(9,4),
    gross_revenue_zar decimal(18,2),
    discount_amount_zar decimal(18,2),
    net_revenue_zar decimal(18,2),
    return_flag int,
    source_system varchar(120),
    raw_file_name varchar(500),
    ingested_at_utc datetime2
);

-- SILVER: clean, conformed and deduplicated.
create schema if not exists silver;
create table if not exists silver.fact_order_lines_clean (
    transaction_line_id bigint not null,
    order_id bigint not null,
    order_date date not null,
    month varchar(7) not null,
    customer_id bigint,
    product_id bigint,
    product_title varchar(500) not null,
    category varchar(100) not null,
    channel varchar(80) not null,
    province varchar(120),
    city varchar(120),
    quantity int not null,
    unit_price_zar decimal(18,2) not null,
    discount_pct decimal(9,4) not null,
    net_revenue_zar decimal(18,2) not null,
    gross_margin_zar decimal(18,2) not null,
    return_flag bit not null,
    silver_quality_status varchar(40),
    source_issue_text varchar(1000)
);

-- GOLD: business-friendly marts for Power BI and finance reconciliation.
create schema if not exists gold;
create view gold.category_kpis as
select
    category,
    sum(net_revenue_zar) as net_revenue_zar,
    sum(gross_margin_zar) as gross_margin_zar,
    sum(case when return_flag = 1 then net_revenue_zar else 0 end) as return_amount_zar,
    count(distinct order_id) as orders,
    sum(quantity) as units
from silver.fact_order_lines_clean
group by category;

create view gold.monthly_revenue_margin as
select
    month,
    sum(net_revenue_zar) as net_revenue_zar,
    sum(gross_margin_zar) as gross_margin_zar,
    sum(case when return_flag = 1 then net_revenue_zar else 0 end) as return_amount_zar
from silver.fact_order_lines_clean
group by month;
