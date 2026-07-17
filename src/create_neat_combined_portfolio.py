from __future__ import annotations

import csv
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
REPO = OUT / "leatt-fabric-bi-ml-git-proof"
REPORTS = REPO / "artifacts" / "reports"
DOCS = REPO / "docs"
EVIDENCE = REPO / "artifacts" / "evidence_images"
DATA = REPO / "artifacts" / "data_samples"
FINAL = OUT / "LEATT_GROWTH_OS_FINAL_DELIVERY"
TMP = OUT / "_combined_portfolio_tmp"

INK = "#141414"
RED = "#d71920"
MUTED = "#5f646a"
PAPER = "#f7f4ef"


@dataclass(frozen=True)
class PortfolioItem:
    title: str
    source: Path
    destination_group: str
    reason: str
    include_in_master_pdf: bool = True


PDF_ITEMS = [
    PortfolioItem("Start Here: Leatt Growth OS Case Study", REPORTS / "leatt_growth_os_case_study.pdf", "01_MASTER_STORY", "Lead visual case study and best first-read artifact."),
    PortfolioItem("Story-Driven Executive Report", REPORTS / "leatt_story_driven_executive_report.pdf", "01_MASTER_STORY", "Board-style summary of the commercial story."),
    PortfolioItem("Premium Executive BI Report", REPORTS / "leatt_premium_executive_bi_report.pdf", "02_POWERBI_AND_DASHBOARDS", "Polished Power BI-style report pages."),
    PortfolioItem("Power BI ML Report Screenshots", REPORTS / "leatt_powerbi_ml_report_screenshots.pdf", "02_POWERBI_AND_DASHBOARDS", "Static Power BI/ML report evidence."),
    PortfolioItem("Fabric ERD And Deployment Report", REPORTS / "leatt_erd_and_fabric_deployment_report.pdf", "03_AZURE_FABRIC_DATA_FACTORY_PROOF", "ERD, Lakehouse/Warehouse and Fabric architecture proof."),
    PortfolioItem("Evidence Addendum", REPORTS / "evidence_addendum.pdf", "03_AZURE_FABRIC_DATA_FACTORY_PROOF", "Screenshot-based proof pack."),
    PortfolioItem("Accounting, Governance And SAP Report", REPORTS / "leatt_accounting_governance_sap_report.pdf", "04_ACCOUNTING_SAP_GOVERNANCE", "Accounting reconciliation, data audit and SAP fit."),
    PortfolioItem("AI Commerce Command Center Report", REPORTS / "ai_commerce_command_center_report.pdf", "05_AI_ML_SEO_MARKETING", "AI agents, operating model and automation layer."),
    PortfolioItem("Growth, AI And Marketing Report", REPORTS / "leatt_growth_ai_marketing_report.pdf", "05_AI_ML_SEO_MARKETING", "A/B testing, marketing, competitor and growth analysis."),
    PortfolioItem("KPI And Report Rationale", REPORTS / "leatt_kpi_and_report_rationale.pdf", "06_DECISION_INTELLIGENCE", "Explains why each KPI exists and what action it drives."),
    PortfolioItem("Decision Intelligence Playbook", REPORTS / "leatt_decision_intelligence_playbook.pdf", "06_DECISION_INTELLIGENCE", "Signal rules, owners and next-best actions."),
    PortfolioItem("AI SEO Best Practices Playbook", REPORTS / "leatt_ai_seo_best_practices_playbook.pdf", "05_AI_ML_SEO_MARKETING", "AI-era SEO roadmap and best practices."),
    PortfolioItem("Final Executive Portfolio Dossier", REPORTS / "leatt_final_executive_portfolio_dossier.pdf", "07_ARCHIVE_SUPPORTING_REPORTS", "Legacy final dossier retained as supporting context."),
]

