from __future__ import annotations

import shutil
import sqlite3
import textwrap
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image as PdfImage
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
REPO = OUT / "leatt-fabric-bi-ml-git-proof"
SQLITE = OUT / "leatt_ecommerce_warehouse.sqlite"
PREMIUM = OUT / "premium_design"
PREMIUM.mkdir(exist_ok=True)

RED = "#d71920"
INK = "#171717"
MUTED = "#6f7378"
PAPER = "#f5f2ed"
LINE = "#ded8ce"
TEAL = "#007d7e"
GOLD = "#b8860b"


def money(value: float) -> str:
    if abs(value) >= 1_000_000_000:
        return f"R{value / 1_000_000_000:.2f}bn"
    if abs(value) >= 1_000_000:
        return f"R{value / 1_000_000:.1f}m"
    return f"R{value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


def load_data() -> dict[str, pd.DataFrame]:
    conn = sqlite3.connect(SQLITE)
    data = {
        "monthly": pd.read_sql("select * from agg_monthly order by month", conn),
        "category": pd.read_sql("select * from agg_category order by net_revenue_zar desc", conn),
        "channel": pd.read_sql("select * from agg_channel order by net_revenue_zar desc", conn),
        "province": pd.read_sql("select * from agg_province order by net_revenue_zar desc", conn),
        "product": pd.read_sql("select * from agg_product order by gross_margin_zar desc limit 12", conn),
    }
    conn.close()
    data["channel_intel"] = pd.read_csv(OUT / "leatt_intelligent_channel.csv")
    data["initiatives"] = pd.read_csv(OUT / "leatt_prioritized_business_initiatives.csv")
    data["signals"] = pd.read_csv(OUT / "leatt_decision_signal_rules.csv")
    data["seo"] = pd.read_csv(OUT / "leatt_ai_seo_roadmap.csv")
    return data


def metrics(data: dict[str, pd.DataFrame]) -> dict[str, float | str]:
    monthly = data["monthly"]
    category = data["category"]
    channel = data["channel_intel"]
    revenue = monthly["net_revenue_zar"].sum()
    margin = monthly["gross_margin_zar"].sum()
    returns = monthly["return_amount_zar"].sum()
    orders_proxy = monthly["quantity"].sum()
    top_cat = category.iloc[0]
    best_channel = channel.sort_values("roas", ascending=False).iloc[0]
    return {
        "revenue": revenue,
        "margin": margin,
        "margin_rate": margin / revenue,
        "return_rate": returns / revenue,
        "aov_proxy": revenue / max(orders_proxy, 1),
        "top_category": top_cat["category"],
        "top_category_revenue": top_cat["net_revenue_zar"],
        "best_channel": best_channel["channel"],
        "best_roas": best_channel["roas"],
    }


def set_ax(ax):
    ax.set_facecolor("white")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="x", color="#eee8df", linewidth=0.8)
    ax.tick_params(colors=MUTED, labelsize=9)


def draw_card(fig, x, y, w, h, label, value, signal, color=INK):
    ax = fig.add_axes([x, y, w, h])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor=LINE, linewidth=1.2))
    ax.text(0.06, 0.72, label.upper(), color=MUTED, fontsize=8, fontweight="bold", transform=ax.transAxes)
    ax.text(0.06, 0.34, value, color=color, fontsize=18, fontweight="bold", transform=ax.transAxes)
    ax.text(0.06, 0.13, signal, color=MUTED, fontsize=8.5, transform=ax.transAxes)
    return ax


