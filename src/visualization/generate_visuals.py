"""Generate publication-quality chart pack for the analytics narrative."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter, PercentFormatter

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"


COLORS = {
    "revenue": "#0B4F6C",
    "cost": "#C44536",
    "margin": "#2A9D8F",
    "neutral": "#6C757D",
    "accent": "#FFB703",
    "bar": "#264653",
}


def currency_fmt(x: float, _: int) -> str:
    if abs(x) >= 1_000_000:
        return f"${x / 1_000_000:.1f}M"
    if abs(x) >= 1_000:
        return f"${x / 1_000:.0f}K"
    return f"${x:.0f}"


def save_figure(fig: plt.Figure, filename: str) -> Path:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CHARTS_DIR / filename
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def base_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["figure.titlesize"] = 14


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "monthly_revenue_health": pd.read_csv(
            TABLES_DIR / "monthly_revenue_health.csv", parse_dates=["month"]
        ),
        "cohort_retention_summary": pd.read_csv(TABLES_DIR / "cohort_retention_summary.csv"),
        "unit_economics": pd.read_csv(TABLES_DIR / "unit_economics_channel_diagnostics.csv"),
        "segment_profitability": pd.read_csv(TABLES_DIR / "segment_profitability.csv"),
        "customer_metrics": pd.read_csv(PROCESSED_DIR / "customer_metrics.csv"),
        "customers": pd.read_csv(RAW_DIR / "customers.csv"),
        "transactions": pd.read_csv(RAW_DIR / "transactions.csv", parse_dates=["transaction_date"]),
    }


def chart_revenue_trend(monthly: pd.DataFrame) -> tuple[str, str]:
    df = monthly.copy()
    start = float(df["total_revenue"].iloc[0])
    end = float(df["total_revenue"].iloc[-1])
    ratio = end / start if start else np.nan

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df["month"], df["total_revenue"], color=COLORS["revenue"], linewidth=2.5)
    ax.fill_between(df["month"], df["total_revenue"], color=COLORS["revenue"], alpha=0.08)
    ax.set_title(f"Revenue scaled {ratio:.1f}x from first to latest month")
    ax.set_ylabel("Revenue")
    ax.yaxis.set_major_formatter(FuncFormatter(currency_fmt))
    ax.set_ylim(bottom=0)
    ax.set_xlabel("")

    save_figure(fig, "01_revenue_trend_over_time.png")
    takeaway = f"Monthly revenue increased from ${start:,.0f} to ${end:,.0f} ({ratio:.1f}x)."
    return "01_revenue_trend_over_time.png", takeaway


def chart_margin_trend(monthly: pd.DataFrame) -> tuple[str, str]:
    df = monthly.copy()
    start = float(df["contribution_margin"].iloc[0])
    end = float(df["contribution_margin"].iloc[-1])
    growth = (end / start - 1) if start else np.nan

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df["month"], df["contribution_margin"], color=COLORS["margin"], linewidth=2.5)
    ax.fill_between(df["month"], df["contribution_margin"], color=COLORS["margin"], alpha=0.1)
    ax.set_title(
        f"Contribution margin expanded {growth:.0%} as scale improved"
        if pd.notna(growth)
        else "Contribution margin trend"
    )
    ax.set_ylabel("Contribution Margin")
    ax.yaxis.set_major_formatter(FuncFormatter(currency_fmt))
    ax.set_ylim(bottom=0)
    ax.set_xlabel("")

    save_figure(fig, "02_contribution_margin_trend_over_time.png")
    takeaway = f"Contribution margin rose from ${start:,.0f} to ${end:,.0f} ({growth:.0%})."
    return "02_contribution_margin_trend_over_time.png", takeaway


def chart_revenue_vs_cost(monthly: pd.DataFrame) -> tuple[str, str]:
    df = monthly.copy()
    latest_gap = float(df["total_revenue"].iloc[-1] - df["total_cost"].iloc[-1])

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df["month"], df["total_revenue"], color=COLORS["revenue"], linewidth=2.3, label="Revenue")
    ax.plot(df["month"], df["total_cost"], color=COLORS["cost"], linewidth=2.3, label="Cost")
    ax.set_title("Revenue remains above cost with widening absolute spread")
    ax.set_ylabel("Amount")
    ax.yaxis.set_major_formatter(FuncFormatter(currency_fmt))
    ax.set_ylim(bottom=0)
    ax.set_xlabel("")
    ax.legend(frameon=False)

    save_figure(fig, "03_revenue_vs_cost_over_time.png")
    takeaway = f"Latest monthly revenue-cost spread is ${latest_gap:,.0f}."
    return "03_revenue_vs_cost_over_time.png", takeaway


def chart_cohort_revenue_retention(cohort_retention: pd.DataFrame) -> tuple[str, str]:
    df = cohort_retention.copy()
    df = df[df["months_since_cohort"] <= 24]
    m6 = float(df.loc[df["months_since_cohort"] == 6, "median_revenue_retention"].iloc[0])
    m12 = float(df.loc[df["months_since_cohort"] == 12, "median_revenue_retention"].iloc[0])

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(
        df["months_since_cohort"],
        df["median_revenue_retention"],
        color=COLORS["bar"],
        linewidth=2.5,
        marker="o",
        markersize=3,
    )
    ax.axhline(1.0, color=COLORS["neutral"], linestyle="--", linewidth=1.2, alpha=0.8)
    ax.set_title("Cohort revenue retention decays materially after month 6")
    ax.set_ylabel("Median Revenue Retention")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xlabel("Months Since Cohort Start")
    ax.set_ylim(bottom=0)

    save_figure(fig, "04_cohort_revenue_retention.png")
    takeaway = f"Median revenue retention drops to {m6:.1%} by month 6 and {m12:.1%} by month 12."
    return "04_cohort_revenue_retention.png", takeaway


def chart_ltv_vs_cac(unit_econ: pd.DataFrame) -> tuple[str, str]:
    df = unit_econ.copy().sort_values("LTV_to_CAC", ascending=False)
    best = df.iloc[0]
    worst = df.iloc[-1]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df["CAC"], df["average_LTV"], color=COLORS["bar"], s=90, alpha=0.9)

    x_max = float(df["CAC"].max() * 1.1)
    ax.plot([0, x_max], [0, x_max], linestyle="--", color=COLORS["neutral"], linewidth=1.2)

    for _, row in df.iterrows():
        ax.annotate(
            row["acquisition_channel"],
            (row["CAC"], row["average_LTV"]),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=9,
        )

    ax.set_title("Organic and referral channels dominate unit economics efficiency")
    ax.set_xlabel("CAC")
    ax.set_ylabel("Average LTV")
    ax.xaxis.set_major_formatter(FuncFormatter(currency_fmt))
    ax.yaxis.set_major_formatter(FuncFormatter(currency_fmt))
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    save_figure(fig, "05_ltv_vs_cac_by_acquisition_channel.png")
    takeaway = (
        f"Best LTV/CAC is {best['acquisition_channel']} ({best['LTV_to_CAC']:.2f}); "
        f"weakest is {worst['acquisition_channel']} ({worst['LTV_to_CAC']:.2f})."
    )
    return "05_ltv_vs_cac_by_acquisition_channel.png", takeaway


def chart_margin_by_segment(segment_profitability: pd.DataFrame) -> tuple[str, str]:
    df = segment_profitability.copy().sort_values("contribution_margin", ascending=False)
    lowest_margin_pct = float(df["margin_pct"].min())
    lowest_segment = str(df.loc[df["margin_pct"].idxmin(), "dimension_value"])

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(df["dimension_value"], df["contribution_margin"], color=COLORS["margin"], alpha=0.9)
    ax.set_title("Enterprise drives margin dollars but shows the thinnest margin rate")
    ax.set_ylabel("Contribution Margin")
    ax.yaxis.set_major_formatter(FuncFormatter(currency_fmt))
    ax.set_xlabel("")

    for bar, pct in zip(bars, df["margin_pct"], strict=False):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{pct:.1%}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    save_figure(fig, "06_contribution_margin_by_segment.png")
    takeaway = f"{lowest_segment} has the lowest margin rate at {lowest_margin_pct:.1%}."
    return "06_contribution_margin_by_segment.png", takeaway


def chart_revenue_distribution(customer_metrics: pd.DataFrame) -> tuple[str, str]:
    df = customer_metrics.copy()
    rev = df["total_revenue"].fillna(0)
    rev_nonzero = rev[rev > 0]
    p50 = float(rev_nonzero.median()) if len(rev_nonzero) else 0.0
    p90 = float(rev_nonzero.quantile(0.9)) if len(rev_nonzero) else 0.0
    top_decile_threshold = rev_nonzero.quantile(0.9) if len(rev_nonzero) else np.nan
    top_decile_share = (
        rev_nonzero[rev_nonzero >= top_decile_threshold].sum() / rev_nonzero.sum()
        if len(rev_nonzero) and rev_nonzero.sum() > 0
        else np.nan
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(rev_nonzero, bins=40, color=COLORS["bar"], alpha=0.9)
    ax.set_xscale("log")
    ax.set_title("Customer revenue is highly skewed toward a high-value minority")
    ax.set_xlabel("Total Revenue per Customer (log scale)")
    ax.set_ylabel("Customer Count")
    ax.xaxis.set_major_formatter(FuncFormatter(currency_fmt))

    save_figure(fig, "07_revenue_distribution_across_customers.png")
    takeaway = (
        f"Median customer revenue is ${p50:,.0f} vs P90 ${p90:,.0f}; "
        f"top decile contributes {top_decile_share:.1%} of customer revenue."
    )
    return "07_revenue_distribution_across_customers.png", takeaway


def chart_avg_rev_per_tx_by_segment(
    customers: pd.DataFrame, transactions: pd.DataFrame
) -> tuple[str, str]:
    df = transactions.merge(customers[["customer_id", "segment"]], on="customer_id", how="left")
    by_seg = (
        df.groupby("segment", as_index=False)
        .agg(avg_revenue_per_transaction=("revenue", "mean"))
        .sort_values("avg_revenue_per_transaction", ascending=False, ignore_index=True)
    )
    top_seg = str(by_seg.iloc[0]["segment"])
    top_val = float(by_seg.iloc[0]["avg_revenue_per_transaction"])

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(by_seg["segment"], by_seg["avg_revenue_per_transaction"], color=COLORS["accent"], alpha=0.95)
    ax.set_title("Enterprise transactions carry materially higher ticket size")
    ax.set_ylabel("Average Revenue per Transaction")
    ax.yaxis.set_major_formatter(FuncFormatter(currency_fmt))
    ax.set_xlabel("")

    save_figure(fig, "08_avg_revenue_per_transaction_by_segment.png")
    takeaway = f"{top_seg} has the highest average revenue per transaction at ${top_val:,.0f}."
    return "08_avg_revenue_per_transaction_by_segment.png", takeaway


def write_chart_index(entries: list[tuple[str, str, str]]) -> None:
    lines = [
        "# Chart Index",
        "",
        "| Filename | Chart Purpose | Main Takeaway |",
        "| --- | --- | --- |",
    ]
    for filename, purpose, takeaway in entries:
        lines.append(f"| `{filename}` | {purpose} | {takeaway} |")

    (CHARTS_DIR / "chart_index.md").write_text("\n".join(lines), encoding="utf-8")


def run() -> None:
    base_style()
    data = load_data()

    entries: list[tuple[str, str, str]] = []

    f, t = chart_revenue_trend(data["monthly_revenue_health"])
    entries.append((f, "Show top-line monthly growth trajectory.", t))

    f, t = chart_margin_trend(data["monthly_revenue_health"])
    entries.append((f, "Track monthly contribution margin expansion.", t))

    f, t = chart_revenue_vs_cost(data["monthly_revenue_health"])
    entries.append((f, "Compare revenue and cost scale through time.", t))

    f, t = chart_cohort_revenue_retention(data["cohort_retention_summary"])
    entries.append((f, "Assess revenue retention durability by cohort age.", t))

    f, t = chart_ltv_vs_cac(data["unit_economics"])
    entries.append((f, "Benchmark channel efficiency using LTV and CAC.", t))

    f, t = chart_margin_by_segment(data["segment_profitability"])
    entries.append((f, "Compare contribution margin by customer segment.", t))

    f, t = chart_revenue_distribution(data["customer_metrics"])
    entries.append((f, "Visualize customer-level revenue concentration.", t))

    f, t = chart_avg_rev_per_tx_by_segment(data["customers"], data["transactions"])
    entries.append((f, "Compare transaction ticket size by segment.", t))

    write_chart_index(entries)

    print("Chart pack created.")
    print(f"charts_dir: {CHARTS_DIR}")
    print(f"chart_index: {CHARTS_DIR / 'chart_index.md'}")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