NON_PDF_ITEMS = [
    PortfolioItem("Master Excel Command Center", REPORTS / "leatt_ecommerce_bi_ml_ai_command_center_master.xlsx", "08_EXCEL_AND_DATA", "Excel workbook with BI, ML, Fabric and story sheets.", False),
    PortfolioItem("Fabric ERD Deployment Workbook", REPORTS / "leatt_ecommerce_bi_ml_fabric_erd_deployment_master.xlsx", "08_EXCEL_AND_DATA", "Workbook with ERD and deployment tabs.", False),
    PortfolioItem("Finance Governance Workbook", REPORTS / "leatt_ecommerce_bi_ml_finance_governance_master.xlsx", "08_EXCEL_AND_DATA", "Workbook for reconciliation, SAP mapping and governance.", False),
    PortfolioItem("Board Presentation", REPORTS / "leatt_fabric_bi_ml_board_presentation.pptx", "09_PRESENTATION", "PowerPoint-compatible board deck.", False),
]

DOC_ITEMS = [
    DOCS / "leatt_growth_os_case_study.md",
    DOCS / "powerbi_report_creation_proof.md",
    DOCS / "fabric_onelake_upload_proof.md",
    DOCS / "fabric_push_million_rows_runbook.md",
    DOCS / "SAP_ACCOUNTING_GOVERNANCE_INTEGRATION.md",
    DOCS / "Ecommerce_platform_research.md",
    DOCS / "ECommerce_platform_research.md",
    DOCS / "ECOMMERCE_PLATFORM_RESEARCH.md",
    DOCS / "AZURE_FABRIC_EXPORT_TO_GIT.md",
    DOCS / "DATABRICKS_TO_FABRIC_TRANSFERABILITY.md",
]


def ensure_dirs() -> None:
    for root in [FINAL, TMP, REPO / "docs", REPORTS, DATA]:
        root.mkdir(parents=True, exist_ok=True)
    for group in [
        "00_START_HERE",
        "01_MASTER_STORY",
        "02_POWERBI_AND_DASHBOARDS",
        "03_AZURE_FABRIC_DATA_FACTORY_PROOF",
        "04_ACCOUNTING_SAP_GOVERNANCE",
        "05_AI_ML_SEO_MARKETING",
        "06_DECISION_INTELLIGENCE",
        "07_ARCHIVE_SUPPORTING_REPORTS",
        "08_EXCEL_AND_DATA",
        "09_PRESENTATION",
        "10_SOURCE_AND_GIT_PROOF",
    ]:
        (FINAL / group).mkdir(parents=True, exist_ok=True)


def write_pdf_page(path: Path, title: str, subtitle: str, body: list[str]) -> Path:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Hero", parent=styles["Title"], fontSize=30, leading=34, textColor=colors.HexColor(INK), spaceAfter=12))
    styles.add(ParagraphStyle(name="Sub", parent=styles["BodyText"], fontSize=13, leading=18, textColor=colors.HexColor(MUTED), spaceAfter=20))
    styles.add(ParagraphStyle(name="BodyLarge", parent=styles["BodyText"], fontSize=12, leading=17, textColor=colors.HexColor(INK), spaceAfter=10))
    doc = SimpleDocTemplate(str(path), pagesize=landscape(A4), rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm)
    story = [
        Paragraph(title, styles["Hero"]),
        Paragraph(subtitle, styles["Sub"]),
        Spacer(1, 0.5 * cm),
    ]
    for line in body:
        story.append(Paragraph(line, styles["BodyLarge"]))
    doc.build(story)
    return path


