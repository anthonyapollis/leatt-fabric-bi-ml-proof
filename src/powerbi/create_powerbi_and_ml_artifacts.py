from __future__ import annotations

import base64
import json
import shutil
import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image as PdfImage
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
REPO = OUT / "leatt-fabric-bi-ml-git-proof"
SQLITE = OUT / "leatt_ecommerce_warehouse.sqlite"
SCREENSHOTS = OUT / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)
WORKSPACE_ID = "e515bafe-7290-4832-ae1d-514be43a9d87"
WORKSPACE_NAME = "Apollis"
DATASET_NAME = f"Leatt Fabric BI ML Semantic Model {datetime.now():%Y%m%d%H%M}"


def az_token(resource: str) -> str:
    az = shutil.which("az") or shutil.which("az.cmd") or r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    return subprocess.check_output([az, "account", "get-access-token", "--resource", resource, "--query", "accessToken", "-o", "tsv"], text=True).strip()


def powerbi_request(method: str, url: str, **kwargs) -> requests.Response:
    token = az_token("https://analysis.windows.net/powerbi/api")
    headers = kwargs.pop("headers", {})
    headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    last_response = None
    for attempt in range(4):
        response = requests.request(method, url, headers=headers, timeout=120, **kwargs)
        last_response = response
        if response.ok:
            return response
        if response.status_code >= 500:
            time.sleep(5 * (attempt + 1))
            continue
        break
    raise RuntimeError(f"{method} {url} failed: {last_response.status_code} {last_response.text}")


def load_data() -> dict[str, pd.DataFrame]:
    conn = sqlite3.connect(SQLITE)
    data = {
        "monthly": pd.read_sql("select * from agg_monthly order by month", conn),
        "category": pd.read_sql("select * from agg_category order by net_revenue_zar desc", conn),
        "channel": pd.read_sql("select * from agg_channel order by net_revenue_zar desc", conn),
        "province": pd.read_sql("select * from agg_province order by net_revenue_zar desc", conn),
        "product": pd.read_sql("select * from agg_product order by net_revenue_zar desc limit 50", conn),
        "sample": pd.read_sql(
            """
            select transaction_line_id, order_id, order_date, month, customer_id, product_title,
                   category, channel, device, province, quantity, unit_price_zar, discount_pct,
                   net_revenue_zar, gross_margin_zar, return_flag, return_amount_zar,
                   fulfillment_days, payment_method, campaign
            from fact_transaction_lines
            order by transaction_line_id
            limit 300000
            """,
            conn,
        ),
    }
    counts = {
        "fact_rows": conn.execute("select count(*) from fact_transaction_lines").fetchone()[0],
        "customers": conn.execute("select count(*) from dim_customer").fetchone()[0],
        "variants": conn.execute("select count(*) from dim_product_variant").fetchone()[0],
    }
    conn.close()
    data["counts"] = pd.DataFrame([counts])
    return data


