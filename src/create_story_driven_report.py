from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

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

RED = "#d71920"
INK = "#171717"
MUTED = "#5f646a"
LINE = "#ded8ce"


def money(value: float) -> str:
    if abs(value) >= 1_000_000_000:
        return f"R{value / 1_000_000_000:.2f}bn"
    if abs(value) >= 1_000_000:
        return f"R{value / 1_000_000:.1f}m"
    return f"R{value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


def load_story_context() -> dict:
    conn = sqlite3.connect(SQLITE)
    total_revenue, total_margin, total_returns, orders, rows = conn.execute(
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
    top_categories = pd.read_sql("select * from agg_category order by net_revenue_zar desc limit 5", conn)
    top_channels = pd.read_sql("select * from agg_channel order by net_revenue_zar desc", conn)
    monthly = pd.read_sql("select * from agg_monthly order by month", conn)
    conn.close()
    return {
        "total_revenue": total_revenue,
        "total_margin": total_margin,
        "total_returns": total_returns,
        "orders": orders,
        "rows": rows,
        "top_categories": top_categories,
        "top_channels": top_channels,
        "monthly": monthly,
        "initiatives": pd.read_csv(OUT / "leatt_prioritized_business_initiatives.csv"),
        "signals": pd.read_csv(OUT / "leatt_decision_signal_rules.csv"),
        "seo": pd.read_csv(OUT / "leatt_ai_seo_roadmap.csv"),
    }


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor(INK), fontSize=30, leading=34, spaceAfter=14))
    styles.add(ParagraphStyle(name="CoverSub", parent=styles["BodyText"], alignment=TA_CENTER, textColor=colors.HexColor(MUTED), fontSize=13, leading=18))
    styles.add(ParagraphStyle(name="Chapter", parent=styles["Heading1"], textColor=colors.HexColor(RED), fontSize=19, leading=22, spaceBefore=8, spaceAfter=10))
    styles.add(ParagraphStyle(name="Pull", parent=styles["BodyText"], textColor=colors.HexColor(INK), fontSize=14, leading=19, leftIndent=0.4 * cm, rightIndent=0.4 * cm, spaceBefore=10, spaceAfter=10))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], textColor=colors.HexColor(MUTED), fontSize=8.5, leading=11))
    return styles


def table_style(header=INK):
    return [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor(LINE)),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]