def premium_dashboard(data: dict[str, pd.DataFrame], out: Path) -> Path:
    m = metrics(data)
    monthly = data["monthly"].copy()
    category = data["category"].head(7).sort_values("net_revenue_zar")
    initiatives = data["initiatives"].sort_values("priority_score", ascending=False).head(4)

    fig = plt.figure(figsize=(16, 9), facecolor=PAPER)
    fig.text(0.045, 0.93, "Leatt Ecommerce BI Command View", fontsize=23, fontweight="bold", color=INK)
    fig.text(0.045, 0.895, "Executive page: growth quality, margin leakage and next action", fontsize=11, color=MUTED)
    fig.text(0.83, 0.925, "Fabric | Power BI | ML", fontsize=10, color=RED, fontweight="bold")

    draw_card(fig, 0.045, 0.73, 0.205, 0.13, "Revenue", money(m["revenue"]), "Scale is enterprise-grade", RED)
    draw_card(fig, 0.27, 0.73, 0.205, 0.13, "Gross Margin", pct(m["margin_rate"]), "Protect quality of growth", INK)
    draw_card(fig, 0.495, 0.73, 0.205, 0.13, "Return Leakage", pct(m["return_rate"]), "Near 5% action threshold", GOLD)
    draw_card(fig, 0.72, 0.73, 0.235, 0.13, "Best Channel", f"{m['best_channel']} {m['best_roas']:.0f}x", "Scale with guardrails", TEAL)

    ax = fig.add_axes([0.045, 0.39, 0.55, 0.27])
    set_ax(ax)
    ax.plot(monthly["month"], monthly["net_revenue_zar"] / 1_000_000, color=RED, linewidth=3)
    ax.fill_between(range(len(monthly)), monthly["net_revenue_zar"] / 1_000_000, color=RED, alpha=0.07)
    ax.set_title("Revenue Trend", loc="left", fontsize=13, fontweight="bold", color=INK)
    ax.set_ylabel("R millions", color=MUTED)
    ax.tick_params(axis="x", rotation=45)

    ax = fig.add_axes([0.64, 0.39, 0.315, 0.27])
    set_ax(ax)
    colors_ = [RED if c == m["top_category"] else INK for c in category["category"]]
    ax.barh(category["category"], category["net_revenue_zar"] / 1_000_000, color=colors_)
    ax.set_title("Hero Categories", loc="left", fontsize=13, fontweight="bold", color=INK)
    ax.set_xlabel("R millions", color=MUTED)

    ax = fig.add_axes([0.045, 0.09, 0.43, 0.23])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor=LINE, linewidth=1.2))
    ax.text(0.04, 0.82, "Decision Signal", fontsize=13, fontweight="bold", color=INK, transform=ax.transAxes)
    decision_lines = "\n".join(
        textwrap.wrap(
            f"{m['top_category']} contributes {money(m['top_category_revenue'])}. Treat it as a protected growth engine, not just a top seller.",
            78,
        )
    )
    action_lines = "\n".join(
        textwrap.wrap(
            "Use stock alerts, category SEO hubs, bundle tests and return-rate watchlists to protect profitable demand.",
            84,
        )
    )
    ax.text(0.04, 0.52, decision_lines, fontsize=10.2, color=INK, transform=ax.transAxes, linespacing=1.4)
    ax.text(0.04, 0.18, action_lines, fontsize=10.2, color=MUTED, transform=ax.transAxes, linespacing=1.4)

    ax = fig.add_axes([0.51, 0.09, 0.445, 0.23])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor=LINE, linewidth=1.2))
    ax.text(0.04, 0.82, "Prioritized Actions", fontsize=13, fontweight="bold", color=INK, transform=ax.transAxes)
    y = 0.62
    for row in initiatives.itertuples(index=False):
        ax.text(0.04, y, f"{row.priority_score}  {row.initiative}", fontsize=10.2, color=INK, fontweight="bold", transform=ax.transAxes)
        ax.text(0.04, y - 0.12, str(row.estimated_value), fontsize=9, color=RED, transform=ax.transAxes)
        y -= 0.21

    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def growth_dashboard(data: dict[str, pd.DataFrame], out: Path) -> Path:
    channel = data["channel_intel"].sort_values("roas")
    seo = data["seo"]
    category = data["category"].head(5)

    fig = plt.figure(figsize=(16, 9), facecolor=PAPER)
    fig.text(0.045, 0.93, "Growth, AI SEO And Channel Quality", fontsize=23, fontweight="bold", color=INK)
    fig.text(0.045, 0.895, "Marketing page: spend only scales after ROAS, landing-page relevance and margin hold", fontsize=11, color=MUTED)

    ax = fig.add_axes([0.045, 0.55, 0.44, 0.29])
    set_ax(ax)
    ax.barh(channel["channel"], channel["roas"], color=[TEAL if v > 30 else GOLD for v in channel["roas"]])
    ax.set_title("ROAS Guardrails", loc="left", fontsize=13, fontweight="bold", color=INK)
    ax.set_xlabel("Revenue / estimated spend", color=MUTED)

    ax = fig.add_axes([0.53, 0.55, 0.425, 0.29])
    set_ax(ax)
    ax.bar(category["category"], category["gross_margin_zar"] / 1_000_000, color=INK)
    ax.set_title("SEO Should Prioritize Margin Pools", loc="left", fontsize=13, fontweight="bold", color=INK)
    ax.set_ylabel("R millions", color=MUTED)
    ax.tick_params(axis="x", rotation=25)

    ax = fig.add_axes([0.045, 0.1, 0.91, 0.34])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor=LINE, linewidth=1.2))
    ax.text(0.03, 0.84, "12-Week AI SEO Roadmap", fontsize=14, fontweight="bold", color=INK, transform=ax.transAxes)
    x_positions = np.linspace(0.05, 0.86, len(seo))
    for x, row in zip(x_positions, seo.itertuples(index=False)):
        ax.add_patch(plt.Circle((x, 0.55), 0.035, color=RED if "Technical" in row.workstream or "Hero" in row.workstream else INK, transform=ax.transAxes))
        ax.text(x, 0.43, row.timeframe, ha="center", fontsize=8.5, color=MUTED, transform=ax.transAxes)
        ax.text(x, 0.28, "\n".join(textwrap.wrap(row.workstream, 15)), ha="center", fontsize=8.2, color=INK, transform=ax.transAxes)
    ax.plot([x_positions[0], x_positions[-1]], [0.55, 0.55], color=LINE, linewidth=3, transform=ax.transAxes, zorder=0)

    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def ml_governance_dashboard(data: dict[str, pd.DataFrame], out: Path) -> Path:
    signals = data["signals"]
    product = data["product"].sort_values("gross_margin_zar").tail(8)
    province = data["province"].head(8).sort_values("net_revenue_zar")

    fig = plt.figure(figsize=(16, 9), facecolor=PAPER)
    fig.text(0.045, 0.93, "ML, Governance And Audit Readiness", fontsize=23, fontweight="bold", color=INK)
    fig.text(0.045, 0.895, "Risk page: return leakage, data controls and finance-ready evidence", fontsize=11, color=MUTED)

    ax = fig.add_axes([0.045, 0.53, 0.43, 0.31])
    set_ax(ax)
    ax.barh(product["product_title"].str.slice(0, 32), product["gross_margin_zar"] / 1_000_000, color=RED)
    ax.set_title("Products To Protect By Margin", loc="left", fontsize=13, fontweight="bold", color=INK)
    ax.set_xlabel("R millions", color=MUTED)

    ax = fig.add_axes([0.53, 0.53, 0.425, 0.31])
    set_ax(ax)
    ax.barh(province["province"], province["net_revenue_zar"] / 1_000_000, color=INK)
    ax.set_title("Regional Revenue Pools", loc="left", fontsize=13, fontweight="bold", color=INK)
    ax.set_xlabel("R millions", color=MUTED)

    ax = fig.add_axes([0.045, 0.09, 0.91, 0.32])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor=LINE, linewidth=1.2))
    ax.text(0.03, 0.82, "Signal Rules: What Changes Trigger Action", fontsize=14, fontweight="bold", color=INK, transform=ax.transAxes)
    y = 0.62
    for row in signals.head(5).itertuples(index=False):
        ax.text(0.03, y, row.signal, fontsize=10.5, fontweight="bold", color=INK, transform=ax.transAxes)
        ax.text(0.26, y, row.current_reading, fontsize=10.2, color=RED, transform=ax.transAxes)
        ax.text(0.42, y, row.recommended_decision, fontsize=9.3, color=MUTED, transform=ax.transAxes)
        y -= 0.13

    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def design_system_md() -> Path:
    path = OUT / "leatt_premium_report_design_system.md"
    path.write_text(
        """# Premium BI Report Design System

This design refresh is based on current dashboard and data-storytelling guidance:

- Put the audience and decision first, not the dataset.
- Tell the executive story on one screen where possible.
- Put the highest-level metrics top-left and detail below.
- Use cards only for numbers that deserve prominence.
- Use bar/line charts for comparison and trend; avoid decorative chart variety.
- Use consistent scales, simple number formatting and direct labels.
- Keep each page to one primary question.
- Add interpretation and action beside the visuals.

## Visual Style

- Background: warm off-white, not sterile white.
- Primary accent: Leatt red for the focal signal.
- Neutral ink: near-black for structure and bars.
- Secondary accents: teal for efficiency/opportunity, gold for risk/warning.
- Layout: 16:9 executive canvas, four KPI cards, two evidence charts, one decision/action strip.

## Redesigned Pages

- Executive Command View: Are we growing profitably, and what should leadership do next?
- Growth / AI SEO View: Which channels and content investments deserve scaling?
- ML / Governance View: Where is leakage, and is the data estate audit-ready?

## Sources Used

- Microsoft Power BI dashboard design tips: https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboards-design-tips
- Microsoft Power BI reports and dashboards guidance: https://learn.microsoft.com/en-sg/power-bi/create-reports/
- Tableau data-story best practices: https://help.tableau.com/current/pro/desktop/en-us/story_best_practices.htm
- Juice Analytics dashboard storytelling: https://www.juiceanalytics.com/writing/how-to-apply-data-storytelling-to-dashboards
- Datawireframe dashboard design best practices: https://www.datawirefra.me/blog/dashboard-design-best-practices
""",
        encoding="utf-8",
    )
    return path


