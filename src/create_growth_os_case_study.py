from __future__ import annotations

import shutil
import sqlite3
import textwrap
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import cm
from reportlab.platypus import Image as PdfImage
from reportlab.platypus import PageBreak, SimpleDocTemplate


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
REPO = OUT / "leatt-fabric-bi-ml-git-proof"
SQLITE = OUT / "leatt_ecommerce_warehouse.sqlite"
STORY_DIR = OUT / "growth_os_story"
STORY_DIR.mkdir(exist_ok=True)

INK = "#141414"
PAPER = "#f7f4ef"
RED = "#d71920"
MUTED = "#64666a"
LINE = "#dfd8ce"
TEAL = "#007d7e"
GOLD = "#b8860b"
GREEN = "#1b7f4d"


def money(value: float) -> str:
    if abs(value) >= 1_000_000_000:
        return f"R{value / 1_000_000_000:.2f}bn"
    if abs(value) >= 1_000_000:
        return f"R{value / 1_000_000:.1f}m"
    return f"R{value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


def load() -> dict:
    conn = sqlite3.connect(SQLITE)
    fact = conn.execute(
        """
        select
            sum(net_revenue_zar),
            sum(gross_margin_zar),
            sum(return_amount_zar),
            count(distinct order_id),
            count(*)
        from fact_transaction_lines
        """
    ).fetchone()
    data = {
        "category": pd.read_sql("select * from agg_category order by net_revenue_zar desc", conn),
        "monthly": pd.read_sql("select * from agg_monthly order by month", conn),
        "channel": pd.read_sql("select * from agg_channel order by net_revenue_zar desc", conn),
        "province": pd.read_sql("select * from agg_province order by net_revenue_zar desc", conn),
        "product": pd.read_sql("select * from agg_product order by gross_margin_zar desc limit 10", conn),
    }
    conn.close()
    data.update(
        {
            "revenue": fact[0],
            "margin": fact[1],
            "returns": fact[2],
            "orders": fact[3],
            "rows": fact[4],
            "initiatives": pd.read_csv(OUT / "leatt_prioritized_business_initiatives.csv"),
            "signals": pd.read_csv(OUT / "leatt_decision_signal_rules.csv"),
            "seo": pd.read_csv(OUT / "leatt_ai_seo_roadmap.csv"),
            "ab": pd.read_csv(OUT / "leatt_ab_test_results.csv"),
            "competitors": pd.read_csv(OUT / "leatt_competitor_analysis.csv"),
            "recon": pd.read_csv(OUT / "leatt_reconciliation.csv"),
        }
    )
    return data


def fig_page(title: str, kicker: str | None = None):
    fig = plt.figure(figsize=(16, 9), facecolor=PAPER)
    fig.text(0.045, 0.925, title, fontsize=25, fontweight="bold", color=INK)
    if kicker:
        fig.text(0.047, 0.885, kicker, fontsize=11.5, color=MUTED)
    fig.text(0.86, 0.925, "LEATT GROWTH OS", fontsize=9.5, color=RED, fontweight="bold")
    return fig


def save(fig, name: str) -> Path:
    path = STORY_DIR / name
    fig.savefig(path, dpi=175, facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def add_panel(ax, x, y, w, h, fc="white", ec=LINE, lw=1.1, radius=0.0):
    if radius:
        patch = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.015,rounding_size={radius}", facecolor=fc, edgecolor=ec, linewidth=lw)
    else:
        patch = Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=lw)
    ax.add_patch(patch)
    return patch


def wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(str(text), width=width))


def img_ax(fig, path: Path, rect: list[float], title: str | None = None):
    ax = fig.add_axes(rect)
    ax.axis("off")
    if path.exists():
        img = plt.imread(path)
        ax.imshow(img)
    else:
        ax.add_patch(Rectangle((0, 0), 1, 1, color="#eeeeee"))
        ax.text(0.5, 0.5, "Missing image", ha="center", va="center", color=MUTED)
    if title:
        ax.text(0.02, 0.96, title, transform=ax.transAxes, va="top", color="white", fontsize=11, fontweight="bold", bbox={"facecolor": INK, "edgecolor": "none", "pad": 4})
    return ax