def build_master_pdf(master_path: Path) -> Path:
    writer = PdfWriter()
    cover = write_pdf_page(
        TMP / "00_cover.pdf",
        "Leatt Growth OS: Combined Portfolio",
        "One neat BI + ML + Fabric case study, with supporting proof ordered behind the story.",
        [
            "Read this as a single operating system: storefront evidence, Fabric data engine, Power BI control room, ML leakage control, AI SEO growth loop, SAP/accounting governance and 90-day action plan.",
            "The first section is the strongest narrative artifact. The remaining sections are supporting evidence, technical proof and audit trail.",
            f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}.",
        ],
    )
    for page in PdfReader(str(cover)).pages:
        writer.add_page(page)
    writer.add_outline_item("Portfolio Cover", 0)

    for item in PDF_ITEMS:
        if not item.include_in_master_pdf or not item.source.exists():
            continue
        divider = write_pdf_page(TMP / f"divider_{len(writer.pages):03d}.pdf", item.title, item.reason, [f"Source file: {item.source.name}"])
        start_page = len(writer.pages)
        for page in PdfReader(str(divider)).pages:
            writer.add_page(page)
        writer.add_outline_item(item.title, start_page)
        for page in PdfReader(str(item.source)).pages:
            writer.add_page(page)

    with master_path.open("wb") as f:
        writer.write(f)
    return master_path


def copy_item(item: PortfolioItem) -> str:
    if not item.source.exists():
        return "missing"
    dest = FINAL / item.destination_group / item.source.name
    shutil.copy2(item.source, dest)
    return str(dest.relative_to(FINAL))


def write_start_here(master_pdf_name: str, manifest_name: str) -> Path:
    path = OUT / "START_HERE_LEATT_GROWTH_OS.md"
    path.write_text(
        f"""# START HERE: Leatt Growth OS

This is the neat combined delivery for the Leatt BI, ML, Fabric and ecommerce analytics portfolio.

## Best Reading Order

1. Open `{master_pdf_name}` first. It combines the story and the evidence in the correct order.
2. If you only have five minutes, read `01_MASTER_STORY/leatt_growth_os_case_study.pdf`.
3. For Azure/Fabric/Data Factory proof, open `03_AZURE_FABRIC_DATA_FACTORY_PROOF`.
4. For Power BI proof, open `02_POWERBI_AND_DASHBOARDS`.
5. For SAP/accounting/governance, open `04_ACCOUNTING_SAP_GOVERNANCE`.
6. For Excel, source samples and workbooks, open `08_EXCEL_AND_DATA`.

## What The Project Proves

- Extracted and structured public ecommerce/product evidence.
- Generated and modeled 2,000,000 transaction lines.
- Built a BI-ready dimensional model and ERD.
- Created Fabric/Data Factory/OneLake proof and Power BI report proof.
- Added ML return-risk, A/B testing, marketing ROI, competitor and AI SEO analysis.
- Added SAP Business One/BW positioning, reconciliation, audit and governance thinking.
- Packaged the work for GitHub proof and interview review.

## Important Note

The live Power BI item was created in the Fabric/Power BI workspace and bound to the semantic model. Some service export screenshots rendered Power BI loading/sign-in screens, so the package uses the API proof plus static report screenshots instead of pretending those blank exports were visual proof.

Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}.
""",
        encoding="utf-8",
    )
    shutil.copy2(path, FINAL / "00_START_HERE" / path.name)
    shutil.copy2(path, REPO / "docs" / path.name)
    return path


def write_html_index(master_pdf_name: str, rows: list[dict[str, str]]) -> Path:
    path = OUT / "leatt_growth_os_combined_index.html"
    cards = "\n".join(
        f"""<article>
  <h2>{row['title']}</h2>
  <p>{row['reason']}</p>
  <a href="{row['final_delivery_path']}">{row['final_delivery_path']}</a>
</article>"""
        for row in rows
        if row["status"] == "included"
    )
    path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Leatt Growth OS Combined Delivery</title>
