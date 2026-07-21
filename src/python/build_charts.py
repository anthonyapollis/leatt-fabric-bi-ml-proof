"""Render Leatt Growth OS charts from the real gold-layer CSVs.

Sourced from leatt_intelligent_category/channel/monthly/province.csv — the
correctly-scaled gold aggregates that match the actual 2,000,000-row fact
table (verified: sums to R3,994,247,412.56 net revenue, matching
leatt_reconciliation.csv's sales_incl_vat_zar total exactly). The older
gold_*_kpis.csv files are a stale, ~400x-smaller demo sample that was
mistakenly wired into earlier chart/ebook/Excel builds and is no longer
used here.

Bold red/black/white palette matching Leatt's actual brand identity
(motocross/adventure gear) — distinct from every other project in this
portfolio.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(BASE, "artifacts", "data_samples")
OUT = os.path.join(BASE, "artifacts", "evidence_images", "charts")

RED = "#D71920"
INK = "#141414"
PAPER = "#F7F4EF"
GREY = "#8A8D91"
GOLD = "#B8860B"

plt.rcParams.update({
    "figure.facecolor": PAPER, "axes.facecolor": PAPER,
    "axes.edgecolor": "#DDD6CC", "axes.grid": True,
    "grid.color": "#EAE4D9", "grid.linewidth": 0.7,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.titlesize": 14, "axes.titleweight": "bold", "text.color": INK,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
})


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("chart:", name)


def money(x):
    return f"R{x/1e9:,.2f}bn" if abs(x) >= 1e9 else f"R{x/1e6:,.1f}m"


def main():
    cat = pd.read_csv(os.path.join(DATA, "leatt_intelligent_category.csv")).sort_values("net_revenue_zar", ascending=False)
    chan = pd.read_csv(os.path.join(DATA, "leatt_intelligent_channel.csv")).sort_values("net_revenue_zar", ascending=False)
    mon = pd.read_csv(os.path.join(DATA, "leatt_intelligent_monthly.csv")).sort_values("month")
    prov = pd.read_csv(os.path.join(DATA, "leatt_intelligent_province.csv")).sort_values("net_revenue_zar", ascending=False)
    roi = pd.read_csv(os.path.join(DATA, "leatt_marketing_roi.csv")).sort_values("roas", ascending=False)
    ab = pd.read_csv(os.path.join(DATA, "leatt_ab_test_results.csv"))
    forecast = pd.read_csv(os.path.join(DATA, "leatt_revenue_forecast.csv"))
    risk = pd.read_csv(os.path.join(DATA, "leatt_ml_return_risk_scores_sample.csv"))

    # 1. category revenue + margin
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    d = cat.sort_values("net_revenue_zar")
    ax1.barh(d["category"], d["net_revenue_zar"] / 1e9, color=RED)
    ax1.set_xlabel("Net revenue (R billions)")
    ax1.set_title("Revenue by category")
    d2 = cat.sort_values("margin_rate")
    ax2.barh(d2["category"], d2["margin_rate"] * 100, color=INK)
    ax2.axvline(cat["margin_rate"].mean() * 100, color=RED, ls="--", lw=1.5,
                label=f"avg {cat['margin_rate'].mean():.0%}")
    ax2.set_xlabel("Gross margin %")
    ax2.set_title("Margin by category")
    ax2.legend(frameon=False)
    fig.tight_layout()
    save(fig, "01_category.png")

    # 2. monthly revenue + margin trend, with real anomaly-flagged months marked
    fig, ax = plt.subplots(figsize=(12, 5.5))
    x = pd.to_datetime(mon["month"])
    ax.plot(x, mon["net_revenue_zar"] / 1e6, color=RED, lw=2.2, label="Net revenue")
    ax.fill_between(x, mon["net_revenue_zar"] / 1e6, color=RED, alpha=0.08)
    ax2 = ax.twinx()
    ax2.grid(False)
    ax2.plot(x, mon["margin_rate"] * 100, color=INK, lw=1.6, ls="--", label="Margin %")
    ax2.set_ylabel("Margin %")
    margin_pct = mon["margin_rate"] * 100
    ax2.set_ylim(margin_pct.min() - 8, margin_pct.max() + 3)
    flagged = mon["anomaly_flag"] == True
    for xi, yi in zip(x[flagged], margin_pct[flagged]):
        ax2.scatter([xi], [yi], color=GOLD, s=32, zorder=5)
    if flagged.any():
        ax2.annotate("Anomaly-flagged months:\nNov/Dec both years — margin\ndrops ~5.8pts from the ~49.3% norm", xy=(x[flagged].iloc[-1], margin_pct[flagged].iloc[-1]),
                     xytext=(-190, -46), textcoords="offset points", fontsize=8.5, color=GOLD,
                     arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.2))
    ax.set_ylabel("Net revenue (R millions)")
    ax.set_title("Monthly revenue and margin quality")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False)
    fig.autofmt_xdate()
    fig.tight_layout()
    save(fig, "02_monthly.png")

    # 3. channel performance
    fig, ax = plt.subplots(figsize=(11, 5.5))
    d = chan.sort_values("net_revenue_zar")
    ax.barh(d["channel"], d["net_revenue_zar"] / 1e9, color=RED)
    ax.set_xlabel("Net revenue (R billions)")
    ax.set_title("Revenue by acquisition channel")
    fig.tight_layout()
    save(fig, "03_channel.png")

    # 4. marketing ROAS
    fig, ax = plt.subplots(figsize=(11, 5.5))
    d = roi.sort_values("roas")
    colors = [RED if v >= 20 else INK for v in d["roas"]]
    ax.barh(d["channel"], d["roas"], color=colors)
    ax.set_xlabel("Return on ad spend (x)")
    ax.set_title("Marketing ROAS by channel")
    fig.tight_layout()
    save(fig, "04_roas.png")

    # 5. A/B test results
    fig, ax = plt.subplots(figsize=(11, 5.5))
    d = ab.sort_values("Observed lift")
    colors = [RED if s == "Yes" else GREY for s in d["Statistically significant"]]
    ax.barh(d["Test"], d["Observed lift"] * 100, color=colors)
    ax.axvline(0, color=INK, lw=1)
    ax.set_xlabel("Observed conversion lift (%)")
    ax.set_title("A/B test results — red = statistically significant")
    fig.tight_layout()
    save(fig, "05_ab_tests.png")

    # 6. revenue by province
    fig, ax = plt.subplots(figsize=(11, 5.5))
    d = prov.sort_values("net_revenue_zar")
    colors = [RED if r == "Priority growth market" else INK for r in d["market_role"]]
    ax.barh(d["province"], d["net_revenue_zar"] / 1e9, color=colors)
    ax.set_xlabel("Net revenue (R billions)")
    ax.set_title("Revenue by province — red = priority growth market")
    fig.tight_layout()
    save(fig, "06_province.png")

    # 7. forecast: actual monthly (with anomalies) + moving average + 6-month forward forecast
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(x, mon["net_revenue_zar"] / 1e6, color=INK, lw=2, label="Actual")
    ax.plot(x, mon["revenue_ma3"] / 1e6, color=GREY, lw=1.4, ls=":", label="3-month moving average")
    ax.scatter(x[flagged], (mon["net_revenue_zar"] / 1e6)[flagged], color=GOLD, s=36, zorder=5, label="Anomaly-flagged month")
    fx = pd.to_datetime(forecast["forecast_month"])
    ax.plot(fx, forecast["forecast_net_revenue_zar"] / 1e6, color=RED, lw=2.2, ls="--", marker="o", markersize=4, label="6-month forecast")
    ax.axvline(x.iloc[-1], color="#ccc", lw=1)
    ax.set_ylabel("Net revenue (R millions)")
    ax.set_title("Revenue trend, anomaly detection and 6-month forecast")
    ax.legend(frameon=False, loc="upper left")
    fig.autofmt_xdate()
    fig.tight_layout()
    save(fig, "07_forecast.png")

    # 8. return-risk watchlist (ML-scored high-risk transaction sample) by category
    fig, ax = plt.subplots(figsize=(11, 5.5))
    by_cat = risk.groupby("category")["net_revenue_zar"].agg(["count", "sum"]).sort_values("sum")
    ax.barh(by_cat.index, by_cat["sum"] / 1e6, color=RED)
    for i, (cnt, val) in enumerate(zip(by_cat["count"], by_cat["sum"])):
        ax.annotate(f"{cnt:,} lines", (val / 1e6, i), va="center", ha="left", fontsize=9, color=GREY,
                    xytext=(6, 0), textcoords="offset points")
    ax.set_xlabel("Revenue at risk (R millions)")
    ax.set_title("ML-flagged high-return-risk transactions by category (watchlist sample)")
    fig.tight_layout()
    save(fig, "08_return_risk.png")

    print("all charts written to", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