def stat(fig, x, y, label, value, note, color=INK):
    ax = fig.add_axes([x, y, 0.2, 0.13])
    ax.axis("off")
    add_panel(ax, 0, 0, 1, 1)
    ax.text(0.06, 0.72, label.upper(), color=MUTED, fontsize=8, fontweight="bold", transform=ax.transAxes)
    ax.text(0.06, 0.34, value, color=color, fontsize=18, fontweight="bold", transform=ax.transAxes)
    ax.text(0.06, 0.13, note, color=MUTED, fontsize=8.5, transform=ax.transAxes)


def cover(data: dict) -> Path:
    fig = plt.figure(figsize=(16, 9), facecolor=INK)
    img_ax(fig, OUT / "evidence_images" / "leatt_moto_boots_collection.png", [0.50, 0.08, 0.47, 0.78])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 0.58, 1, color=INK, alpha=0.96))
    ax.add_patch(Rectangle((0.045, 0.16), 0.006, 0.64, color=RED))
    ax.text(0.075, 0.74, "LEATT\nGROWTH OS", color="white", fontsize=46, fontweight="bold", va="top", linespacing=0.9)
    ax.text(0.078, 0.47, "A non-boring ecommerce BI + ML case study", color="#f1ebe1", fontsize=17, fontweight="bold")
    ax.text(
        0.078,
        0.37,
        wrap("From storefront evidence to Fabric Lakehouse, Power BI, ML return-risk, AI SEO, SAP reconciliation and executive action.", 62),
        color="#c9c3ba",
        fontsize=12.5,
        linespacing=1.35,
    )
    ax.text(0.078, 0.18, f"{data['rows']:,} modeled transaction lines | {money(data['revenue'])} revenue | {pct(data['returns']/data['revenue'])} return leakage", color="white", fontsize=11)
    return save(fig, "01_growth_os_cover.png")


def storyline(data: dict) -> Path:
    fig = fig_page("One Story, Not A Folder Of Reports", "The project reads as a single operating system for ecommerce growth.")
    ax = fig.add_axes([0.04, 0.10, 0.92, 0.72])
    ax.axis("off")
    steps = [
        ("1", "Storefront\nSignal", "What products, categories and content are visible?"),
        ("2", "Data\nEngine", "Fabric, Lakehouse, Factory, ERD and semantic model."),
        ("3", "Money\nMap", "Revenue, margin, returns, regions and channels."),
        ("4", "Growth\nLoop", "SEO, A/B tests, campaigns and competitor signals."),
        ("5", "Control\nTower", "ML risk, governance, reconciliation and SAP fit."),
        ("6", "Actions", "Owner-led 90-day moves and interview-ready proof."),
    ]
    card_w = 0.145
    gap = 0.016
    start_x = 0.018
    for i, (n, title, desc) in enumerate(steps):
        x = start_x + i * (card_w + gap)
        accent = RED if n in {"1", "6"} else INK
        add_panel(ax, x, 0.12, card_w, 0.58)
        ax.add_patch(Rectangle((x, 0.66), card_w, 0.04, facecolor=accent, edgecolor=accent, transform=ax.transAxes))
        ax.text(x + 0.018, 0.58, n, color=accent, fontsize=20, fontweight="bold", transform=ax.transAxes)
        ax.text(x + 0.018, 0.42, title, color=INK, fontsize=13.5, fontweight="bold", linespacing=0.9, transform=ax.transAxes)
        ax.text(x + 0.018, 0.19, wrap(desc, 20), color=MUTED, fontsize=8.7, linespacing=1.22, transform=ax.transAxes)
    ax.text(0.05, 0.82, "The through-line", fontsize=14, fontweight="bold", color=INK)
    ax.text(0.05, 0.76, wrap("Leatt sells performance gear. The BI story is therefore about protecting profitable demand: the right product, in the right channel, with the right content, while controlling fit/return risk and proving the numbers back to finance.", 150), fontsize=12, color=MUTED)
    return save(fig, "02_one_story.png")