def train_return_risk(data: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    df = data["sample"].copy()
    df["return_flag"] = df["return_flag"].astype(int)
    df["margin_rate"] = df["gross_margin_zar"] / df["net_revenue_zar"].replace(0, np.nan)
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
    features = ["category", "channel", "device", "province", "payment_method", "campaign", "quantity", "unit_price_zar", "discount_pct", "net_revenue_zar", "margin_rate", "fulfillment_days"]
    numeric = ["quantity", "unit_price_zar", "discount_pct", "net_revenue_zar", "margin_rate", "fulfillment_days"]
    categorical = ["category", "channel", "device", "province", "payment_method", "campaign"]
    model_df = df.sample(min(120000, len(df)), random_state=123)
    X = model_df[features]
    y = model_df["return_flag"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=123, stratify=y)
    model = Pipeline(
        [
            ("prep", ColumnTransformer([("num", StandardScaler(), numeric), ("cat", OneHotEncoder(handle_unknown="ignore"), categorical)])),
            ("clf", LogisticRegression(max_iter=700, class_weight="balanced")),
        ]
    )
    model.fit(X_train, y_train)
    score = model.predict_proba(X_test)[:, 1]
    pred = (score >= 0.5).astype(int)
    metrics = {
        "model_name": "Return Risk Logistic Regression",
        "training_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "auc": float(roc_auc_score(y_test, score)),
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }
    scored = df.sample(min(50000, len(df)), random_state=321).copy()
    scored["return_risk_score"] = model.predict_proba(scored[features])[:, 1]
    scored["risk_band"] = pd.cut(scored["return_risk_score"], bins=[-0.01, 0.25, 0.50, 0.75, 1.0], labels=["Low", "Medium", "High", "Critical"])
    scored_out = scored[
        [
            "transaction_line_id",
            "order_id",
            "customer_id",
            "product_title",
            "category",
            "channel",
            "province",
            "net_revenue_zar",
            "return_flag",
            "return_risk_score",
            "risk_band",
        ]
    ].sort_values("return_risk_score", ascending=False)
    segment = scored_out.groupby(["risk_band", "category"], observed=False).agg(
        lines=("transaction_line_id", "count"),
        avg_risk=("return_risk_score", "mean"),
        net_revenue_zar=("net_revenue_zar", "sum"),
        actual_return_rate=("return_flag", "mean"),
    ).reset_index().sort_values(["risk_band", "avg_risk"], ascending=[False, False])
    return scored_out, segment, metrics


def prepare_powerbi_tables(data: dict[str, pd.DataFrame], ml_segment: pd.DataFrame, metrics: dict) -> dict[str, pd.DataFrame]:
    monthly = data["monthly"].copy()
    monthly["margin_rate"] = monthly["gross_margin_zar"] / monthly["net_revenue_zar"].replace(0, np.nan)
    monthly["return_rate"] = monthly["return_amount_zar"] / monthly["net_revenue_zar"].replace(0, np.nan)

    category = data["category"].head(20).copy()
    category["margin_rate"] = category["gross_margin_zar"] / category["net_revenue_zar"].replace(0, np.nan)
    category["return_rate"] = category["return_amount_zar"] / category["net_revenue_zar"].replace(0, np.nan)

    channel = data["channel"].copy()
    spend_rate = {"Organic Search": 0.035, "Paid Search": 0.145, "Paid Social": 0.170, "Email": 0.018, "Direct": 0.010, "Marketplace": 0.115}
    channel["estimated_spend_zar"] = channel.apply(lambda r: r["net_revenue_zar"] * spend_rate.get(r["channel"], 0.08), axis=1)
    channel["roas"] = channel["net_revenue_zar"] / channel["estimated_spend_zar"].replace(0, np.nan)

    counts = data["counts"].iloc[0]
    total_revenue = monthly["net_revenue_zar"].sum()
    total_margin = monthly["gross_margin_zar"].sum()
    kpis = pd.DataFrame(
        [
            ("Fact Rows In Fabric OneLake", float(counts["fact_rows"]), f"{int(counts['fact_rows']):,}"),
            ("Customers", float(counts["customers"]), f"{int(counts['customers']):,}"),
            ("Product Variants", float(counts["variants"]), f"{int(counts['variants']):,}"),
            ("Net Revenue", float(total_revenue), f"R{total_revenue:,.0f}"),
            ("Gross Margin", float(total_margin), f"R{total_margin:,.0f}"),
            ("Gross Margin Rate", float(total_margin / total_revenue), f"{total_margin / total_revenue:.1%}"),
            ("Return Risk AUC", float(metrics["auc"]), f"{metrics['auc']:.3f}"),
        ],
        columns=["metric", "value", "display_value"],
    )
    fabric = pd.DataFrame(
        [
            ("Workspace", "Apollis"),
            ("Capacity", "fabric-capacity-redacted / SKU redacted / Azure region redacted"),
            ("Lakehouse", "Leatt_BI_ML_Lakehouse"),
            ("Bronze Fact File", "Files/Bronze/leatt_ecommerce_transactions_2m.parquet"),
            ("Data Pipeline", "pipeline name redacted for public sharing"),
        ],
        columns=["item", "value"],
    )
    ml_metrics = pd.DataFrame([(k, str(v)) for k, v in metrics.items()], columns=["metric", "value"])
    return {
        "ExecutiveKPI": kpis,
        "MonthlyTrend": monthly[["month", "quantity", "net_revenue_zar", "gross_margin_zar", "return_amount_zar", "margin_rate", "return_rate"]],
        "CategoryKPI": category[["category", "quantity", "net_revenue_zar", "gross_margin_zar", "return_amount_zar", "margin_rate", "return_rate"]],
        "ChannelROI": channel[["channel", "quantity", "net_revenue_zar", "gross_margin_zar", "return_amount_zar", "estimated_spend_zar", "roas"]],
        "MLReturnRisk": ml_segment.head(80),
        "MLMetrics": ml_metrics,
        "FabricProof": fabric,
    }


def powerbi_schema() -> dict:
    return {
        "name": DATASET_NAME,
        "defaultMode": "Push",
        "tables": [
            {"name": "ExecutiveKPI", "columns": [{"name": "metric", "dataType": "string"}, {"name": "value", "dataType": "double"}, {"name": "display_value", "dataType": "string"}]},
            {"name": "MonthlyTrend", "columns": [{"name": "month", "dataType": "string"}, {"name": "quantity", "dataType": "double"}, {"name": "net_revenue_zar", "dataType": "double"}, {"name": "gross_margin_zar", "dataType": "double"}, {"name": "return_amount_zar", "dataType": "double"}, {"name": "margin_rate", "dataType": "double"}, {"name": "return_rate", "dataType": "double"}]},
            {"name": "CategoryKPI", "columns": [{"name": "category", "dataType": "string"}, {"name": "quantity", "dataType": "double"}, {"name": "net_revenue_zar", "dataType": "double"}, {"name": "gross_margin_zar", "dataType": "double"}, {"name": "return_amount_zar", "dataType": "double"}, {"name": "margin_rate", "dataType": "double"}, {"name": "return_rate", "dataType": "double"}]},
            {"name": "ChannelROI", "columns": [{"name": "channel", "dataType": "string"}, {"name": "quantity", "dataType": "double"}, {"name": "net_revenue_zar", "dataType": "double"}, {"name": "gross_margin_zar", "dataType": "double"}, {"name": "return_amount_zar", "dataType": "double"}, {"name": "estimated_spend_zar", "dataType": "double"}, {"name": "roas", "dataType": "double"}]},
            {"name": "MLReturnRisk", "columns": [{"name": "risk_band", "dataType": "string"}, {"name": "category", "dataType": "string"}, {"name": "lines", "dataType": "Int64"}, {"name": "avg_risk", "dataType": "double"}, {"name": "net_revenue_zar", "dataType": "double"}, {"name": "actual_return_rate", "dataType": "double"}]},
            {"name": "MLMetrics", "columns": [{"name": "metric", "dataType": "string"}, {"name": "value", "dataType": "string"}]},
            {"name": "FabricProof", "columns": [{"name": "item", "dataType": "string"}, {"name": "value", "dataType": "string"}]},
        ],
    }


def create_powerbi_dataset(tables: dict[str, pd.DataFrame]) -> dict:
    base = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}"
    existing = powerbi_request("GET", f"{base}/datasets").json().get("value", [])
    for ds in existing:
        if ds.get("name") == DATASET_NAME:
            powerbi_request("DELETE", f"{base}/datasets/{ds['id']}")
    created = powerbi_request("POST", f"{base}/datasets?defaultRetentionPolicy=basicFIFO", data=json.dumps(powerbi_schema())).json()
    dataset_id = created["id"]
    for table_name, df in tables.items():
        rows = json.loads(df.replace([np.inf, -np.inf], np.nan).where(pd.notna(df), None).to_json(orient="records"))
        powerbi_request("POST", f"{base}/datasets/{dataset_id}/tables/{table_name}/rows", data=json.dumps({"rows": rows}))
    return {"dataset_id": dataset_id, "dataset_name": DATASET_NAME, "workspace_id": WORKSPACE_ID, "workspace_name": WORKSPACE_NAME}


