"""Render Leatt Growth OS charts from the real gold-layer CSVs.

Bold red/black/white palette matching Leatt's actual brand identity
(motocross/adventure gear) — distinct from every other project in this
portfolio. Every number comes straight from artifacts/data_samples/*.csv.
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
    return f"R{x/1e6:,.1f}m" if abs(x) < 1e9 else f"R{x/1e9:,.2f}bn"


def main():
    cat = pd.read_csv(os.path.join(DATA, "gold_category_kpis.csv")).sort_values("net_revenue_zar", ascending=False)
    chan = pd.read_csv(os.path.join(DATA, "gold_channel_kpis.csv")).sort_values("net_revenue_zar", ascending=False)
    mon = pd.read_csv(os.path.join(DATA, "gold_monthly_kpis.csv")).sort_values("month")
    roi = pd.read_csv(os.path.join(DATA, "leatt_marketing_roi.csv")).sort_values("roas", ascending=False)
    ab = pd.read_csv(os.path.join(DATA, "leatt_ab_test_results.csv"))

    # 1. category revenue + margin
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    d = cat.sort_values("net_revenue_zar")
    ax1.barh(d["category"], d["net_revenue_zar"] / 1e6, color=RED)
    ax1.set_xlabel("Net revenue (R millions)")
    ax1.set_title("Revenue by category")
    d2 = cat.sort_values("gross_margin_rate")
    ax2.barh(d2["category"], d2["gross_margin_rate"] * 100, color=INK)
    ax2.axvline(cat["gross_margin_rate"].mean() * 100, color=RED, ls="--", lw=1.5,
                label=f"avg {cat['gross_margin_rate'].mean():.0%}")
    ax2.set_xlabel("Gross margin %")
    ax2.set_title("Margin by category")
    ax2.legend(frameon=False)
    fig.tight_layout()
    save(fig, "01_category.png")

    # 2. monthly revenue + margin trend
    fig, ax = plt.subplots(figsize=(12, 5.5))
    x = pd.to_datetime(mon["month"])
    ax.plot(x, mon["net_revenue_zar"] / 1e6, color=RED, lw=2.2, label="Net revenue")
    ax.fill_between(x, mon["net_revenue_zar"] / 1e6, color=RED, alpha=0.08)
    ax2 = ax.twinx()
    ax2.grid(False)
    ax2.plot(x, mon["gross_margin_zar"] / mon["net_revenue_zar"] * 100, color=INK, lw=1.6, ls="--", label="Margin %")
    ax2.set_ylabel("Margin %")
    nov_dec = x.dt.month.isin([11, 12])
    for xi, yi in zip(x[nov_dec], (mon["gross_margin_zar"] / mon["net_revenue_zar"] * 100)[nov_dec]):
        ax2.scatter([xi], [yi], color=GOLD, s=28, zorder=5)
    ax2.annotate("Nov/Dec: seasonal margin\ncompression both years", xy=(x[nov_dec].iloc[-1], 41.5),
                 xytext=(20, -30), textcoords="offset points", fontsize=8.5, color=GOLD,
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
    bars = ax.barh(d["channel"], d["net_revenue_zar"] / 1e6, color=RED)
    for b, orders in zip(bars, d["orders"]):
        ax.annotate(f"{orders:,} orders", (b.get_width(), b.get_y() + b.get_height() / 2),
                    va="center", ha="left", fontsize=9, color=GREY, xytext=(6, 0),
                    textcoords="offset points")
    ax.set_xlabel("Net revenue (R millions)")
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

    print("all charts written to", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
