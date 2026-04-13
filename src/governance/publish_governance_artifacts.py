"""Publish governance artifacts used by validation and release checks."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

if str(Path(__file__).resolve().parents[2]) not in sys.path:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.governance.data_catalog import write_data_catalog_artifacts
from src.governance.metric_registry import write_metric_registry_report
from src.governance.release_governance import write_release_governance_artifacts

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def write_decision_brief() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    monthly = pd.read_csv(TABLES_DIR / "monthly_revenue_health.csv", parse_dates=["month"])
    findings = pd.read_csv(TABLES_DIR / "main_analysis_findings.csv")
    unit_econ = pd.read_csv(PROCESSED_DIR / "unit_economics.csv")
    scenario = pd.read_csv(TABLES_DIR / "scenario_outcomes_summary.csv")
    stress = pd.read_csv(TABLES_DIR / "scenario_stress_test_summary.csv")

    total_revenue = float(monthly["total_revenue"].sum())
    total_cost = float(monthly["total_cost"].sum())
    total_margin = float(monthly["contribution_margin"].sum())
    margin_pct = total_margin / total_revenue if total_revenue else float("nan")

    unit_sorted = unit_econ.sort_values("LTV_to_CAC", ascending=False)
    top_channel = unit_sorted.iloc[0]
    bottom_channel = unit_sorted.iloc[-1]

    scenario_row = scenario.iloc[0]
    stress_by_name = stress.set_index("scenario_name")

    brief_lines = [
        "# Decision Brief",
        "",
        "## Executive Summary",
        f"- Total revenue: ${total_revenue:,.2f}",
        f"- Contribution margin: ${total_margin:,.2f} ({margin_pct:.1%})",
        "- Growth quality is assessed via margin trend, cohort retention, and channel unit economics.",
        "",
        "## Channel Unit Economics (Observed)",
        f"- Best channel: {top_channel['acquisition_channel']} (LTV/CAC {top_channel['LTV_to_CAC']:.2f}, payback {top_channel['approximate_payback_period']:.1f}m)",
        f"- Weakest channel: {bottom_channel['acquisition_channel']} (LTV/CAC {bottom_channel['LTV_to_CAC']:.2f}, payback {bottom_channel['approximate_payback_period']:.1f}m)",
        "",
        "## Scenario Summary (Policy Simulation)",
        f"- Baseline contribution: ${scenario_row['baseline_contribution_est']:,.2f}",
        f"- Scenario contribution: ${scenario_row['scenario_contribution_est']:,.2f}",
        f"- Estimated uplift: ${scenario_row['estimated_contribution_uplift']:,.2f}",
        "",
        "## Stress Cases",
        f"- Best case: ${float(stress_by_name.loc['best_case', 'scenario_contribution_est']):,.2f}",
        f"- Base case: ${float(stress_by_name.loc['base_case', 'scenario_contribution_est']):,.2f}",
        f"- Worst case: ${float(stress_by_name.loc['worst_case', 'scenario_contribution_est']):,.2f}",
        "",
        "## Recommendations",
        "1. Shift budget away from inefficient channels until LTV/CAC >= 3.0 and payback <= 12 months.",
        "2. Prioritize retention plays in cohorts with the steepest early‑life decay.",
        "3. Address low‑margin pockets via pricing and cost‑to‑serve changes.",
        "",
        "## Assumptions and Caveats",
        "- Data is synthetic and intended for methodology demonstration, not forecasting.",
        "- LTV is observed contribution margin per customer during the available window.",
        "- CAC is period-level spend divided by customers acquired in the channel.",
        "- Scenario outputs apply bounded CAC/LTV response assumptions under spend changes; they are policy simulations, not forecasts.",
    ]

    (REPORTS_DIR / "decision_brief.md").write_text("\n".join(brief_lines), encoding="utf-8")


def run() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    write_metric_registry_report()
    write_data_catalog_artifacts()
    write_release_governance_artifacts()
    write_decision_brief()
    print("Governance artifacts published.")
    print(f"metric_registry: {REPORTS_DIR / 'metric_governance_registry.md'}")
    print(f"release_governance: {REPORTS_DIR / 'release_governance.md'}")
    print(f"decision_brief: {REPORTS_DIR / 'decision_brief.md'}")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