def storefront(data: dict) -> Path:
    fig = fig_page("The Storefront Is The Brief", "Use the real site as the narrative anchor: product, category, price, content and customer intent.")
    img_ax(fig, OUT / "evidence_images" / "leatt_about_source.png", [0.045, 0.50, 0.39, 0.30], "Brand proof")
    img_ax(fig, OUT / "evidence_images" / "leatt_lifestyle_eyewear_collection.png", [0.465, 0.50, 0.23, 0.30], "Lifestyle")
    img_ax(fig, OUT / "evidence_images" / "leatt_moto_boots_collection.png", [0.72, 0.50, 0.235, 0.30], "Moto boots")
    ax = fig.add_axes([0.045, 0.12, 0.91, 0.28])
    ax.axis("off")
    add_panel(ax, 0, 0, 1, 1)
    ax.text(0.03, 0.78, "What this signals", fontsize=15, fontweight="bold", color=INK)
    bullets = [
        "This is not abstract ecommerce: the category mix has safety, fit, seasonality and premium-price dynamics.",
        "Public storefront evidence points to Shopify, so SAP Commerce/Hybris is not required for this proof.",
        "SAP Business One or SAP BW fits as the finance/inventory authority for reconciliation, VAT, stock and margin.",
        "BI value comes from connecting storefront demand to returns, channel spend, stock risk and finance truth.",
    ]
    y = 0.58
    for b in bullets:
        ax.text(0.04, y, f"- {b}", fontsize=11, color=MUTED, transform=ax.transAxes)
        y -= 0.15
    return save(fig, "03_storefront_brief.png")


def data_engine(data: dict) -> Path:
    fig = fig_page("The Engine: Fabric, Factory, Lakehouse, Warehouse", "This is the proof layer: data movement, modeling, governance and source control.")
    img_ax(fig, OUT / "evidence_images" / "fabric_data_factory_pipeline_blueprint.png", [0.045, 0.49, 0.42, 0.34], "Data Factory blueprint")
    img_ax(fig, OUT / "evidence_images" / "leatt_star_schema_erd.png", [0.50, 0.49, 0.455, 0.34], "ERD / semantic grain")
    ax = fig.add_axes([0.045, 0.12, 0.91, 0.27])
    ax.axis("off")
    stats = [
        ("Rows", f"{data['rows']:,}", "enterprise-scale synthetic transaction fact"),
        ("Warehouse", "SQLite + Fabric plan", "local proof plus OneLake runbook"),
        ("Power BI", "semantic model", "report item created through API"),
        ("Git", "pushed proof", "scripts, docs, evidence and outputs"),
    ]
    for i, (label, value, note) in enumerate(stats):
        x = 0.02 + i * 0.245
        add_panel(ax, x, 0.08, 0.22, 0.82)
        ax.text(x + 0.02, 0.67, label.upper(), color=MUTED, fontsize=8, fontweight="bold")
        ax.text(x + 0.02, 0.43, value, color=RED if i == 0 else INK, fontsize=16, fontweight="bold")
        ax.text(x + 0.02, 0.22, wrap(note, 27), color=MUTED, fontsize=8.5)
    return save(fig, "04_data_engine.png")