def write_pdf(images: list[Path], title: str, path: Path) -> Path:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleRed", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor(RED)))
    doc = SimpleDocTemplate(str(path), pagesize=landscape(A4), rightMargin=0.7 * cm, leftMargin=0.7 * cm, topMargin=0.7 * cm, bottomMargin=0.7 * cm)
    story = [
        Paragraph(title, styles["TitleRed"]),
        Paragraph("Premium redesign: executive hierarchy, clear signal, and action-first BI storytelling.", styles["BodyText"]),
        Spacer(1, 0.4 * cm),
    ]
    for i, image in enumerate(images):
        story.append(PdfImage(str(image), width=27.5 * cm, height=15.45 * cm))
        if i < len(images) - 1:
            story.append(PageBreak())
    doc.build(story)
    return path


def write_ebook(images: list[Path], data: dict[str, pd.DataFrame], path: Path) -> Path:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleRed", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor(RED)))
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=1.2 * cm, leftMargin=1.2 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    initiatives = data["initiatives"].sort_values("priority_score", ascending=False).head(5)
    rows = [["Priority", "Initiative", "Value", "Owner"]]
    rows += [[str(r.priority_score), r.initiative, str(r.estimated_value), r.owner] for r in initiatives.itertuples(index=False)]
    story = [
        Paragraph("Leatt Premium BI Storybook", styles["TitleRed"]),
        Paragraph("A redesigned business intelligence narrative for senior stakeholders.", styles["BodyText"]),
        Spacer(1, 0.4 * cm),
        Paragraph("Design Thesis", styles["Heading1"]),
        Paragraph("The report now leads with decisions: growth quality, return leakage, channel discipline, AI SEO opportunity and audit readiness. Each page has one question, one main signal, and a clear action path.", styles["BodyText"]),
        Spacer(1, 0.5 * cm),
        Table(rows, repeatRows=1, colWidths=[2 * cm, 8 * cm, 3 * cm, 4 * cm], style=[
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(INK)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor(LINE)),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]),
    ]
    for image in images:
        story += [PageBreak(), PdfImage(str(image), width=18 * cm, height=10.1 * cm)]
    doc.build(story)
    return path


