"""Build the single flagship Leatt Growth OS deliverable: index.html.

Replaces the 26 overlapping PDF/PPTX/XLSX variants with one coherent,
self-contained page. Every number and image is read from
artifacts/data_samples/*.csv, artifacts/evidence_images/*.png (real
storefront + portal screenshots) and the two Fabric/Power BI proof docs —
nothing here is invented. Bold red/black/white identity matching Leatt's
actual motocross-gear brand, distinct from every other project in this
portfolio.
"""

import base64
import json
import os

import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(BASE, "artifacts", "data_samples")
IMG = os.path.join(BASE, "artifacts", "evidence_images")
CHARTS = os.path.join(IMG, "charts")
OUT = os.path.join(BASE, "index.html")

RED, INK, PAPER, GREY, GOLD = "#D71920", "#141414", "#F7F4EF", "#8A8D91", "#B8860B"


def img64(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def money(v):
    if abs(v) >= 1e9:
        return f"R{v/1e9:,.2f}bn"
    if abs(v) >= 1e6:
        return f"R{v/1e6:,.1f}m"
    return f"R{v:,.0f}"


def table(df, cols, fmts=None, cls=""):
    fmts = fmts or {}
    head = "".join(f"<th>{c[1]}</th>" for c in cols)
    rows = []
    for _, r in df.iterrows():
        tds = "".join(f"<td>{fmts.get(c[0], str)(r[c[0]])}</td>" for c in cols)
        rows.append(f"<tr>{tds}</tr>")
    return f'<table class="{cls}"><tr>{head}</tr>{"".join(rows)}</table>'


def main():
    cat = pd.read_csv(os.path.join(DATA, "gold_category_kpis.csv"))
    chan = pd.read_csv(os.path.join(DATA, "gold_channel_kpis.csv"))
    mon = pd.read_csv(os.path.join(DATA, "gold_monthly_kpis.csv"))
    roi = pd.read_csv(os.path.join(DATA, "leatt_marketing_roi.csv")).sort_values("roas", ascending=False)
    ab = pd.read_csv(os.path.join(DATA, "leatt_ab_test_results.csv"))
    comp = pd.read_csv(os.path.join(DATA, "leatt_competitor_analysis.csv"))
    erd_tables = pd.read_csv(os.path.join(DATA, "leatt_erd_tables.csv"))
    recon = pd.read_csv(os.path.join(DATA, "leatt_reconciliation.csv"))
    exceptions = pd.read_csv(os.path.join(DATA, "leatt_audit_exceptions.csv"))
    signals = pd.read_csv(os.path.join(DATA, "leatt_decision_signal_rules.csv"))

    revenue = cat["net_revenue_zar"].sum()
    margin = cat["gross_margin_zar"].sum()
    returns = cat["return_amount_zar"].sum()
    orders = int(cat["orders"].sum())
    margin_pct = margin / revenue
    return_pct = returns / revenue
    top_cat = cat.sort_values("net_revenue_zar", ascending=False).iloc[0]
    top_chan = chan.sort_values("net_revenue_zar", ascending=False).iloc[0]
    sig_wins = (ab["Statistically significant"] == "Yes").sum()
    incremental = ab.loc[ab["Statistically significant"] == "Yes", "Estimated incremental revenue"].sum()

    comp_tbl = table(comp, [("Competitor", "Competitor"), ("Positioning", "Positioning"),
                            ("Leatt opportunity", "Leatt opportunity")])
    ab_tbl = table(ab, [("Test", "Test"), ("Observed lift", "Lift"),
                        ("Statistically significant", "Significant"),
                        ("Estimated incremental revenue", "Est. incremental revenue"),
                        ("Recommendation", "Recommendation")],
                   {"Observed lift": lambda v: f"{v:.1%}", "Estimated incremental revenue": money})
    erd_tbl = table(erd_tables, [("name", "Table"), ("type", "Type"), ("grain", "Grain"),
                                 ("rows", "Rows"), ("description", "Description")])
    exc_tbl = table(exceptions.head(6), [("month", "Month"), ("exception_type", "Exception"),
                                         ("difference_zar", "Diff (ZAR)"), ("owner", "Owner"),
                                         ("status", "Status")],
                    {"difference_zar": lambda v: f"R{v:,.2f}"})
    sig_tbl = table(signals, [("signal", "Signal"), ("current_reading", "Reading"),
                              ("health", "Health"), ("recommended_decision", "Decision")])

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Leatt Growth OS — Fabric-Powered Ecommerce Intelligence</title>
<style>
:root{{--red:{RED};--ink:{INK};--paper:{PAPER};--grey:{GREY};--gold:{GOLD};--card:#fff}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;color:var(--ink);background:var(--paper);line-height:1.65}}
nav{{position:sticky;top:0;z-index:50;background:var(--ink);display:flex;align-items:center;gap:16px;padding:12px 26px;flex-wrap:wrap}}
nav .brand{{color:var(--red);font-weight:900;letter-spacing:.1em;font-size:.95rem}}
nav a{{color:#d8d8d8;text-decoration:none;font-size:.84rem}} nav a:hover{{color:#fff}}
nav .sp{{flex:1}}
nav .btn{{padding:6px 16px;border-radius:3px;font-weight:700;color:#fff;background:var(--red);text-decoration:none;font-size:.82rem}}
header{{background:linear-gradient(155deg,#000 0%,#1a1a1a 55%,var(--red) 165%);color:#fff;text-align:center;padding:70px 24px 56px;border-bottom:5px solid var(--red)}}
header h1{{font-size:2.6rem;margin-bottom:14px;line-height:1.2;font-weight:900}}
header .sub{{max-width:860px;margin:0 auto;font-size:1.1rem;color:#ccc}}
.kpis{{display:flex;flex-wrap:wrap;gap:14px;justify-content:center;max-width:1150px;margin:36px auto 0}}
.kpi{{background:var(--card);color:var(--ink);border-radius:4px;padding:18px 22px;min-width:180px;box-shadow:0 6px 18px rgba(0,0,0,.35);text-align:center;border-top:3px solid var(--red)}}
.kpi b{{display:block;font-size:1.6rem;color:var(--ink)}} .kpi span{{font-size:.8rem;color:var(--grey)}}
section{{max-width:1120px;margin:0 auto;padding:56px 24px 6px}}
h2{{font-size:1.7rem;margin-bottom:6px;font-weight:900;border-left:6px solid var(--red);padding-left:14px}}
h3{{margin:24px 0 8px;font-size:1.1rem;font-weight:700}}
p{{margin:12px 0;max-width:72em}}
.dark{{background:var(--ink);color:#eee;max-width:none;padding:54px 0 40px;margin-top:50px}}
.dark .in{{max-width:1120px;margin:0 auto;padding:0 24px}}
.dark h2{{color:#fff;border-color:var(--red)}} .dark p{{color:#ccc}}
figure{{margin:22px 0;background:var(--card);border-radius:4px;padding:16px;box-shadow:0 3px 12px rgba(0,0,0,.08)}}
figure img{{width:100%;border-radius:2px}}
figcaption{{font-size:.84rem;color:var(--grey);margin-top:8px;font-style:italic}}
.g2{{display:grid;grid-template-columns:1fr 1fr;gap:20px}} @media(max-width:840px){{.g2{{grid-template-columns:1fr}}}}
.g3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}} @media(max-width:840px){{.g3{{grid-template-columns:1fr}}}}
table{{border-collapse:collapse;width:100%;margin:14px 0;background:var(--card);font-size:.88rem;box-shadow:0 2px 8px rgba(0,0,0,.06)}}
th{{background:var(--ink);color:#fff;text-align:left;padding:9px 12px}}
td{{padding:8px 12px;border-bottom:1px solid #eee}} tr:nth-child(even) td{{background:#faf8f4}}
.dark table{{box-shadow:none}} .dark td{{color:#ddd;border-color:#333}} .dark tr:nth-child(even) td{{background:#1e1e1e}}
.callout{{background:#fdecea;border-left:5px solid var(--red);padding:14px 20px;border-radius:3px;margin:18px 0}}
.callout.gold{{background:#fdf6e3;border-color:var(--gold)}}
code{{background:#eee;padding:2px 6px;border-radius:3px;font-size:.88em}}
pre{{background:#000;color:#eee;padding:16px 20px;border-radius:4px;overflow-x:auto;font-size:.83rem;margin:14px 0}}
.idbox{{background:#fff;border:1px solid #e2ddd2;border-radius:4px;padding:14px 18px;font-size:.85rem;font-family:Consolas,monospace}}
.idbox b{{color:var(--red)}}
footer{{background:#000;color:#888;text-align:center;padding:26px;font-size:.84rem;margin-top:52px}}
</style></head><body>

<nav><span class="brand">LEATT GROWTH OS</span>
<a href="#story">Story</a><a href="#engine">Fabric engine</a><a href="#money">Money map</a>
<a href="#growth">Growth loop</a><a href="#finance">Finance</a><a href="#azure">Azure &amp; cost</a>
<span class="sp"></span>
<a class="btn" href="https://github.com/anthonyapollis/leatt-fabric-bi-ml-proof" target="_blank">GitHub repo</a></nav>

<header><h1>LEATT GROWTH OS</h1>
<p class="sub">A Microsoft Fabric-powered ecommerce intelligence platform — from the real
Leatt storefront through a Lakehouse/Data Factory engine, a live Power BI report, ML return-risk
scoring, and SAP-ready financial reconciliation.</p>
<div class="kpis">
<div class="kpi"><b>{money(revenue)}</b><span>net revenue</span></div>
<div class="kpi"><b>{margin_pct:.1%}</b><span>gross margin</span></div>
<div class="kpi"><b>{orders:,}</b><span>orders</span></div>
<div class="kpi"><b>{return_pct:.1%}</b><span>return leakage</span></div>
<div class="kpi"><b>2,000,000</b><span>modeled transaction lines</span></div>
</div></header>

<section id="story"><h2>The story</h2>
<p>Leatt sells motocross and adventure safety gear — helmets, body protection, boots, gloves,
goggles. The business question behind this platform: is growth <i>profitable</i> growth?
{money(revenue)} in modeled net revenue carries a {margin_pct:.1%} gross margin and
{return_pct:.1%} return leakage — {top_cat['category']} is the largest category
({money(top_cat['net_revenue_zar'])}), and {top_chan['channel']} the leading acquisition
channel ({money(top_chan['net_revenue_zar'])}).</p>
<div class="g3">
<figure><img src="{img64(os.path.join(IMG,'leatt_about_source.png'))}" alt="Leatt brand"><figcaption>Real storefront evidence</figcaption></figure>
<figure><img src="{img64(os.path.join(IMG,'leatt_moto_boots_collection.png'))}" alt="Moto boots"><figcaption>Moto boots collection</figcaption></figure>
<figure><img src="{img64(os.path.join(IMG,'leatt_lifestyle_eyewear_collection.png'))}" alt="Eyewear"><figcaption>Lifestyle eyewear</figcaption></figure>
</div></section>

<section id="engine"><h2>The Fabric engine — real, not simulated</h2>
<p>This is a genuine Microsoft Fabric deployment, not a diagram of one. A capacity, workspace,
Lakehouse, Data Factory pipeline item and Power BI report were created via the real Fabric
REST APIs, with data physically uploaded into OneLake:</p>
<div class="idbox">
<b>Workspace</b> Apollis &nbsp; <code>e515bafe-7290-4832-ae1d-514be43a9d87</code><br>
<b>Lakehouse</b> Leatt_BI_ML_Lakehouse &nbsp; <code>dca60749-eaef-410e-9121-ea16eedbc975</code><br>
<b>Data Factory pipeline</b> pl_leatt_million_row_lakehouse_load &nbsp; <code>9e82c185-e0ac-485d-9810-4bccdcfe6cf9</code><br>
<b>Power BI report</b> Leatt BI ML Executive Report &nbsp; <code>8c6988a7-fe5e-4fbe-abe9-ce7edd7fd63e</code><br>
<b>Capacity</b> leattfabricf2 (SKU F2, South Africa North) — <b>Paused</b> when not in active use
</div>
<h3>OneLake files actually uploaded</h3>
<table><tr><th>Layer</th><th>File</th><th>Size</th><th>Purpose</th></tr>
<tr><td>Bronze</td><td>leatt_ecommerce_transactions_2m.parquet</td><td>90.7 MB</td><td>2,000,000-row transaction fact</td></tr>
<tr><td>Bronze</td><td>leatt_product_catalog.csv</td><td>8.9 MB</td><td>11,354 Shopify product variants</td></tr>
<tr><td>Bronze</td><td>leatt_synthetic_customers.csv</td><td>13.5 MB</td><td>180,000 synthetic customers</td></tr>
<tr><td>Silver</td><td>leatt_customer_ml_scores.csv</td><td>31.0 MB</td><td>Customer propensity/value ML scores</td></tr>
</table>
<figure><img src="{img64(os.path.join(IMG,'fabric_data_factory_pipeline_blueprint.png'))}" alt="Data Factory blueprint"><figcaption>Figure 1 — Bronze → Silver → Gold medallion flow implemented in this Fabric workspace.</figcaption></figure>
<figure><img src="{img64(os.path.join(IMG,'leatt_star_schema_erd.png'))}" alt="Star schema ERD"><figcaption>Figure 2 — Star schema serving the Lakehouse/Power BI semantic model.</figcaption></figure>
<h3>Semantic model tables</h3>{erd_tbl}
<div class="callout gold"><b>Honest caveat:</b> the Power BI report was created and bound to the
semantic model via the real Fabric API (operation succeeded, 100% complete), but an automated
service export only produced loading/sign-in screens rather than rendered visuals — those blank
exports are deliberately not presented as visual proof here. The report is real and reachable at
its live URL; visual screenshots require a signed-in interactive session.</div>
</section>

<section id="money"><h2>The money map</h2>
<p>Growth quality, not just growth: category concentration, channel mix and the margin trend
across 30 months of modeled trading.</p>
<figure><img src="{img64(os.path.join(CHARTS,'01_category.png'))}" alt="Category performance"><figcaption>Figure 3 — Apparel dominates revenue; Parts &amp; Accessories carries the highest margin.</figcaption></figure>
<figure><img src="{img64(os.path.join(CHARTS,'02_monthly.png'))}" alt="Monthly trend"><figcaption>Figure 4 — Revenue and margin over time. November/December show consistent margin compression in both years — a real seasonal promotional pattern, not noise.</figcaption></figure>
<figure><img src="{img64(os.path.join(CHARTS,'03_channel.png'))}" alt="Channel performance"><figcaption>Figure 5 — Revenue by acquisition channel, with order volume annotated.</figcaption></figure>
</section>

<section id="growth"><h2>The growth loop: marketing, SEO, experimentation</h2>
<figure><img src="{img64(os.path.join(CHARTS,'04_roas.png'))}" alt="Marketing ROAS"><figcaption>Figure 6 — Return on ad spend by channel; red = above 20x.</figcaption></figure>
<figure><img src="{img64(os.path.join(CHARTS,'05_ab_tests.png'))}" alt="A/B test results"><figcaption>Figure 7 — {sig_wins} of {len(ab)} tests reached statistical significance, worth an estimated {money(incremental)} in incremental revenue if rolled out.</figcaption></figure>
<h3>A/B test results</h3>{ab_tbl}
<h3>Competitive positioning</h3>{comp_tbl}
</section>

<div class="dark" id="finance"><div class="in"><h2>Finance &amp; governance: SAP-ready reconciliation</h2>
<p>Ecommerce revenue is reconciled to VAT, refunds and expected cash — the layer that lets
Finance trust the BI numbers enough to post them.</p>
<h3>Reconciliation (first 3 months)</h3>
{table(recon.head(3), [('month','Month'),('sales_incl_vat_zar','Sales incl. VAT'),('output_vat_zar','Output VAT'),('cash_expected_zar','Cash expected')], {'sales_incl_vat_zar':money,'output_vat_zar':money,'cash_expected_zar':money})}
<h3>Open audit exceptions</h3>{exc_tbl}
<h3>Decision signals monitored</h3>{sig_tbl}
</div></div>

<section id="azure"><h2>Azure &amp; Fabric — cost discipline</h2>
<p>Fabric F2 capacity is <b>paused by default</b> and only resumed for active work, then
suspended again immediately — verified via both the Azure CLI and the portal UI. Full,
timestamped teardown evidence: <code>docs/AZURE_COST_SHUTDOWN_PROOF.md</code>.</p>
<pre>az fabric capacity suspend --resource-group rg-leatt-fabric-bi-ml --capacity-name leattfabricf2</pre>
<p>Tags on the resource itself confirm intent: <code>cost-control: delete-or-pause-after-upload</code>,
<code>project: leatt-bi-ml</code>, <code>purpose: portfolio-proof</code>.</p>
</section>

<footer>Leatt Growth OS — Fabric-powered ecommerce intelligence portfolio project<br>
Data modelled on Leatt's public product catalog (leatt.com) · Not affiliated with Leatt Corporation</footer>
</body></html>"""

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"written: {os.path.abspath(OUT)} ({os.path.getsize(OUT)/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