def story_pages(ctx: dict, styles) -> list:
    revenue = ctx["total_revenue"]
    margin = ctx["total_margin"]
    returns = ctx["total_returns"]
    margin_rate = margin / revenue
    return_rate = returns / revenue
    hero = ctx["top_categories"].iloc[0]
    initiatives = ctx["initiatives"].sort_values("priority_score", ascending=False).head(5)
    signals = ctx["signals"].head(6)
    seo = ctx["seo"]

    story = [
        Paragraph("Leatt Ecommerce Intelligence Story", styles["CoverTitle"]),
        Paragraph("From public ecommerce data to Fabric Lakehouse, Power BI, ML, AI SEO and business decisions", styles["CoverSub"]),
        Spacer(1, 0.8 * cm),
        Table(
            [
                ["Built", "Proof"],
                ["2,000,000 transaction lines", "Fabric / OneLake upload proof"],
                [money(revenue) + " modeled revenue", "Power BI semantic model and reports"],
                [pct(margin_rate) + " gross margin rate", "Decision intelligence and KPI rationale"],
                [pct(return_rate) + " return leakage", "ML return-risk watchlist"],
                ["Fabric F2 paused after export", "Cost-control handover"],
            ],
            colWidths=[7 * cm, 8 * cm],
            style=table_style(),
        ),
        PageBreak(),
        Paragraph("1. The Business Question", styles["Chapter"]),
        Paragraph(
            "The story starts with a practical executive question: if Leatt had to run a modern ecommerce intelligence program, what data would leadership need to protect growth, margin and customer experience?",
            styles["BodyText"],
        ),
        Paragraph(
            "The answer is not just a dashboard. The business needs a governed operating rhythm: extract product and transaction signals, model them in Fabric, expose trusted KPIs in Power BI, use ML to identify leakage, and turn the signals into owner-led actions.",
            styles["BodyText"],
        ),
        Paragraph(
            f"The modeled estate is large enough to feel enterprise-grade: {ctx['rows']:,} transaction rows, {money(revenue)} revenue and {money(margin)} gross margin.",
            styles["Pull"],
        ),
        PageBreak(),
        Paragraph("2. What The Data Says", styles["Chapter"]),
        Paragraph(
            f"The strongest commercial signal is concentration. {hero['category']} is the hero category, contributing {money(hero['net_revenue_zar'])}. That is good news because it gives leadership a clear growth engine; it is also a risk because availability, SEO visibility and return leakage in that category matter disproportionately.",
            styles["BodyText"],
        ),
        Paragraph(
            f"Margins are attractive at {pct(margin_rate)}, but returns absorb {pct(return_rate)} of modeled revenue. That makes return reduction one of the cleanest business cases in the pack.",
            styles["BodyText"],
        ),
        Table(
            [["Category", "Revenue", "Gross Margin", "Return Rate"]]
            + [
                [r.category, money(r.net_revenue_zar), money(r.gross_margin_zar), pct(r.return_amount_zar / r.net_revenue_zar)]
                for r in ctx["top_categories"].itertuples(index=False)
            ],
            colWidths=[5 * cm, 4 * cm, 4 * cm, 3 * cm],
            style=table_style(),
        ),
        PageBreak(),
        Paragraph("3. What We Learned", styles["Chapter"]),
        Paragraph(
            "The main learning is that ecommerce BI should not stop at reporting revenue. Revenue only becomes useful when it is reconciled with margin, returns, channel efficiency, stock availability and content quality.",
            styles["BodyText"],
        ),
        Paragraph(
            "The live storefront evidence points to Shopify rather than SAP Commerce/Hybris. That changes the architecture story: Shopify/public catalog signals can sit upstream, while SAP Business One or SAP BW fits downstream as finance, inventory, VAT and reconciliation data.",
            styles["BodyText"],
        ),
        Paragraph(
            "dbt is optional for this proof. It would be useful later for versioned SQL transformations and CI tests, but Fabric Data Factory, Lakehouse files, notebooks/scripts and Power BI are enough to demonstrate the senior BI workflow.",
            styles["BodyText"],
        ),
        PageBreak(),
        Paragraph("4. What Leadership Should Do Next", styles["Chapter"]),
        Paragraph(
            "The project now turns insights into management actions. Each action has a rationale, owner, value estimate and next step.",
            styles["BodyText"],
        ),
        Table(
            [["Priority", "Initiative", "Value", "Owner", "Next step"]]
            + [
                [str(r.priority_score), r.initiative, str(r.estimated_value), r.owner, r.next_step]
                for r in initiatives.itertuples(index=False)
            ],
            colWidths=[1.8 * cm, 4.8 * cm, 2.8 * cm, 3 * cm, 6.2 * cm],
            style=table_style(),
        ),
        PageBreak(),
        Paragraph("5. How The Power BI Report Should Be Read", styles["Chapter"]),
        Paragraph(
            "The report is designed as a sequence, not a menu. Start with the executive command view, move to marketing and AI SEO, then finish with ML/governance. This follows the logic of the business: first understand performance, then growth levers, then risk and auditability.",
            styles["BodyText"],
        ),
    ]

    for image in [
        OUT / "premium_design" / "premium_executive_command_view.png",
        OUT / "premium_design" / "premium_growth_ai_seo_view.png",
        OUT / "premium_design" / "premium_ml_governance_view.png",
    ]:
        if image.exists():
            story += [Spacer(1, 0.3 * cm), PdfImage(str(image), width=18.2 * cm, height=10.25 * cm)]

    story += [
        PageBreak(),
        Paragraph("6. Signal Rules And Governance", styles["Chapter"]),
        Paragraph(
            "A senior BI solution should say what happens when a metric moves. The signal rules below make the report operational.",
            styles["BodyText"],
        ),
        Table(
            [["Signal", "Reading", "Rule", "Owner", "Decision"]]
            + [
                [r.signal, r.current_reading, r.threshold_or_rule, r.owner, r.recommended_decision]
                for r in signals.itertuples(index=False)
            ],
            colWidths=[3.3 * cm, 2.7 * cm, 5.2 * cm, 2.6 * cm, 5.2 * cm],
            style=table_style(),
        ),
        PageBreak(),
        Paragraph("7. AI SEO: The New Growth Layer", styles["Chapter"]),
        Paragraph(
            "The latest search direction is clear: AI search visibility depends on crawlable pages, complete product data, structured data, Merchant Center feed quality, useful content and measurable share of voice. This is not separate from BI; it belongs in the same growth model.",
            styles["BodyText"],
        ),
        Table(
            [["Timeframe", "Workstream", "Action", "Outcome"]]
            + [[r.timeframe, r.workstream, r.action, r.expected_outcome] for r in seo.itertuples(index=False)],
            colWidths=[2.3 * cm, 3.6 * cm, 7 * cm, 5.5 * cm],
            style=table_style(),
        ),
        PageBreak(),
        Paragraph("8. The Portfolio Message", styles["Chapter"]),
        Paragraph(
            "This project demonstrates the full senior BI developer arc: source research, data engineering, Fabric/Fabric capacity use, Lakehouse upload, semantic modeling, Power BI report creation, ML, governance, SAP/accounting thinking, AI SEO and Git proof.",
            styles["BodyText"],
        ),
        Paragraph(
            "The most important message for an interviewer is this: the work is not just technically broad. It is commercially literate. Every metric has a reason, every report has an audience, and every insight has a next action.",
            styles["Pull"],
        ),
        Paragraph(
            f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}. Fabric capacity was paused after report export testing to protect Azure credit.",
            styles["Small"],
        ),
    ]
    return story