def money_map(data: dict) -> Path:
    fig = fig_page("The Money Map: Growth Quality Beats Vanity Revenue", "The case study follows margin, returns and category concentration, not only sales.")
    category = data["category"].head(7).sort_values("net_revenue_zar")
    monthly = data["monthly"].copy()
    stat(fig, 0.045, 0.72, "Revenue", money(data["revenue"]), "scale signal", RED)
    stat(fig, 0.275, 0.72, "Gross margin", pct(data["margin"] / data["revenue"]), "quality signal", GREEN)
    stat(fig, 0.505, 0.72, "Return leakage", pct(data["returns"] / data["revenue"]), "risk signal", GOLD)
    stat(fig, 0.735, 0.72, "Orders", f"{data['orders']:,}", "transaction grain", INK)
    ax = fig.add_axes([0.06, 0.15, 0.43, 0.45])
    ax.set_facecolor("white")
    ax.barh(category["category"], category["net_revenue_zar"] / 1_000_000, color=[RED if i == len(category)-1 else INK for i in range(len(category))])
    ax.set_title("Hero category concentration", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Revenue, R millions")
    ax.grid(axis="x", color="#eee8df")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax = fig.add_axes([0.55, 0.15, 0.39, 0.45])
    ax.set_facecolor("white")
    ax.plot(monthly["month"], monthly["net_revenue_zar"] / 1_000_000, color=RED, lw=3)
    ax.plot(monthly["month"], monthly["gross_margin_zar"] / 1_000_000, color=INK, lw=2)
    ax.set_title("Revenue and margin move together", loc="left", fontsize=13, fontweight="bold")
    ax.set_ylabel("R millions")
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    ax.grid(axis="y", color="#eee8df")
    for spine in ax.spines.values():
        spine.set_visible(False)
    return save(fig, "05_money_map.png")


def leak_and_ml(data: dict) -> Path:
    fig = fig_page("The Leak: Returns Are A Margin Problem Wearing A CX Mask", "ML turns return risk from a lagging report into a management queue.")
    signals = data["signals"].head(5)
    products = data["product"].sort_values("gross_margin_zar").tail(7)
    ax = fig.add_axes([0.055, 0.16, 0.42, 0.58])
    ax.set_facecolor("white")
    ax.barh(products["product_title"].str.slice(0, 34), products["gross_margin_zar"] / 1_000_000, color=RED)
    ax.set_title("Products to protect by margin", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Gross margin, R millions")
    ax.grid(axis="x", color="#eee8df")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax = fig.add_axes([0.52, 0.16, 0.43, 0.58])
    ax.axis("off")
    add_panel(ax, 0, 0, 1, 1)
    ax.text(0.05, 0.86, "Signal rules", fontsize=15, fontweight="bold", color=INK)
    y = 0.70
    for row in signals.itertuples(index=False):
        ax.text(0.05, y, row.signal, fontsize=10.5, fontweight="bold", color=INK, transform=ax.transAxes)
        ax.text(0.05, y - 0.07, wrap(row.recommended_decision, 62), fontsize=9.2, color=MUTED, transform=ax.transAxes)
        y -= 0.16
    return save(fig, "06_leak_ml.png")


def growth_loop(data: dict) -> Path:
    fig = fig_page("The Growth Loop: SEO, A/B Testing, Campaign Discipline", "Growth is only interesting when the loop can be measured and improved.")
    seo = data["seo"]
    ab = data["ab"]
    comp = data["competitors"].head(5)
    ax = fig.add_axes([0.055, 0.56, 0.39, 0.25])
    ax.axis("off")
    add_panel(ax, 0, 0, 1, 1)
    ax.text(0.05, 0.75, "A/B testing role", fontsize=15, fontweight="bold", color=INK)
    best = ab.sort_values("Estimated incremental gross margin", ascending=False).iloc[0]
    ax.text(0.05, 0.48, wrap(f"Best test: {best['Test']} generated {money(best['Estimated incremental gross margin'])} modeled incremental margin.", 60), fontsize=10.5, color=MUTED)
    ax.text(0.05, 0.18, "Use tests to prove margin-positive change, not cosmetic conversion wins.", fontsize=10.2, color=RED, fontweight="bold")
    ax = fig.add_axes([0.50, 0.56, 0.43, 0.25])
    ax.set_facecolor("white")
    scores = list(range(len(comp), 0, -1))
    ax.bar(comp["Competitor"], scores, color=[RED, INK, INK, TEAL, GOLD][: len(comp)])
    ax.set_title("Competitor benchmark map", loc="left", fontsize=13, fontweight="bold")
    ax.set_ylabel("Qualitative threat rank")
    ax.tick_params(axis="x", rotation=18, labelsize=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax = fig.add_axes([0.055, 0.14, 0.875, 0.30])
    ax.axis("off")
    add_panel(ax, 0, 0, 1, 1)
    ax.text(0.03, 0.80, "AI SEO roadmap", fontsize=15, fontweight="bold", color=INK)
    xs = np.linspace(0.08, 0.88, len(seo))
    ax.plot([xs[0], xs[-1]], [0.50, 0.50], color=LINE, lw=4, transform=ax.transAxes)
    for x, row in zip(xs, seo.itertuples(index=False)):
        ax.add_patch(Circle((x, 0.50), 0.035, color=RED if x == xs[0] else INK, transform=ax.transAxes))
        ax.text(x, 0.36, row.timeframe, ha="center", fontsize=8.5, color=MUTED, transform=ax.transAxes)
        ax.text(x, 0.18, wrap(row.workstream, 16), ha="center", fontsize=8.5, color=INK, transform=ax.transAxes)
    return save(fig, "07_growth_loop.png")


def finance_control(data: dict) -> Path:
    fig = fig_page("The Control Layer: SAP, Reconciliation, Governance", "The report becomes credible when it can survive finance and audit questions.")
    img_ax(fig, OUT / "evidence_images" / "accounting_reconciliation_sales_vat.png", [0.055, 0.53, 0.42, 0.28], "Accounting proof")
    img_ax(fig, OUT / "evidence_images" / "data_governance_controls.png", [0.52, 0.53, 0.40, 0.28], "Governance proof")
    ax = fig.add_axes([0.055, 0.14, 0.87, 0.28])
    ax.axis("off")
    add_panel(ax, 0, 0, 1, 1)
    ax.text(0.035, 0.78, "Where SAP fits", fontsize=15, fontweight="bold", color=INK)
    copy = [
        "SAP Business One: practical fit for finance, inventory, VAT, chart of accounts, sales documents and close reconciliation.",
        "SAP BW: fit when the company already runs SAP enterprise reporting and needs governed extracts into Fabric.",
        "SAP Commerce / Hybris: possible in a larger SAP commerce estate, but the public storefront evidence does not require it here.",
        "Fabric remains the analytics layer: ingest, model, score, govern and publish to Power BI.",
    ]
    y = 0.57
    for line in copy:
        ax.text(0.04, y, f"- {line}", fontsize=10.5, color=MUTED, transform=ax.transAxes)
        y -= 0.15
    return save(fig, "08_finance_control.png")


def report_path(data: dict) -> Path:
    fig = fig_page("How To Read The Power BI Report", "The report has a path: performance, growth, risk, proof.")
    img_ax(fig, OUT / "screenshots" / "powerbi_executive_overview.png", [0.045, 0.53, 0.28, 0.25], "1 Executive")
    img_ax(fig, OUT / "screenshots" / "powerbi_marketing_fabric_proof.png", [0.36, 0.53, 0.28, 0.25], "2 Growth")
    img_ax(fig, OUT / "screenshots" / "powerbi_ml_monitoring.png", [0.675, 0.53, 0.28, 0.25], "3 ML")
    ax = fig.add_axes([0.045, 0.14, 0.91, 0.28])
    ax.axis("off")
    add_panel(ax, 0, 0, 1, 1)
    path = [
        ("Start", "Are we growing profitably?"),
        ("Then", "Which channels/content deserve money?"),
        ("Then", "Where is leakage and model risk?"),
        ("End", "Can the data be proven in Azure/Fabric/Git?"),
    ]
    xs = [0.08, 0.34, 0.60, 0.84]
    for x, (label, question) in zip(xs, path):
        ax.add_patch(Circle((x, 0.58), 0.045, color=RED if label in {"Start", "End"} else INK, transform=ax.transAxes))
        ax.text(x, 0.58, label[0], ha="center", va="center", color="white", fontweight="bold", transform=ax.transAxes)
        ax.text(x, 0.34, label, ha="center", fontsize=12, color=INK, fontweight="bold", transform=ax.transAxes)
        ax.text(x, 0.18, wrap(question, 30), ha="center", fontsize=9.5, color=MUTED, transform=ax.transAxes)
    return save(fig, "09_powerbi_reading_path.png")


def action_plan(data: dict) -> Path:
    fig = fig_page("The Ending: A 90-Day Growth Operating Plan", "A case study lands when the viewer knows exactly what to do next.")
    initiatives = data["initiatives"].sort_values("priority_score", ascending=False).head(5)
    ax = fig.add_axes([0.055, 0.12, 0.89, 0.70])
    ax.axis("off")
    headers = ["Move", "Why it matters", "Owner", "Next action"]
    widths = [0.23, 0.25, 0.16, 0.29]
    x = 0.02
    for h, w in zip(headers, widths):
        ax.text(x, 0.92, h.upper(), fontsize=8.5, color=MUTED, fontweight="bold", transform=ax.transAxes)
        x += w
    y = 0.78
    for row in initiatives.itertuples(index=False):
        ax.add_patch(Rectangle((0.0, y - 0.05), 0.98, 0.12, facecolor="white", edgecolor=LINE, linewidth=0.8, transform=ax.transAxes))
        ax.text(0.02, y, wrap(row.initiative, 29), fontsize=10.5, color=INK, fontweight="bold", transform=ax.transAxes)
        ax.text(0.25, y, wrap(str(row.estimated_value), 30), fontsize=10, color=RED, transform=ax.transAxes)
        ax.text(0.50, y, wrap(row.owner, 20), fontsize=9.5, color=MUTED, transform=ax.transAxes)
        ax.text(0.66, y, wrap(row.next_step, 45), fontsize=9.5, color=MUTED, transform=ax.transAxes)
        y -= 0.15
    ax.text(0.02, 0.04, "Interview message: this is not a report pack. It is a senior BI operating model that connects data engineering, Power BI, ML, AI SEO, accounting controls, cloud cost discipline and business action.", fontsize=12, color=INK, fontweight="bold", transform=ax.transAxes)
    return save(fig, "10_90_day_plan.png")


def build_pdf(images: list[Path], path: Path) -> Path:
    doc = SimpleDocTemplate(str(path), pagesize=landscape(A4), rightMargin=0, leftMargin=0, topMargin=0, bottomMargin=0)
    story = []
    for i, image in enumerate(images):
        story.append(PdfImage(str(image), width=29.7 * cm, height=16.7 * cm))
        if i < len(images) - 1:
            story.append(PageBreak())
    doc.build(story)
    return path


def write_md(data: dict, path: Path) -> Path:
    top_cat = data["category"].iloc[0]
    path.write_text(
        f"""# Leatt Growth OS Case Study

This is the tighter storyline for the portfolio: not a scattered report pack, but one senior BI case study.

## Narrative Spine

Leatt sells performance gear, so the analytics story is about protecting profitable demand. The customer wants gear that fits, protects, ships, and performs. Leadership wants margin, stock visibility, channel discipline, return control and finance-ready proof.

## What The Data Says

- Modeled transaction rows: {data['rows']:,}
- Modeled revenue: {money(data['revenue'])}
- Gross margin rate: {pct(data['margin'] / data['revenue'])}
- Return leakage: {pct(data['returns'] / data['revenue'])}
- Hero category: {top_cat['category']} at {money(top_cat['net_revenue_zar'])}

## The Story Arc

1. The storefront is the brief: product categories, prices and content reveal demand.
2. Fabric is the engine: ingest, model, score and govern the data.
3. Power BI is the control room: performance, growth, ML risk and proof.
4. ML reduces leakage: returns and margin risk become owner-led queues.
5. AI SEO and A/B testing create growth loops.
6. SAP Business One or SAP BW supplies finance/inventory truth; SAP Commerce/Hybris is possible but not required by the storefront proof.

## Why It Is Valuable

The project demonstrates a complete BI operating model: source extraction, million-row transactional modeling, data warehousing, Fabric/Data Factory thinking, Power BI, ML, accounting reconciliation, data governance, SEO, competitor analysis, A/B testing, Git proof and cloud cost control.

Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}.
""",
        encoding="utf-8",
    )
    return path


def copy_to_repo(paths: list[Path]) -> None:
    if not REPO.exists():
        return
    (REPO / "docs").mkdir(parents=True, exist_ok=True)
    (REPO / "artifacts" / "reports").mkdir(parents=True, exist_ok=True)
    (REPO / "artifacts" / "evidence_images" / "growth_os_story").mkdir(parents=True, exist_ok=True)
    for p in paths:
        if p.suffix.lower() == ".pdf":
            shutil.copy2(p, REPO / "artifacts" / "reports" / p.name)
        elif p.suffix.lower() == ".md":
            shutil.copy2(p, REPO / "docs" / p.name)
        elif p.suffix.lower() == ".png":
            shutil.copy2(p, REPO / "artifacts" / "evidence_images" / "growth_os_story" / p.name)
    shutil.copy2(Path(__file__), REPO / "src" / "create_growth_os_case_study.py")


def main() -> None:
    data = load()
    images = [
        cover(data),
        storyline(data),
        storefront(data),
        data_engine(data),
        money_map(data),
        leak_and_ml(data),
        growth_loop(data),
        finance_control(data),
        report_path(data),
        action_plan(data),
    ]
    outputs = [
        *images,
        build_pdf(images, OUT / "leatt_growth_os_case_study.pdf"),
        write_md(data, OUT / "leatt_growth_os_case_study.md"),
    ]
    copy_to_repo(outputs)
    print("Growth OS case study complete:")
    for p in outputs:
        print(f"- {p} ({p.stat().st_size / (1024 * 1024):.2f} MB)")


if __name__ == "__main__":
    main()