def create_screenshots(tables: dict[str, pd.DataFrame], metrics: dict, powerbi_info: dict) -> dict[str, Path]:
    paths = {}
    plt.style.use("seaborn-v0_8-whitegrid")
    kpi = tables["ExecutiveKPI"]
    monthly = tables["MonthlyTrend"].copy()
    category = tables["CategoryKPI"].head(8).sort_values("net_revenue_zar")
    channel = tables["ChannelROI"].sort_values("roas")
    ml = tables["MLReturnRisk"].copy()

    fig = plt.figure(figsize=(16, 9), facecolor="#f6f7f9")
    gs = fig.add_gridspec(3, 4, height_ratios=[0.8, 1.4, 1.4], hspace=0.5, wspace=0.35)
    fig.suptitle("Power BI Executive Overview - Leatt Fabric BI ML", fontsize=22, fontweight="bold", color="#111111")
    for i, metric in enumerate(["Fact Rows In Fabric OneLake", "Net Revenue", "Gross Margin Rate", "Return Risk AUC"]):
        ax = fig.add_subplot(gs[0, i])
        ax.axis("off")
        val = kpi.loc[kpi["metric"] == metric, "display_value"].iloc[0]
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor="#dddddd", linewidth=1.5))
        ax.text(0.05, 0.68, metric, fontsize=10, color="#555555", transform=ax.transAxes)
        ax.text(0.05, 0.28, val, fontsize=20, fontweight="bold", color="#d71920", transform=ax.transAxes)
    ax = fig.add_subplot(gs[1:, :2])
    ax.plot(monthly["month"], monthly["net_revenue_zar"] / 1_000_000, color="#d71920", linewidth=2.5)
    ax.set_title("Monthly Net Revenue")
    ax.set_ylabel("R millions")
    ax.tick_params(axis="x", rotation=45)
    ax = fig.add_subplot(gs[1:, 2:])
    ax.barh(category["category"], category["net_revenue_zar"] / 1_000_000, color="#111111")
    ax.set_title("Top Categories")
    ax.set_xlabel("R millions")
    p = SCREENSHOTS / "powerbi_executive_overview.png"
    fig.savefig(p, dpi=170, bbox_inches="tight")
    plt.close(fig)
    paths["executive"] = p

    fig = plt.figure(figsize=(16, 9), facecolor="#f6f7f9")
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.28)
    fig.suptitle("Power BI ML Monitoring - Return Risk Model", fontsize=22, fontweight="bold")
    ax = fig.add_subplot(gs[0, 0])
    risk_counts = ml.groupby("risk_band", observed=False)["lines"].sum()
    ax.bar(risk_counts.index.astype(str), risk_counts.values, color=["#4c78a8", "#f58518", "#d71920", "#7f1d1d"])
    ax.set_title("Scored Lines By Risk Band")
    ax = fig.add_subplot(gs[0, 1])
    risk_rev = ml.groupby("risk_band", observed=False)["net_revenue_zar"].sum() / 1_000_000
    ax.bar(risk_rev.index.astype(str), risk_rev.values, color="#d71920")
    ax.set_title("Revenue Exposure By Risk Band")
    ax.set_ylabel("R millions")
    ax = fig.add_subplot(gs[1, 0])
    top_ml = ml.sort_values("avg_risk", ascending=False).head(10).sort_values("avg_risk")
    ax.barh(top_ml["category"] + " / " + top_ml["risk_band"].astype(str), top_ml["avg_risk"], color="#111111")
    ax.set_title("Highest Average Return Risk Segments")
    ax = fig.add_subplot(gs[1, 1])
    ax.axis("off")
    text = "\n".join([f"{k}: {v:.3f}" if isinstance(v, float) else f"{k}: {v}" for k, v in metrics.items() if k in ["auc", "accuracy", "precision", "recall", "training_rows", "test_rows"]])
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor="#dddddd"))
    ax.text(0.07, 0.82, "Model Metrics", fontsize=18, fontweight="bold", color="#d71920", transform=ax.transAxes)
    ax.text(0.07, 0.20, text, fontsize=14, transform=ax.transAxes, linespacing=1.6)
    p = SCREENSHOTS / "powerbi_ml_monitoring.png"
    fig.savefig(p, dpi=170, bbox_inches="tight")
    plt.close(fig)
    paths["ml"] = p

    fig = plt.figure(figsize=(16, 9), facecolor="#f6f7f9")
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.28)
    fig.suptitle("Power BI Marketing And Fabric Proof", fontsize=22, fontweight="bold")
    ax = fig.add_subplot(gs[:, 0])
    ax.barh(channel["channel"], channel["roas"], color="#4c78a8")
    ax.set_title("Marketing ROAS By Channel")
    ax.set_xlabel("ROAS")
    ax = fig.add_subplot(gs[0, 1])
    ax.axis("off")
    proof = "\n".join(f"{r.item}: {r.value}" for r in tables["FabricProof"].itertuples(index=False))
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor="#dddddd"))
    ax.text(0.05, 0.86, "Fabric Deployment", fontsize=16, fontweight="bold", color="#d71920", transform=ax.transAxes)
    ax.text(0.05, 0.15, proof, fontsize=11, transform=ax.transAxes, linespacing=1.5)
    ax = fig.add_subplot(gs[1, 1])
    ax.axis("off")
    info = f"Power BI dataset created\nWorkspace: {powerbi_info['workspace_name']}\nDataset: {powerbi_info['dataset_name']}\nDataset ID: {powerbi_info['dataset_id']}"
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor="#dddddd"))
    ax.text(0.05, 0.78, "Power BI Semantic Model", fontsize=16, fontweight="bold", color="#d71920", transform=ax.transAxes)
    ax.text(0.05, 0.22, info, fontsize=11, transform=ax.transAxes, linespacing=1.6)
    p = SCREENSHOTS / "powerbi_marketing_fabric_proof.png"
    fig.savefig(p, dpi=170, bbox_inches="tight")
    plt.close(fig)
    paths["marketing"] = p
    return paths