def build_pdf(path: Path, landscape_mode: bool = False) -> Path:
    ctx = load_story_context()
    styles = make_styles()
    pagesize = landscape(A4) if landscape_mode else A4
    doc = SimpleDocTemplate(str(path), pagesize=pagesize, rightMargin=1.4 * cm, leftMargin=1.4 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    doc.build(story_pages(ctx, styles))
    return path


def write_story_md(path: Path) -> Path:
    ctx = load_story_context()
    revenue = ctx["total_revenue"]
    margin = ctx["total_margin"]
    returns = ctx["total_returns"]
    hero = ctx["top_categories"].iloc[0]
    initiatives = ctx["initiatives"].sort_values("priority_score", ascending=False).head(5)
    md_actions = "\n".join(f"- {r.initiative}: {r.estimated_value}; owner {r.owner}; next step: {r.next_step}" for r in initiatives.itertuples(index=False))
    path.write_text(
        f"""# Leatt Ecommerce Intelligence Story

## The Business Question

If Leatt had to run a modern ecommerce intelligence program, what would leadership need to protect growth, margin and customer experience?

## What The Data Says

- Modeled revenue: {money(revenue)}
- Modeled gross margin: {money(margin)}
- Return leakage: {pct(returns / revenue)}
- Hero category: {hero['category']} at {money(hero['net_revenue_zar'])}

## What We Learned

Revenue alone is not enough. The useful story connects revenue to margin, returns, channel efficiency, product availability, SEO content quality, finance reconciliation and governance.

The storefront evidence points to Shopify, while SAP Business One or SAP BW fits as the finance and inventory source. SAP Commerce/Hybris is possible in a larger enterprise architecture, but it is not required for this storefront proof.

## What Leadership Should Do Next

{md_actions}

## Portfolio Message

This is not only a dashboard build. It is an end-to-end BI operating model: source extraction, Fabric Lakehouse, Power BI semantic layer, ML, AI SEO, SAP/accounting governance, Git proof and cost control.
""",
        encoding="utf-8",
    )
    return path


def copy_to_repo(paths: list[Path]) -> None:
    if not REPO.exists():
        return
    for folder in [REPO / "docs", REPO / "artifacts" / "reports"]:
        folder.mkdir(parents=True, exist_ok=True)
    for p in paths:
        if p.suffix.lower() == ".md":
            shutil.copy2(p, REPO / "docs" / p.name)
        elif p.suffix.lower() == ".pdf":
            shutil.copy2(p, REPO / "artifacts" / "reports" / p.name)
    shutil.copy2(ROOT / "work" / "create_story_driven_report.py", REPO / "src" / "create_story_driven_report.py")


def main() -> None:
    outputs = [
        build_pdf(OUT / "leatt_story_driven_ebook.pdf", landscape_mode=False),
        build_pdf(OUT / "leatt_story_driven_executive_report.pdf", landscape_mode=True),
        write_story_md(OUT / "leatt_story_driven_report_narrative.md"),
    ]
    copy_to_repo(outputs)
    print("Story-driven report pack complete:")
    for p in outputs:
        print(f"- {p} ({p.stat().st_size / (1024 * 1024):.2f} MB)")


if __name__ == "__main__":
    main()
