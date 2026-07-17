from __future__ import annotations

import math
import os
import re
import sqlite3
import textwrap
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
from bs4 import BeautifulSoup
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "work"
OUT_DIR = ROOT / "outputs"
SOURCE_URL = "https://za.leatt.com"
PRODUCTS_URL = f"{SOURCE_URL}/products.json"
ABOUT_URL = f"{SOURCE_URL}/pages/about-us"
RNG_SEED = 42
ROW_COUNT = int(os.environ.get("LEATT_ROWS", "2000000"))
CHUNK_SIZE = int(os.environ.get("LEATT_CHUNK_SIZE", "250000"))


def money(value: float) -> str:
    return f"R{value:,.0f}"


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    soup = BeautifulSoup(value, "html.parser")
    return re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()


def classify_category(title: str, product_type: str, tags: str) -> str:
    haystack = f"{title} {product_type} {tags}".lower()
    checks = [
        ("Helmet", ["helmet"]),
        ("Body Protection", ["protector", "protection", "guard", "brace", "vest", "chest"]),
        ("Goggles", ["goggle", "lens"]),
        ("Footwear", ["shoe", "boot", "footwear", "sock"]),
        ("Gloves", ["glove"]),
        ("Apparel", ["jersey", "pant", "short", "jacket", "shirt", "hoodie", "jogger", "cap"]),
        ("Hydration", ["hydration", "drink", "water", "bladder"]),
        ("Bags", ["bag", "pack"]),
        ("Parts & Accessories", ["strap", "part", "accessory", "spare", "kit", "clip", "mount"]),
        ("Gift Card", ["gift card"]),
    ]
    for category, needles in checks:
        if any(needle in haystack for needle in needles):
            return category
    return "Other Gear"


def fetch_catalog() -> pd.DataFrame:
    rows: list[dict] = []
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 Codex BI Builder"})

    for page in range(1, 40):
        response = session.get(PRODUCTS_URL, params={"limit": 250, "page": page}, timeout=40)
        response.raise_for_status()
        products = response.json().get("products", [])
        if not products:
            break

        for product in products:
            product_tags = ", ".join(product.get("tags") or [])
            product_type = product.get("product_type") or ""
            category = classify_category(product.get("title", ""), product_type, product_tags)
            description = clean_text(product.get("body_html", ""))
            for variant in product.get("variants", []):
                price = float(variant.get("price") or 0)
                compare_at = variant.get("compare_at_price")
                compare_at_price = float(compare_at) if compare_at else np.nan
                rows.append(
                    {
                        "product_id": product.get("id"),
                        "variant_id": variant.get("id"),
                        "title": product.get("title"),
                        "variant_title": variant.get("title"),
                        "handle": product.get("handle"),
                        "vendor": product.get("vendor") or "Leatt",
                        "product_type": product_type,
                        "category": category,
                        "tags": product_tags,
                        "sku": variant.get("sku"),
                        "available": bool(variant.get("available", False)),
                        "price_zar": price,
                        "compare_at_price_zar": compare_at_price,
                        "grams": variant.get("grams"),
                        "created_at": product.get("created_at"),
                        "updated_at": product.get("updated_at"),
                        "source_url": f"{SOURCE_URL}/products/{product.get('handle')}",
                        "description": description[:500],
                    }
                )

    catalog = pd.DataFrame(rows)
    catalog = catalog[catalog["price_zar"].fillna(0) > 0].drop_duplicates("variant_id")
    catalog["price_zar"] = catalog["price_zar"].astype(float)
    catalog["compare_at_price_zar"] = pd.to_numeric(catalog["compare_at_price_zar"], errors="coerce")
    catalog["sale_flag"] = catalog["compare_at_price_zar"].fillna(0) > catalog["price_zar"]
    catalog["catalog_discount_pct"] = np.where(
        catalog["sale_flag"],
        1 - catalog["price_zar"] / catalog["compare_at_price_zar"].replace(0, np.nan),
        0,
    )
    catalog["catalog_discount_pct"] = catalog["catalog_discount_pct"].fillna(0).clip(0, 0.8)
    catalog = catalog.sort_values(["category", "title", "variant_title"]).reset_index(drop=True)
    return catalog