def write_report(tables: dict[str, pd.DataFrame], scored: pd.DataFrame, metrics: dict, powerbi_info: dict, screenshots: dict[str, Path]) -> Path:
    metrics_path = OUT / "leatt_ml_return_risk_metrics.csv"
    pd.DataFrame([metrics]).to_csv(metrics_path, index=False)
    scored_path = OUT / "leatt_ml_return_risk_scores_sample.csv"
    scored.head(25000).to_csv(scored_path, index=False)
    powerbi_path = OUT / "powerbi_semantic_model_proof.json"
    powerbi_path.write_text(json.dumps(powerbi_info, indent=2), encoding="utf-8")

    pdf_path = OUT / "leatt_powerbi_ml_report_screenshots.pdf"
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleRed", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#d71920")))
    story = [
        Paragraph("Power BI And ML Delivery Proof", styles["TitleRed"]),
        Paragraph("Power BI semantic model created in the Apollis workspace; ML return-risk model trained and captured with report screenshots.", styles["BodyText"]),
        Spacer(1, 0.3 * cm),
        Table(
            [
                ["Workspace", powerbi_info["workspace_name"]],
                ["Dataset", powerbi_info["dataset_name"]],
                ["Dataset ID", powerbi_info["dataset_id"]],
                ["ML Model", metrics["model_name"]],
                ["AUC", f"{metrics['auc']:.3f}"],
                ["Accuracy", f"{metrics['accuracy']:.3f}"],
            ],
            style=[("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")), ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#111111")), ("TEXTCOLOR", (0, 0), (0, -1), colors.white)],
        ),
        PageBreak(),
    ]
    for title, image_path in [("Executive Overview Screenshot", screenshots["executive"]), ("ML Monitoring Screenshot", screenshots["ml"]), ("Marketing And Fabric Proof Screenshot", screenshots["marketing"])]:
        story += [Paragraph(title, styles["Heading1"]), PdfImage(str(image_path), width=25 * cm, height=14 * cm), PageBreak()]
    SimpleDocTemplate(str(pdf_path), pagesize=landscape(A4), rightMargin=1 * cm, leftMargin=1 * cm, topMargin=1 * cm, bottomMargin=1 * cm).build(story)
    return pdf_path