<style>
body {{ margin:0; font-family: Arial, sans-serif; background:{PAPER}; color:{INK}; }}
header {{ background:{INK}; color:white; padding:40px 52px; border-bottom:7px solid {RED}; }}
main {{ max-width:1120px; margin:0 auto; padding:28px; }}
.lead {{ background:white; border:1px solid #ded8ce; padding:24px; margin-bottom:20px; }}
article {{ background:white; border:1px solid #ded8ce; padding:18px; margin:14px 0; }}
h1,h2 {{ margin:0 0 8px; }}
p {{ color:{MUTED}; line-height:1.45; }}
a {{ color:{RED}; font-weight:bold; text-decoration:none; }}
</style>
</head>
<body>
<header><h1>Leatt Growth OS Combined Delivery</h1><p>One ordered story, with supporting proof behind it.</p></header>
<main>
<section class="lead"><h2>Start With The Master PDF</h2><p><a href="{master_pdf_name}">{master_pdf_name}</a></p></section>
{cards}
</main>
</body>
</html>""",
        encoding="utf-8",
    )
    shutil.copy2(path, FINAL / "00_START_HERE" / path.name)
    shutil.copy2(path, REPO / "docs" / path.name)
    return path


def write_manifest(rows: list[dict[str, str]]) -> Path:
    path = OUT / "leatt_growth_os_combined_manifest.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "group", "source", "final_delivery_path", "reason", "status"])
        writer.writeheader()
        writer.writerows(rows)
    DATA.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, DATA / path.name)
    shutil.copy2(path, FINAL / "00_START_HERE" / path.name)
    return path


def copy_supporting_docs() -> None:
    for doc in DOC_ITEMS:
        if doc.exists():
            shutil.copy2(doc, FINAL / "10_SOURCE_AND_GIT_PROOF" / doc.name)
    if EVIDENCE.exists():
        dest = FINAL / "03_AZURE_FABRIC_DATA_FACTORY_PROOF" / "evidence_images"
        dest.mkdir(parents=True, exist_ok=True)
        for p in EVIDENCE.rglob("*"):
            if p.is_file():
                rel = p.relative_to(EVIDENCE)
                (dest / rel.parent).mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dest / rel)


def update_repo_readme() -> None:
    readme = REPO / "README.md"
    text = readme.read_text(encoding="utf-8")
    block = """## Start Here

- `artifacts/reports/leatt_growth_os_master_portfolio.pdf` - combined master dossier. Open this first.
- `docs/START_HERE_LEATT_GROWTH_OS.md` - clean reading order and proof guide.
- `docs/leatt_growth_os_combined_index.html` - clickable local index for the curated package.
- `artifacts/data_samples/leatt_growth_os_combined_manifest.csv` - manifest of the curated final delivery.

"""
    if "## Start Here\n\n- `artifacts/reports/leatt_growth_os_master_portfolio.pdf`" not in text:
        text = text.replace("## Final deliverables\n\n", block + "## Final deliverables\n\n")
    if "- `artifacts/reports/leatt_growth_os_master_portfolio.pdf` - combined master dossier." not in text:
        text = text.replace(
            "## Final deliverables\n\n",
            "## Final deliverables\n\n- `artifacts/reports/leatt_growth_os_master_portfolio.pdf` - combined master dossier.\n",
        )
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    master = OUT / "leatt_growth_os_master_portfolio.pdf"
    build_master_pdf(master)
    shutil.copy2(master, REPORTS / master.name)
    shutil.copy2(master, FINAL / "00_START_HERE" / master.name)

    rows: list[dict[str, str]] = []
    for item in [*PDF_ITEMS, *NON_PDF_ITEMS]:
        final_path = copy_item(item)
        rows.append(
            {
                "title": item.title,
                "group": item.destination_group,
                "source": str(item.source),
                "final_delivery_path": final_path,
                "reason": item.reason,
                "status": "included" if final_path != "missing" else "missing",
            }
        )

    manifest = write_manifest(rows)
    start = write_start_here(master.name, manifest.name)
    html = write_html_index(master.name, rows)
    copy_supporting_docs()
    shutil.copy2(Path(__file__), REPO / "src" / "create_neat_combined_portfolio.py")
    shutil.copy2(Path(__file__), FINAL / "10_SOURCE_AND_GIT_PROOF" / "create_neat_combined_portfolio.py")
    update_repo_readme()

    print("Combined portfolio complete:")
    for p in [master, start, html, manifest, FINAL]:
        print(f"- {p}")


if __name__ == "__main__":
    main()