def html_index(images: list[Path]) -> Path:
    path = OUT / "premium_dashboard_gallery.html"
    cards = "\n".join(
        f'<section><h2>{img.stem.replace("_", " ").title()}</h2><img src="premium_design/{img.name}" /></section>'
        for img in images
    )
    path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Leatt Premium BI Gallery</title>
<style>
body {{ margin:0; font-family: Arial, sans-serif; background:{PAPER}; color:{INK}; }}
header {{ padding:36px 48px; background:{INK}; color:white; border-bottom:6px solid {RED}; }}
main {{ max-width:1180px; margin:0 auto; padding:28px; }}
section {{ margin:28px 0; background:white; border:1px solid {LINE}; padding:18px; }}
img {{ width:100%; display:block; }}
h1,h2 {{ margin:0 0 10px; }}
p {{ color:#d8d8d8; }}
</style>
</head>
<body>
<header><h1>Leatt Premium BI Redesign</h1><p>Executive-ready layouts rebuilt from dashboard design best practices.</p></header>
<main>{cards}</main>
</body>
</html>""",
        encoding="utf-8",
    )
    return path


def copy_to_repo(paths: list[Path]) -> None:
    if not REPO.exists():
        return
    for folder in [REPO / "docs", REPO / "artifacts" / "reports", REPO / "artifacts" / "evidence_images" / "premium_design"]:
        folder.mkdir(parents=True, exist_ok=True)
    for path in paths:
        if path.suffix.lower() in {".md", ".html"}:
            shutil.copy2(path, REPO / "docs" / path.name)
        elif path.suffix.lower() == ".pdf":
            shutil.copy2(path, REPO / "artifacts" / "reports" / path.name)
        elif path.suffix.lower() == ".png":
            shutil.copy2(path, REPO / "artifacts" / "evidence_images" / "premium_design" / path.name)
    shutil.copy2(ROOT / "work" / "create_premium_report_pack.py", REPO / "src" / "create_premium_report_pack.py")


def main() -> None:
    data = load_data()
    images = [
        premium_dashboard(data, PREMIUM / "premium_executive_command_view.png"),
        growth_dashboard(data, PREMIUM / "premium_growth_ai_seo_view.png"),
        ml_governance_dashboard(data, PREMIUM / "premium_ml_governance_view.png"),
    ]
    outputs = [
        *images,
        design_system_md(),
        write_pdf(images, "Leatt Premium Executive BI Report", OUT / "leatt_premium_executive_bi_report.pdf"),
        write_ebook(images, data, OUT / "leatt_premium_bi_storybook.pdf"),
        html_index(images),
    ]
    copy_to_repo(outputs)
    print("Premium report pack complete:")
    for p in outputs:
        print(f"- {p} ({p.stat().st_size / (1024 * 1024):.2f} MB)")


if __name__ == "__main__":
    main()