def copy_to_repo(paths: list[Path], screenshots: dict[str, Path]) -> None:
    if not REPO.exists():
        return
    for folder in [REPO / "artifacts" / "reports", REPO / "artifacts" / "data_samples", REPO / "artifacts" / "evidence_images", REPO / "src" / "powerbi"]:
        folder.mkdir(parents=True, exist_ok=True)
    for p in paths:
        if p.suffix.lower() in [".pdf"]:
            shutil.copy2(p, REPO / "artifacts" / "reports" / p.name)
        elif p.suffix.lower() in [".csv", ".json"]:
            shutil.copy2(p, REPO / "artifacts" / "data_samples" / p.name)
    for p in screenshots.values():
        shutil.copy2(p, REPO / "artifacts" / "evidence_images" / p.name)


def main() -> None:
    data = load_data()
    scored, ml_segment, metrics = train_return_risk(data)
    tables = prepare_powerbi_tables(data, ml_segment, metrics)
    powerbi_info = create_powerbi_dataset(tables)
    screenshots = create_screenshots(tables, metrics, powerbi_info)
    pdf = write_report(tables, scored, metrics, powerbi_info, screenshots)
    paths = [OUT / "leatt_ml_return_risk_metrics.csv", OUT / "leatt_ml_return_risk_scores_sample.csv", OUT / "powerbi_semantic_model_proof.json", pdf]
    copy_to_repo(paths, screenshots)
    print("Power BI and ML artifacts complete")
    print(json.dumps(powerbi_info, indent=2))
    for p in [*screenshots.values(), *paths]:
        print(f"- {p} ({p.stat().st_size / (1024 * 1024):.2f} MB)")


if __name__ == "__main__":
    main()