def fetch_about_text() -> str:
    try:
        response = requests.get(ABOUT_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
        start = text.lower().find("about us")
        return text[start : start + 2200] if start >= 0 else text[:2200]
    except Exception:
        return "Leatt ZA public ecommerce catalog was used as the product source."


def make_customers(n_customers: int, rng: np.random.Generator) -> pd.DataFrame:
    provinces = [
        ("Gauteng", "Johannesburg", 0.31),
        ("Western Cape", "Cape Town", 0.22),
        ("KwaZulu-Natal", "Durban", 0.15),
        ("Eastern Cape", "Gqeberha", 0.07),
        ("Free State", "Bloemfontein", 0.05),
        ("Limpopo", "Polokwane", 0.05),
        ("Mpumalanga", "Mbombela", 0.05),
        ("North West", "Rustenburg", 0.04),
        ("Northern Cape", "Kimberley", 0.02),
        ("International", "Windhoek", 0.04),
    ]
    province_names = [p[0] for p in provinces]
    city_map = {p[0]: p[1] for p in provinces}
    province_probs = np.array([p[2] for p in provinces])
    province_probs = province_probs / province_probs.sum()

    province = rng.choice(province_names, size=n_customers, p=province_probs)
    rider_types = rng.choice(["MTB", "Moto", "ADV", "Lifestyle"], size=n_customers, p=[0.38, 0.31, 0.18, 0.13])
    acquisition_channel = rng.choice(
        ["Organic Search", "Paid Search", "Paid Social", "Email", "Direct", "Retail Referral"],
        size=n_customers,
        p=[0.28, 0.19, 0.17, 0.14, 0.13, 0.09],
    )
    first_dates = pd.to_datetime("2021-01-01") + pd.to_timedelta(rng.integers(0, 1750, n_customers), unit="D")
    tiers = rng.choice(["Bronze", "Silver", "Gold", "Platinum"], size=n_customers, p=[0.56, 0.27, 0.13, 0.04])
    return pd.DataFrame(
        {
            "customer_id": np.arange(1, n_customers + 1, dtype=np.int32),
            "first_seen_date": first_dates,
            "province": province,
            "city": [city_map[p] for p in province],
            "rider_type": rider_types,
            "acquisition_channel": acquisition_channel,
            "loyalty_tier": tiers,
            "age_band": rng.choice(["18-24", "25-34", "35-44", "45-54", "55+"], size=n_customers, p=[0.12, 0.35, 0.28, 0.17, 0.08]),
            "email_opt_in": rng.choice([True, False], size=n_customers, p=[0.68, 0.32]),
        }
    )


def date_probabilities() -> tuple[pd.DatetimeIndex, np.ndarray]:
    dates = pd.date_range("2024-01-01", "2026-06-30", freq="D")
    month_factor = np.array([1.0 + 0.18 * math.sin((d.month - 1) / 12 * 2 * math.pi) for d in dates])
    weekend_factor = np.where(pd.Series(dates).dt.dayofweek.to_numpy() >= 5, 1.16, 1.0)
    payday_factor = np.where(np.isin(pd.Series(dates).dt.day.to_numpy(), [25, 26, 27, 28, 29, 30, 31, 1, 2]), 1.22, 1.0)
    holiday_factor = np.where(np.isin(pd.Series(dates).dt.month.to_numpy(), [11, 12]), 1.35, 1.0)
    p = month_factor * weekend_factor * payday_factor * holiday_factor
    return dates, p / p.sum()


def category_cost_factor(category: pd.Series) -> pd.Series:
    factors = {
        "Helmet": 0.55,
        "Body Protection": 0.52,
        "Goggles": 0.48,
        "Footwear": 0.58,
        "Gloves": 0.44,
        "Apparel": 0.46,
        "Hydration": 0.50,
        "Bags": 0.53,
        "Parts & Accessories": 0.42,
        "Gift Card": 0.98,
        "Other Gear": 0.50,
    }
    return category.map(factors).fillna(0.50)


def add_group(current: pd.DataFrame | None, update: pd.DataFrame, keys: list[str], sums: list[str]) -> pd.DataFrame:
    if current is None:
        return update
    combined = pd.concat([current, update], ignore_index=True)
    return combined.groupby(keys, as_index=False)[sums].sum()


def generate_transactions(catalog: pd.DataFrame, customers: pd.DataFrame) -> dict:
    rng = np.random.default_rng(RNG_SEED)
    parquet_path = OUT_DIR / "leatt_ecommerce_transactions_2m.parquet"
    sqlite_path = OUT_DIR / "leatt_ecommerce_warehouse.sqlite"
    if parquet_path.exists():
        parquet_path.unlink()
    if sqlite_path.exists():
        sqlite_path.unlink()

    variants = catalog.reset_index(drop=True).copy()
    variants["price_zar"] = variants["price_zar"].clip(lower=20)
    price = variants["price_zar"].to_numpy(float)
    category = variants["category"].astype(str).to_numpy()
    product_id = variants["product_id"].to_numpy()
    variant_id = variants["variant_id"].to_numpy()
    product_titles = variants["title"].astype(str).to_numpy()
    available = variants["available"].to_numpy(bool)

    category_weights = pd.Series(category).map(
        {
            "Helmet": 1.25,
            "Body Protection": 1.22,
            "Goggles": 1.12,
            "Footwear": 0.86,
            "Gloves": 1.08,
            "Apparel": 1.18,
            "Hydration": 0.76,
            "Bags": 0.63,
            "Parts & Accessories": 0.92,
            "Gift Card": 0.20,
            "Other Gear": 0.75,
        }
    ).fillna(0.75).to_numpy(float)
    product_weights = category_weights * (1 / np.sqrt(price)) * np.where(available, 1.0, 0.20) * rng.lognormal(0, 0.55, len(variants))
    product_weights = product_weights / product_weights.sum()

    dates, date_probs = date_probabilities()
    customer_weights = rng.gamma(shape=0.8, scale=1.0, size=len(customers))
    customer_weights = customer_weights / customer_weights.sum()
    customer_ids = customers["customer_id"].to_numpy()
    customer_province_map = customers.set_index("customer_id")["province"].to_dict()
    customer_city_map = customers.set_index("customer_id")["city"].to_dict()

    channels = np.array(["Organic Search", "Paid Search", "Paid Social", "Email", "Direct", "Marketplace"])
    channel_probs = np.array([0.25, 0.18, 0.18, 0.15, 0.17, 0.07])
    devices = np.array(["Mobile", "Desktop", "Tablet"])
    device_probs = np.array([0.69, 0.24, 0.07])
    payment_methods = np.array(["Card", "EFT", "Payflex", "Instant EFT", "Gift Card"])
    payment_probs = np.array([0.58, 0.16, 0.12, 0.10, 0.04])

    monthly = None
    category_kpi = None
    product_kpi = None
    province_kpi = None
    channel_kpi = None
    customer_before = None
    customer_after = None
    customer_all = None
    writer = None

    conn = sqlite3.connect(sqlite_path)
    conn.execute("PRAGMA journal_mode=OFF")
    conn.execute("PRAGMA synchronous=OFF")
    conn.execute("PRAGMA temp_store=MEMORY")

    catalog_sql = catalog.drop(columns=["description"]).copy()
    customers.to_sql("dim_customer", conn, if_exists="replace", index=False)
    catalog_sql.to_sql("dim_product_variant", conn, if_exists="replace", index=False)

    cutoff = pd.Timestamp("2026-03-31")
    start_row = 0
    while start_row < ROW_COUNT:
        n = min(CHUNK_SIZE, ROW_COUNT - start_row)
        row_ix = np.arange(start_row, start_row + n, dtype=np.int64)
        product_ix = rng.choice(len(variants), size=n, p=product_weights)
        sampled_price = price[product_ix]
        sampled_category = category[product_ix]
        sampled_customers = rng.choice(customer_ids, size=n, p=customer_weights)
        sampled_dates = dates[rng.choice(len(dates), size=n, p=date_probs)]
        sampled_channels = rng.choice(channels, size=n, p=channel_probs)
        sampled_devices = rng.choice(devices, size=n, p=device_probs)

        qty_lambda = np.where(sampled_price < 350, 1.45, np.where(sampled_price < 1200, 1.18, 1.04))
        quantity = np.maximum(1, rng.poisson(qty_lambda)).clip(1, 5).astype(np.int16)
        base_discount = rng.beta(1.6, 12, n) * 0.22
        campaign_boost = np.where(np.isin(pd.Series(sampled_dates).dt.month.to_numpy(), [11, 12]), rng.uniform(0.02, 0.18, n), 0)
        discount_pct = np.clip(base_discount + campaign_boost, 0, 0.45)
        unit_price = sampled_price
        gross_revenue = unit_price * quantity
        discount_amount = gross_revenue * discount_pct
        net_revenue = gross_revenue - discount_amount
        cost_factor = pd.Series(sampled_category).map(
            {
                "Helmet": 0.55,
                "Body Protection": 0.52,
                "Goggles": 0.48,
                "Footwear": 0.58,
                "Gloves": 0.44,
                "Apparel": 0.46,
                "Hydration": 0.50,
                "Bags": 0.53,
                "Parts & Accessories": 0.42,
                "Gift Card": 0.98,
                "Other Gear": 0.50,
            }
        ).fillna(0.50).to_numpy(float)
        estimated_unit_cost = unit_price * cost_factor * rng.normal(1, 0.035, n)
        gross_margin = net_revenue - (estimated_unit_cost * quantity)
        return_base = pd.Series(sampled_category).map(
            {
                "Footwear": 0.085,
                "Apparel": 0.075,
                "Helmet": 0.035,
                "Body Protection": 0.045,
                "Goggles": 0.030,
                "Gloves": 0.038,
            }
        ).fillna(0.025).to_numpy(float)
        return_flag = rng.random(n) < (return_base + np.where(discount_pct > 0.25, 0.01, 0))
        return_amount = np.where(return_flag, net_revenue * rng.uniform(0.65, 1.0, n), 0)
        fulfillment_days = np.maximum(1, rng.poisson(np.where(sampled_dates.weekday >= 5, 3.2, 2.4), n)).clip(1, 12)

        month = pd.Series(sampled_dates).dt.to_period("M").astype(str).to_numpy()
        province = [customer_province_map[int(c)] for c in sampled_customers]
        city = [customer_city_map[int(c)] for c in sampled_customers]
        campaigns = np.where(
            np.isin(pd.Series(sampled_dates).dt.month.to_numpy(), [11, 12]),
            "Peak Season",
            np.where(sampled_channels == "Email", "CRM Lifecycle", np.where(sampled_channels == "Paid Social", "Adventure Social", "Always On")),
        )

        df = pd.DataFrame(
            {
                "transaction_line_id": row_ix + 1,
                "order_id": 10_000_000 + (row_ix // 1.38).astype(np.int64),
                "order_date": sampled_dates,
                "month": month,
                "customer_id": sampled_customers.astype(np.int32),
                "product_id": product_id[product_ix],
                "variant_id": variant_id[product_ix],
                "product_title": product_titles[product_ix],
                "category": sampled_category,
                "channel": sampled_channels,
                "device": sampled_devices,
                "province": province,
                "city": city,
                "quantity": quantity,
                "unit_price_zar": np.round(unit_price, 2),
                "discount_pct": np.round(discount_pct, 4),
                "gross_revenue_zar": np.round(gross_revenue, 2),
                "discount_amount_zar": np.round(discount_amount, 2),
                "net_revenue_zar": np.round(net_revenue, 2),
                "estimated_unit_cost_zar": np.round(estimated_unit_cost, 2),
                "gross_margin_zar": np.round(gross_margin, 2),
                "return_flag": return_flag,
                "return_amount_zar": np.round(return_amount, 2),
                "fulfillment_days": fulfillment_days.astype(np.int16),
                "payment_method": rng.choice(payment_methods, size=n, p=payment_probs),
                "campaign": campaigns,
            }
        )

        table = pa.Table.from_pandas(df, preserve_index=False)
        if writer is None:
            writer = pq.ParquetWriter(parquet_path, table.schema, compression="snappy")
        writer.write_table(table)
        df.to_sql("fact_transaction_lines", conn, if_exists="append", index=False, chunksize=25000)

        sums = ["quantity", "gross_revenue_zar", "discount_amount_zar", "net_revenue_zar", "gross_margin_zar", "return_amount_zar"]
        monthly = add_group(monthly, df.groupby("month", as_index=False)[sums].sum(), ["month"], sums)
        category_kpi = add_group(category_kpi, df.groupby("category", as_index=False)[sums].sum(), ["category"], sums)
        product_kpi = add_group(product_kpi, df.groupby(["product_id", "variant_id", "product_title", "category"], as_index=False)[sums].sum(), ["product_id", "variant_id", "product_title", "category"], sums)
        province_kpi = add_group(province_kpi, df.groupby("province", as_index=False)[sums].sum(), ["province"], sums)
        channel_kpi = add_group(channel_kpi, df.groupby("channel", as_index=False)[sums].sum(), ["channel"], sums)

        all_customer_update = df.groupby("customer_id").agg(
            orders=("order_id", "nunique"),
            lines=("transaction_line_id", "count"),
            last_order_date=("order_date", "max"),
            quantity=("quantity", "sum"),
            net_revenue_zar=("net_revenue_zar", "sum"),
            gross_margin_zar=("gross_margin_zar", "sum"),
            return_amount_zar=("return_amount_zar", "sum"),
        ).reset_index()
        customer_all = pd.concat([customer_all, all_customer_update], ignore_index=True) if customer_all is not None else all_customer_update

        before_df = df[df["order_date"] <= cutoff]
        after_df = df[df["order_date"] > cutoff]
        if not before_df.empty:
            update = before_df.groupby("customer_id").agg(
                pre_orders=("order_id", "nunique"),
                pre_lines=("transaction_line_id", "count"),
                pre_last_order=("order_date", "max"),
                pre_quantity=("quantity", "sum"),
                pre_net_revenue=("net_revenue_zar", "sum"),
                pre_margin=("gross_margin_zar", "sum"),
                pre_return_amount=("return_amount_zar", "sum"),
            ).reset_index()
            customer_before = pd.concat([customer_before, update], ignore_index=True) if customer_before is not None else update
        if not after_df.empty:
            update = after_df.groupby("customer_id").agg(
                post_orders=("order_id", "nunique"),
                post_net_revenue=("net_revenue_zar", "sum"),
            ).reset_index()
            customer_after = pd.concat([customer_after, update], ignore_index=True) if customer_after is not None else update

        start_row += n
        print(f"Generated {start_row:,}/{ROW_COUNT:,} rows")

    if writer:
        writer.close()

    conn.execute("CREATE INDEX idx_fact_order_date ON fact_transaction_lines(order_date)")
    conn.execute("CREATE INDEX idx_fact_customer ON fact_transaction_lines(customer_id)")
    conn.execute("CREATE INDEX idx_fact_variant ON fact_transaction_lines(variant_id)")
    conn.commit()

    summaries = {
        "monthly": monthly.sort_values("month"),
        "category": category_kpi.sort_values("net_revenue_zar", ascending=False),
        "product": product_kpi.sort_values("net_revenue_zar", ascending=False),
        "province": province_kpi.sort_values("net_revenue_zar", ascending=False),
        "channel": channel_kpi.sort_values("net_revenue_zar", ascending=False),
    }
    for name, df_sum in summaries.items():
        df_sum.to_sql(f"agg_{name}", conn, if_exists="replace", index=False)

    customer_all = customer_all.groupby("customer_id").agg(
        orders=("orders", "sum"),
        lines=("lines", "sum"),
        last_order_date=("last_order_date", "max"),
        quantity=("quantity", "sum"),
        net_revenue_zar=("net_revenue_zar", "sum"),
        gross_margin_zar=("gross_margin_zar", "sum"),
        return_amount_zar=("return_amount_zar", "sum"),
    ).reset_index()
    customer_before = customer_before.groupby("customer_id").agg(
        pre_orders=("pre_orders", "sum"),
        pre_lines=("pre_lines", "sum"),
        pre_last_order=("pre_last_order", "max"),
        pre_quantity=("pre_quantity", "sum"),
        pre_net_revenue=("pre_net_revenue", "sum"),
        pre_margin=("pre_margin", "sum"),
        pre_return_amount=("pre_return_amount", "sum"),
    ).reset_index()
    customer_after = customer_after.groupby("customer_id").agg(post_orders=("post_orders", "sum"), post_net_revenue=("post_net_revenue", "sum")).reset_index()

    conn.close()
    return {
        "parquet_path": parquet_path,
        "sqlite_path": sqlite_path,
        "summaries": summaries,
        "customer_all": customer_all,
        "customer_before": customer_before,
        "customer_after": customer_after,
    }


def build_ml(customers: pd.DataFrame, generated: dict) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    before = generated["customer_before"].merge(generated["customer_after"], on="customer_id", how="left")
    before = before.merge(customers, on="customer_id", how="left")
    before["post_orders"] = before["post_orders"].fillna(0)
    before["post_net_revenue"] = before["post_net_revenue"].fillna(0)
    cutoff = pd.Timestamp("2026-03-31")
    before["recency_days"] = (cutoff - pd.to_datetime(before["pre_last_order"])).dt.days.clip(lower=0)
    before["avg_order_value_zar"] = before["pre_net_revenue"] / before["pre_orders"].replace(0, np.nan)
    before["return_rate"] = before["pre_return_amount"] / before["pre_net_revenue"].replace(0, np.nan)
    before["margin_rate"] = before["pre_margin"] / before["pre_net_revenue"].replace(0, np.nan)
    before = before.replace([np.inf, -np.inf], np.nan).fillna(0)
    before["target_repurchase_90d"] = (before["post_orders"] > 0).astype(int)

    features = [
        "pre_orders",
        "pre_lines",
        "pre_quantity",
        "pre_net_revenue",
        "pre_margin",
        "recency_days",
        "avg_order_value_zar",
        "return_rate",
        "margin_rate",
        "province",
        "rider_type",
        "loyalty_tier",
        "acquisition_channel",
        "age_band",
        "email_opt_in",
    ]
    X = before[features]
    y = before["target_repurchase_90d"]
    sample = before.sample(min(140000, len(before)), random_state=RNG_SEED)
    Xs = sample[features]
    ys = sample["target_repurchase_90d"]
    X_train, X_test, y_train, y_test = train_test_split(Xs, ys, test_size=0.25, random_state=RNG_SEED, stratify=ys)
    numeric = [
        "pre_orders",
        "pre_lines",
        "pre_quantity",
        "pre_net_revenue",
        "pre_margin",
        "recency_days",
        "avg_order_value_zar",
        "return_rate",
        "margin_rate",
    ]
    categorical = ["province", "rider_type", "loyalty_tier", "acquisition_channel", "age_band", "email_opt_in"]
    model = Pipeline(
        [
            (
                "prep",
                ColumnTransformer(
                    [
                        ("num", StandardScaler(), numeric),
                        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
                    ]
                ),
            ),
            ("clf", LogisticRegression(max_iter=700, class_weight="balanced")),
        ]
    )
    model.fit(X_train, y_train)
    test_score = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, test_score)
    accuracy = accuracy_score(y_test, test_score >= 0.5)

    before["repurchase_propensity"] = model.predict_proba(X)[:, 1]
    customer_all = generated["customer_all"].merge(customers, on="customer_id", how="left")
    customer_all = customer_all.merge(before[["customer_id", "repurchase_propensity"]], on="customer_id", how="left")
    customer_all["margin_rate"] = customer_all["gross_margin_zar"] / customer_all["net_revenue_zar"].replace(0, np.nan)
    customer_all["return_rate"] = customer_all["return_amount_zar"] / customer_all["net_revenue_zar"].replace(0, np.nan)
    customer_all["customer_value_score"] = (
        customer_all["net_revenue_zar"].rank(pct=True) * 0.45
        + customer_all["gross_margin_zar"].rank(pct=True) * 0.35
        + customer_all["repurchase_propensity"].fillna(0).rank(pct=True) * 0.20
    )
    customer_all["ml_segment"] = pd.cut(
        customer_all["customer_value_score"],
        bins=[-0.01, 0.50, 0.80, 0.95, 1.0],
        labels=["Nurture", "Grow", "Retain", "VIP"],
    )

    segment = customer_all.groupby("ml_segment", observed=False).agg(
        customers=("customer_id", "count"),
        orders=("orders", "sum"),
        net_revenue_zar=("net_revenue_zar", "sum"),
        gross_margin_zar=("gross_margin_zar", "sum"),
        avg_propensity=("repurchase_propensity", "mean"),
        avg_return_rate=("return_rate", "mean"),
    ).reset_index()

    metrics = {"repurchase_model_auc": auc, "repurchase_model_accuracy": accuracy, "training_customers": len(sample)}
    return customer_all, segment, metrics


def forecast_monthly(monthly: pd.DataFrame) -> pd.DataFrame:
    df = monthly.copy()
    df["date"] = pd.to_datetime(df["month"] + "-01")
    df["month_num"] = np.arange(len(df))
    df["calendar_month"] = df["date"].dt.month
    X = pd.get_dummies(df[["month_num", "calendar_month"]].astype({"calendar_month": str}), columns=["calendar_month"], drop_first=False)
    model = LinearRegression()
    model.fit(X, df["net_revenue_zar"])
    future_dates = pd.date_range(df["date"].max() + pd.offsets.MonthBegin(1), periods=6, freq="MS")
    future = pd.DataFrame({"date": future_dates, "month_num": np.arange(len(df), len(df) + len(future_dates)), "calendar_month": future_dates.month.astype(str)})
    X_future = pd.get_dummies(future[["month_num", "calendar_month"]], columns=["calendar_month"], drop_first=False)
    X_future = X_future.reindex(columns=X.columns, fill_value=0)
    future["forecast_net_revenue_zar"] = np.maximum(0, model.predict(X_future))
    future["forecast_month"] = future["date"].dt.to_period("M").astype(str)
    return future[["forecast_month", "forecast_net_revenue_zar"]]


def create_charts(monthly: pd.DataFrame, category: pd.DataFrame, segment: pd.DataFrame, forecast: pd.DataFrame) -> dict[str, Path]:
    chart_paths = {}
    plt.style.use("seaborn-v0_8-whitegrid")

    monthly_plot = monthly.copy()
    monthly_plot["date"] = pd.to_datetime(monthly_plot["month"] + "-01")
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(monthly_plot["date"], monthly_plot["net_revenue_zar"] / 1_000_000, color="#d71920", linewidth=2.4)
    ax.set_title("Monthly Net Revenue")
    ax.set_ylabel("R millions")
    ax.set_xlabel("")
    fig.autofmt_xdate()
    path = WORK_DIR / "monthly_revenue.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    chart_paths["monthly"] = path

    top_cat = category.head(8).sort_values("net_revenue_zar")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(top_cat["category"], top_cat["net_revenue_zar"] / 1_000_000, color="#111111")
    ax.set_title("Revenue by Category")
    ax.set_xlabel("R millions")
    path = WORK_DIR / "category_revenue.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    chart_paths["category"] = path

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(segment["ml_segment"].astype(str), segment["net_revenue_zar"] / 1_000_000, color="#4c78a8")
    ax.set_title("Revenue by ML Customer Segment")
    ax.set_ylabel("R millions")
    path = WORK_DIR / "segments.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    chart_paths["segments"] = path

    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.plot(forecast["forecast_month"], forecast["forecast_net_revenue_zar"] / 1_000_000, marker="o", color="#f58518")
    ax.set_title("Six Month Revenue Forecast")
    ax.set_ylabel("R millions")
    ax.tick_params(axis="x", rotation=35)
    path = WORK_DIR / "forecast.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    chart_paths["forecast"] = path
    return chart_paths


def write_excel(
    catalog: pd.DataFrame,
    generated: dict,
    customer_scores: pd.DataFrame,
    segments: pd.DataFrame,
    ml_metrics: dict,
    forecast: pd.DataFrame,
) -> Path:
    path = OUT_DIR / "leatt_ecommerce_bi_ml_report.xlsx"
    summaries = generated["summaries"]
    monthly = summaries["monthly"].copy()
    category = summaries["category"].copy()
    product = summaries["product"].copy()
    province = summaries["province"].copy()
    channel = summaries["channel"].copy()
    for df in [monthly, category, product, province, channel, segments]:
        if "net_revenue_zar" in df:
            df["margin_rate"] = df["gross_margin_zar"] / df["net_revenue_zar"].replace(0, np.nan)
            if "return_amount_zar" in df.columns:
                df["return_rate"] = df["return_amount_zar"] / df["net_revenue_zar"].replace(0, np.nan)

    total_revenue = monthly["net_revenue_zar"].sum()
    total_margin = monthly["gross_margin_zar"].sum()
    total_units = monthly["quantity"].sum()
    total_returns = monthly["return_amount_zar"].sum()
    kpis = pd.DataFrame(
        {
            "KPI": [
                "Transaction lines generated",
                "Net revenue",
                "Gross margin",
                "Gross margin rate",
                "Units sold",
                "Return value rate",
                "Catalog variants extracted",
                "Repurchase model AUC",
                "Repurchase model accuracy",
            ],
            "Value": [
                f"{ROW_COUNT:,}",
                money(total_revenue),
                money(total_margin),
                f"{total_margin / total_revenue:.1%}",
                f"{total_units:,.0f}",
                f"{total_returns / total_revenue:.1%}",
                f"{len(catalog):,}",
                f"{ml_metrics['repurchase_model_auc']:.3f}",
                f"{ml_metrics['repurchase_model_accuracy']:.3f}",
            ],
        }
    )

    data_dictionary = pd.DataFrame(
        [
            ("dim_product_variant", "Leatt ZA product and variant attributes extracted from public Shopify JSON."),
            ("dim_customer", "Synthetic ecommerce customers with geography, rider type, loyalty, and acquisition attributes."),
            ("fact_transaction_lines", "Generated transactional line-item fact table at million-row scale."),
            ("agg_monthly/category/product/province/channel", "Prepared BI aggregation tables for fast reporting."),
            ("customer_scores", "RFM and ML scores for repurchase propensity and value segmentation."),
            ("forecast", "Six month revenue forecast built from monthly trend and seasonality."),
        ],
        columns=["Table", "Purpose"],
    )

    fabric_plan = pd.DataFrame(
        [
            ("Bronze", "Land raw product JSON and parquet transactions in OneLake/Lakehouse Files."),
            ("Silver", "Create Delta tables for product, customer, and transaction facts with data quality checks."),
            ("Gold", "Publish star schema semantic model: Date, Product, Customer, Channel, Geography, Fact Sales."),
            ("ML", "Train and register repurchase propensity and demand forecast models in Fabric Data Science."),
            ("BI", "Build Power BI report pages for executive overview, category, customer, operations, forecast, and model monitoring."),
            ("Ops", "Schedule Data Factory pipelines and monitor capacity with the Fabric Capacity Metrics app."),
        ],
        columns=["Layer", "Action"],
    )

    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        kpis.to_excel(writer, sheet_name="Executive Summary", index=False, startrow=2)
        monthly.to_excel(writer, sheet_name="Monthly Trend", index=False)
        category.to_excel(writer, sheet_name="Category KPI", index=False)
        product.head(5000).to_excel(writer, sheet_name="Product KPI", index=False)
        province.to_excel(writer, sheet_name="Province KPI", index=False)
        channel.to_excel(writer, sheet_name="Channel KPI", index=False)
        segments.to_excel(writer, sheet_name="ML Segments", index=False)
        customer_scores.sort_values("customer_value_score", ascending=False).head(25000).to_excel(writer, sheet_name="Customer Scores Sample", index=False)
        forecast.to_excel(writer, sheet_name="Forecast", index=False)
        catalog.head(25000).to_excel(writer, sheet_name="Catalog", index=False)
        data_dictionary.to_excel(writer, sheet_name="Data Dictionary", index=False)
        fabric_plan.to_excel(writer, sheet_name="Fabric Plan", index=False)

        workbook = writer.book
        header_fmt = workbook.add_format({"bold": True, "font_color": "white", "bg_color": "#111111", "border": 1})
        money_fmt = workbook.add_format({"num_format": "R#,##0"})
        pct_fmt = workbook.add_format({"num_format": "0.0%"})
        title_fmt = workbook.add_format({"bold": True, "font_size": 18, "font_color": "#d71920"})
        small_fmt = workbook.add_format({"font_color": "#555555"})

        for sheet_name, ws in writer.sheets.items():
            ws.freeze_panes(1, 0)
            ws.set_row(0, None, header_fmt)
            ws.set_column(0, 0, 22)
            ws.set_column(1, 12, 18)
        ws = writer.sheets["Executive Summary"]
        ws.write(0, 0, "Leatt ZA Ecommerce BI and ML Report", title_fmt)
        ws.write(1, 0, "Generated from public catalog data plus synthetic million-row ecommerce transactions.", small_fmt)
        ws.set_column(0, 0, 32)
        ws.set_column(1, 1, 24)

        ws = writer.sheets["Monthly Trend"]
        month_rows = len(monthly) + 1
        chart = workbook.add_chart({"type": "line"})
        chart.add_series({"name": "Net Revenue", "categories": ["Monthly Trend", 1, 0, month_rows - 1, 0], "values": ["Monthly Trend", 1, 4, month_rows - 1, 4], "line": {"color": "#d71920", "width": 2.25}})
        chart.set_title({"name": "Monthly Net Revenue"})
        chart.set_y_axis({"num_format": "R#,##0"})
        ws.insert_chart("I2", chart, {"x_scale": 1.45, "y_scale": 1.25})

        ws = writer.sheets["Category KPI"]
        cat_rows = len(category) + 1
        chart = workbook.add_chart({"type": "bar"})
        chart.add_series({"name": "Net Revenue", "categories": ["Category KPI", 1, 0, min(cat_rows - 1, 9), 0], "values": ["Category KPI", 1, 4, min(cat_rows - 1, 9), 4], "fill": {"color": "#111111"}})
        chart.set_title({"name": "Top Categories"})
        chart.set_x_axis({"num_format": "R#,##0"})
        ws.insert_chart("J2", chart, {"x_scale": 1.35, "y_scale": 1.25})

        ws = writer.sheets["ML Segments"]
        seg_rows = len(segments) + 1
        chart = workbook.add_chart({"type": "column"})
        chart.add_series({"name": "Revenue", "categories": ["ML Segments", 1, 0, seg_rows - 1, 0], "values": ["ML Segments", 1, 3, seg_rows - 1, 3], "fill": {"color": "#4c78a8"}})
        chart.set_title({"name": "Revenue by ML Segment"})
        chart.set_y_axis({"num_format": "R#,##0"})
        ws.insert_chart("I2", chart, {"x_scale": 1.25, "y_scale": 1.15})

        for sheet_name in ["Monthly Trend", "Category KPI", "Product KPI", "Province KPI", "Channel KPI", "ML Segments", "Forecast"]:
            ws = writer.sheets[sheet_name]
            ws.set_column(2, 8, 18, money_fmt)
            ws.set_column(8, 12, 14, pct_fmt)

    return path


def write_pdf(
    catalog: pd.DataFrame,
    generated: dict,
    segments: pd.DataFrame,
    ml_metrics: dict,
    forecast: pd.DataFrame,
    about_text: str,
    chart_paths: dict[str, Path],
) -> Path:
    path = OUT_DIR / "leatt_ecommerce_bi_ml_ebook.pdf"
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CenterTitle", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#d71920")))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10, textColor=colors.HexColor("#555555")))
    story = []
    monthly = generated["summaries"]["monthly"]
    category = generated["summaries"]["category"]
    product = generated["summaries"]["product"]
    province = generated["summaries"]["province"]
    total_revenue = monthly["net_revenue_zar"].sum()
    total_margin = monthly["gross_margin_zar"].sum()
    total_returns = monthly["return_amount_zar"].sum()
    top_category = category.iloc[0]
    top_product = product.iloc[0]
    top_province = province.iloc[0]
    latest_month = monthly.iloc[-1]
    first_month = monthly.iloc[0]
    growth = latest_month["net_revenue_zar"] / first_month["net_revenue_zar"] - 1

    story.append(Paragraph("Leatt ZA Ecommerce BI and ML Ebook", styles["CenterTitle"]))
    story.append(Paragraph("Catalog extraction, synthetic ecommerce data, KPI modelling, ML segmentation, forecasting, and Microsoft Fabric implementation plan.", styles["BodyText"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(
        Table(
            [
                ["Metric", "Value"],
                ["Transaction lines", f"{ROW_COUNT:,}"],
                ["Catalog variants extracted", f"{len(catalog):,}"],
                ["Net revenue", money(total_revenue)],
                ["Gross margin rate", f"{total_margin / total_revenue:.1%}"],
                ["Return value rate", f"{total_returns / total_revenue:.1%}"],
                ["Repurchase model AUC", f"{ml_metrics['repurchase_model_auc']:.3f}"],
            ],
            hAlign="LEFT",
            style=[
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("Executive Insights", styles["Heading1"]))
    insights = [
        f"{top_category['category']} is the largest simulated revenue category at {money(top_category['net_revenue_zar'])}. It should anchor homepage merchandising, paid search, and bundle strategy.",
        f"The strongest product variant by revenue is {top_product['product_title']} at {money(top_product['net_revenue_zar'])}. Use it as a hero SKU and cross-sell relevant accessories.",
        f"{top_province['province']} is the top market at {money(top_province['net_revenue_zar'])}. Regional budget allocation should follow demand density while protecting margin.",
        f"Revenue changed {growth:.1%} from {first_month['month']} to {latest_month['month']} in the generated trading history, with peak season uplift visible in November and December.",
        f"The ML segmentation separates customers into VIP, Retain, Grow, and Nurture groups. VIP and Retain audiences should receive early access, replacement-cycle campaigns, and product education.",
    ]
    for item in insights:
        story.append(Paragraph(item, styles["BodyText"]))
        story.append(Spacer(1, 0.18 * cm))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Image(str(chart_paths["monthly"]), width=16 * cm, height=8 * cm))
    story.append(PageBreak())

    story.append(Paragraph("Catalog Source", styles["Heading1"]))
    story.append(Paragraph("Public product and variant data was extracted from Leatt ZA's Shopify-style product JSON endpoint, then normalized into a product variant dimension.", styles["BodyText"]))
    story.append(Paragraph(about_text[:1300], styles["Small"]))
    top_catalog = catalog.groupby("category").agg(variants=("variant_id", "count"), avg_price_zar=("price_zar", "mean")).reset_index().sort_values("variants", ascending=False)
    table_rows = [["Category", "Variants", "Avg price"]] + [[r["category"], f"{int(r['variants']):,}", money(r["avg_price_zar"])] for _, r in top_catalog.head(10).iterrows()]
    story.append(Table(table_rows, hAlign="LEFT", style=[("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")), ("PADDING", (0, 0), (-1, -1), 5)]))
    story.append(PageBreak())

    story.append(Paragraph("Category and Product Performance", styles["Heading1"]))
    story.append(Image(str(chart_paths["category"]), width=15 * cm, height=8.4 * cm))
    product_rows = [["Product", "Category", "Revenue", "Margin"]] + [
        [r["product_title"][:42], r["category"], money(r["net_revenue_zar"]), money(r["gross_margin_zar"])] for _, r in product.head(10).iterrows()
    ]
    story.append(Table(product_rows, hAlign="LEFT", colWidths=[7 * cm, 3.2 * cm, 3 * cm, 3 * cm], style=[("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")), ("PADDING", (0, 0), (-1, -1), 4), ("FONTSIZE", (0, 0), (-1, -1), 7)]))
    story.append(PageBreak())

    story.append(Paragraph("ML Customer Segmentation", styles["Heading1"]))
    story.append(Paragraph(f"The repurchase propensity model was trained on {ml_metrics['training_customers']:,} customer examples using recency, frequency, monetary value, margin, returns, geography, rider type, loyalty tier, and acquisition channel. Test AUC: {ml_metrics['repurchase_model_auc']:.3f}.", styles["BodyText"]))
    story.append(Image(str(chart_paths["segments"]), width=15 * cm, height=8.4 * cm))
    seg_rows = [["Segment", "Customers", "Revenue", "Avg propensity"]] + [
        [str(r["ml_segment"]), f"{int(r['customers']):,}", money(r["net_revenue_zar"]), f"{r['avg_propensity']:.1%}"] for _, r in segments.iterrows()
    ]
    story.append(Table(seg_rows, hAlign="LEFT", style=[("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")), ("PADDING", (0, 0), (-1, -1), 5)]))
    story.append(PageBreak())

    story.append(Paragraph("Forecast and Action Plan", styles["Heading1"]))
    story.append(Image(str(chart_paths["forecast"]), width=15 * cm, height=7.8 * cm))
    forecast_rows = [["Month", "Forecast revenue"]] + [[r["forecast_month"], money(r["forecast_net_revenue_zar"])] for _, r in forecast.iterrows()]
    story.append(Table(forecast_rows, hAlign="LEFT", style=[("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")), ("PADDING", (0, 0), (-1, -1), 5)]))
    story.append(Spacer(1, 0.35 * cm))
    actions = [
        "Prioritize high-margin protection, helmet, and accessory bundles by rider type.",
        "Build abandon-cart and replenishment journeys around accessories, gloves, goggles, and hydration add-ons.",
        "Use VIP and Retain ML segments for early product drops, service reminders, and premium support.",
        "Monitor return rate by category and province to find sizing, delivery, or expectation gaps.",
        "Publish a Fabric semantic model so Power BI can serve executive, category, customer, operations, and ML monitoring pages.",
    ]
    for item in actions:
        story.append(Paragraph(item, styles["BodyText"]))
    story.append(PageBreak())

    story.append(Paragraph("Microsoft Fabric Blueprint", styles["Heading1"]))
    blueprint = [
        ["Fabric area", "Recommended use"],
        ["Data Factory", "Ingest Leatt product JSON, ad data, GA4 exports, payment/order extracts, and support data."],
        ["Lakehouse / OneLake", "Store bronze raw files, silver Delta tables, and gold star schema tables."],
        ["Data Warehouse", "Serve governed SQL models for finance and operations users."],
        ["Data Science", "Train repurchase propensity, demand forecast, next-best-category, and return-risk models."],
        ["Power BI", "Publish executive KPI, category, customer, operations, forecast, and ML monitoring report pages."],
        ["Capacity Metrics", "Track CU consumption and decide when to pause, resume, or scale Fabric capacity."],
    ]
    story.append(Table(blueprint, hAlign="LEFT", colWidths=[4 * cm, 12 * cm], style=[("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")), ("PADDING", (0, 0), (-1, -1), 5), ("VALIGN", (0, 0), (-1, -1), "TOP")]))

    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=1.6 * cm, leftMargin=1.6 * cm, topMargin=1.4 * cm, bottomMargin=1.4 * cm)
    doc.build(story)
    return path


