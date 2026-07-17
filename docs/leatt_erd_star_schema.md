# Leatt Ecommerce BI/ML ERD

```mermaid
erDiagram
    DIM_CUSTOMER ||--o{ FACT_TRANSACTION_LINES : customer_id
    DIM_PRODUCT_VARIANT ||--o{ FACT_TRANSACTION_LINES : variant_id
    DIM_DATE ||--o{ FACT_TRANSACTION_LINES : order_date
    DIM_CUSTOMER ||--|| CUSTOMER_ML_SCORES : customer_id
    FACT_TRANSACTION_LINES }o--|| FINANCE_RECONCILIATION : month

    DIM_CUSTOMER {
        int customer_id PK
        date first_seen_date
        string province
        string city
        string rider_type
        string acquisition_channel
        string loyalty_tier
        string age_band
        boolean email_opt_in
    }

    DIM_PRODUCT_VARIANT {
        long variant_id PK
        long product_id
        string title
        string sku
        string category
        decimal price_zar
        boolean available
        string source_url
    }

    DIM_DATE {
        date date_key PK
        string month
        int quarter
        int year
        string weekday_name
        boolean is_weekend
    }

    FACT_TRANSACTION_LINES {
        long transaction_line_id PK
        long order_id
        date order_date
        string month
        int customer_id FK
        long variant_id FK
        int quantity
        decimal gross_revenue_zar
        decimal discount_amount_zar
        decimal net_revenue_zar
        decimal gross_margin_zar
        boolean return_flag
        decimal return_amount_zar
        string channel
        string payment_method
        string campaign
    }

    CUSTOMER_ML_SCORES {
        int customer_id FK
        decimal repurchase_propensity
        decimal customer_value_score
        string ml_segment
        decimal margin_rate
        decimal return_rate
    }

    FINANCE_RECONCILIATION {
        string month PK
        decimal sales_incl_vat_zar
        decimal sales_ex_vat_zar
        decimal net_output_vat_zar
        decimal refunds_incl_vat_zar
        decimal payment_gateway_fee_zar
        decimal cash_expected_zar
    }
```

## Physical proof

- `fact_transaction_lines`: 2,000,000 rows
- `dim_customer`: 180,000 rows
- `dim_product_variant`: 11,354 rows
- Local full fact file: `outputs/leatt_ecommerce_transactions_2m.parquet`
- Local warehouse: `outputs/leatt_ecommerce_warehouse.sqlite`
- Fabric target: OneLake / Lakehouse `Files/Bronze/leatt_ecommerce_transactions_2m.parquet`, then load to Delta table.