def write_markdown_and_dax(generated: dict, ml_metrics: dict, forecast: pd.DataFrame) -> tuple[Path, Path]:
    guide_path = OUT_DIR / "fabric_powerbi_implementation_guide.md"
    dax_path = OUT_DIR / "powerbi_dax_measures.dax"
    monthly = generated["summaries"]["monthly"]
    guide = f"""# Leatt ZA Fabric and Power BI Implementation Guide

## Is Fabric in Azure?

Yes. Microsoft Fabric can be bought as Azure F SKU capacity from the Azure portal. The practical deployment path is:

1. Azure portal > search for Microsoft Fabric.
2. Create Fabric Capacity.
3. Choose subscription, resource group, region, size, and capacity admin.
4. Create a Fabric workspace and assign it to the capacity.
5. Load this package into a Lakehouse or Warehouse and publish a Power BI semantic model.

## Delivered local package

- Product catalog source: `{PRODUCTS_URL}`
- Transaction fact rows generated: `{ROW_COUNT:,}`
- Revenue period: `{monthly['month'].min()}` to `{monthly['month'].max()}`
- Repurchase model AUC: `{ml_metrics['repurchase_model_auc']:.3f}`
- Six month forecast file sheet: `Forecast`

## Fabric architecture

Bronze: raw product JSON, raw generated parquet, raw customer/order extracts.

Silver: cleaned Delta tables for products, customers, transaction lines, dates, channels, and geography.

Gold: star schema semantic tables with business-friendly names, certified metrics, and row-level security if needed.

ML: customer repurchase propensity, value segmentation, six-month revenue forecast, return-risk model, and next-best-category recommendations.

Power BI report pages:

1. Executive overview: revenue, margin, return rate, units, customer count, forecast.
2. Category performance: revenue, gross margin, return rate, ASP, discount depth.
3. Product drilldown: top products, sales mix, margin leakage, inventory/proxy demand.
4. Customer intelligence: RFM, ML segment, province, rider type, cohort, propensity.
5. Operations: fulfillment days, return value, payment mix, regional pressure.
6. ML monitor: AUC, score distribution, segment movement, forecast vs actual.

## Recommended next data sources

- Shopify orders and customers
- GA4 traffic and conversion paths
- Google Ads / Meta Ads spend
- Payment provider settlements
- Inventory and stock availability
- Returns/refunds reason codes
- Email/SMS campaign engagement

## Immediate business plays

- Build protection and helmet bundles for high-intent MTB/Moto buyers.
- Use accessories as margin-positive attach items.
- Run VIP early access campaigns before peak season.
- Create province-specific delivery and returns monitoring.
- Retarget high-propensity customers with rider-type-specific landing pages.
"""
    dax = """-- Core Power BI measures for the Leatt ecommerce semantic model

Net Revenue = SUM('Fact Transaction Lines'[net_revenue_zar])

Gross Revenue = SUM('Fact Transaction Lines'[gross_revenue_zar])

Gross Margin = SUM('Fact Transaction Lines'[gross_margin_zar])

Gross Margin % = DIVIDE([Gross Margin], [Net Revenue])

Units Sold = SUM('Fact Transaction Lines'[quantity])

Discount Amount = SUM('Fact Transaction Lines'[discount_amount_zar])

Discount % = DIVIDE([Discount Amount], [Gross Revenue])

Return Value = SUM('Fact Transaction Lines'[return_amount_zar])

Return Value % = DIVIDE([Return Value], [Net Revenue])

Orders = DISTINCTCOUNT('Fact Transaction Lines'[order_id])

Customers = DISTINCTCOUNT('Fact Transaction Lines'[customer_id])

Average Order Value = DIVIDE([Net Revenue], [Orders])

Average Selling Price = DIVIDE([Net Revenue], [Units Sold])

Revenue YoY % =
VAR CurrentRevenue = [Net Revenue]
VAR PriorRevenue = CALCULATE([Net Revenue], SAMEPERIODLASTYEAR('Dim Date'[Date]))
RETURN DIVIDE(CurrentRevenue - PriorRevenue, PriorRevenue)

High Propensity Customers =
CALCULATE(
    DISTINCTCOUNT('Customer Scores'[customer_id]),
    'Customer Scores'[repurchase_propensity] >= 0.70
)

VIP Revenue =
CALCULATE(
    [Net Revenue],
    'Customer Scores'[ml_segment] = "VIP"
)
"""
    guide_path.write_text(guide, encoding="utf-8")
    dax_path.write_text(dax, encoding="utf-8")
    return guide_path, dax_path


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching Leatt catalog...")
    catalog = fetch_catalog()
    if catalog.empty:
        raise RuntimeError("No catalog products were extracted.")
    catalog_path = OUT_DIR / "leatt_product_catalog.csv"
    catalog.to_csv(catalog_path, index=False)
    about_text = fetch_about_text()

    print(f"Catalog variants extracted: {len(catalog):,}")
    rng = np.random.default_rng(RNG_SEED)
    customers = make_customers(max(180000, ROW_COUNT // 12), rng)
    customer_path = OUT_DIR / "leatt_synthetic_customers.csv"
    customers.to_csv(customer_path, index=False)

    generated = generate_transactions(catalog, customers)
    customer_scores, segments, ml_metrics = build_ml(customers, generated)
    forecast = forecast_monthly(generated["summaries"]["monthly"])
    chart_paths = create_charts(generated["summaries"]["monthly"], generated["summaries"]["category"], segments, forecast)

    scores_path = OUT_DIR / "leatt_customer_ml_scores.csv"
    customer_scores.to_csv(scores_path, index=False)
    forecast_path = OUT_DIR / "leatt_revenue_forecast.csv"
    forecast.to_csv(forecast_path, index=False)
    excel_path = write_excel(catalog, generated, customer_scores, segments, ml_metrics, forecast)
    pdf_path = write_pdf(catalog, generated, segments, ml_metrics, forecast, about_text, chart_paths)
    guide_path, dax_path = write_markdown_and_dax(generated, ml_metrics, forecast)

    manifest = pd.DataFrame(
        [
            ("Product catalog", catalog_path.name, f"{len(catalog):,} variants extracted from {PRODUCTS_URL}"),
            ("Synthetic customers", customer_path.name, f"{len(customers):,} customers"),
            ("Transactional parquet", generated["parquet_path"].name, f"{ROW_COUNT:,} transaction lines"),
            ("SQLite warehouse", generated["sqlite_path"].name, "dimensional tables, fact table, and aggregations"),
            ("Excel BI/ML report", excel_path.name, "summary workbook with charts and model outputs"),
            ("PDF ebook", pdf_path.name, "executive BI and ML narrative report"),
            ("Customer ML scores", scores_path.name, "customer-level value and propensity scores"),
            ("Revenue forecast", forecast_path.name, "six-month forecast"),
            ("Fabric guide", guide_path.name, "Azure Fabric and Power BI implementation guide"),
            ("DAX measures", dax_path.name, "starter Power BI semantic model measures"),
        ],
        columns=["Asset", "File", "Description"],
    )
    manifest_path = OUT_DIR / "asset_manifest.csv"
    manifest.to_csv(manifest_path, index=False)

    print("\nDONE")
    print(f"Output directory: {OUT_DIR}")
    for file_path in [catalog_path, customer_path, generated["parquet_path"], generated["sqlite_path"], excel_path, pdf_path, scores_path, forecast_path, guide_path, dax_path, manifest_path]:
        print(f"- {file_path.name}: {file_path.stat().st_size / (1024 * 1024):,.2f} MB")


if __name__ == "__main__":
    main()
