"""Build decision scenarios for channel budget reallocation."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

if str(Path(__file__).resolve().parents[2]) not in sys.path:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.governance.metric_registry import (
    EFFICIENCY_THRESHOLDS,
    classify_channel_efficiency,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROC_DIR = PROJECT_ROOT / "data" / "processed"
OUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
OUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"


UPLIFT_POLICY = {
    "efficient": 0.20,
    "borderline": 0.00,
    "inefficient": -0.35,
    "undefined": -0.20,
}

STRESS_SCENARIOS = {
    "best_case": {"cac_multiplier": 0.90, "ltv_multiplier": 1.08},
    "base_case": {"cac_multiplier": 1.00, "ltv_multiplier": 1.00},
    "worst_case": {"cac_multiplier": 1.15, "ltv_multiplier": 0.88},
}


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    unit_economics = pd.read_csv(PROC_DIR / "unit_economics.csv")
    marketing_spend = pd.read_csv(RAW_DIR / "marketing_spend.csv", parse_dates=["date"])
    return unit_economics, marketing_spend


def build_reallocation_plan(
    unit_economics: pd.DataFrame,
    marketing_spend: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    ue = unit_economics.copy()
    ue["efficiency_status"] = ue.apply(
        lambda r: classify_channel_efficiency(r["LTV_to_CAC"], r["approximate_payback_period"]),
        axis=1,
    )

    base_spend = marketing_spend.groupby("acquisition_channel", as_index=False)["spend"].sum()
    base_spend = base_spend.rename(columns={"spend": "baseline_spend"})
    ue = ue.merge(base_spend, on="acquisition_channel", how="left")

    ue["policy_uplift_pct"] = ue["efficiency_status"].map(UPLIFT_POLICY).fillna(0.0)
    ue["preliminary_spend"] = ue["baseline_spend"] * (1 + ue["policy_uplift_pct"])
    total_budget = float(ue["baseline_spend"].sum())
    prelim_total = float(ue["preliminary_spend"].sum())
    delta_budget = total_budget - prelim_total

    efficient_mask = ue["efficiency_status"] == "efficient"
    efficient_scores = np.where(
        efficient_mask,
        np.where(ue["CAC"] > 0, ue["LTV_to_CAC"] / ue["CAC"], 0.0),
        0.0,
    )
    score_sum = float(efficient_scores.sum())

    if score_sum > 0 and delta_budget != 0:
        redistribution = delta_budget * (efficient_scores / score_sum)
    else:
        redistribution = np.zeros(len(ue))

    ue["redistribution_spend"] = redistribution
    ue["scenario_spend"] = ue["preliminary_spend"] + ue["redistribution_spend"]

    ue["baseline_customers_est"] = np.where(ue["CAC"] > 0, ue["baseline_spend"] / ue["CAC"], np.nan)
    ue["scenario_customers_est"] = np.where(ue["CAC"] > 0, ue["scenario_spend"] / ue["CAC"], np.nan)

    ue["baseline_contribution_est"] = ue["baseline_customers_est"] * ue["average_LTV"]
    ue["scenario_contribution_est"] = ue["scenario_customers_est"] * ue["average_LTV"]

    ue["spend_change"] = ue["scenario_spend"] - ue["baseline_spend"]
    ue["contribution_change_est"] = ue["scenario_contribution_est"] - ue["baseline_contribution_est"]

    ue["recommended_action"] = np.select(
        [
            ue["efficiency_status"] == "efficient",
            ue["efficiency_status"] == "inefficient",
            ue["efficiency_status"] == "borderline",
        ],
        [
            "Scale with guardrails (retain LTV/CAC >= target and payback <= target).",
            "Reduce exposure and run economics recovery plan before re-scaling.",
            "Hold spend and run focused CAC/payback improvement experiments.",
        ],
        default="Investigate data quality or denominator gaps before allocation decisions.",
    )

    out_cols = [
        "acquisition_channel",
        "efficiency_status",
        "baseline_spend",
        "scenario_spend",
        "spend_change",
        "CAC",
        "average_LTV",
        "LTV_to_CAC",
        "approximate_payback_period",
        "baseline_customers_est",
        "scenario_customers_est",
        "baseline_contribution_est",
        "scenario_contribution_est",
        "contribution_change_est",
        "recommended_action",
    ]
    plan = ue[out_cols].sort_values("contribution_change_est", ascending=False, ignore_index=True)

    summary = pd.DataFrame(
        [
            {
                "scenario_name": "budget_reallocation_v1",
                "total_budget_baseline": float(plan["baseline_spend"].sum()),
                "total_budget_scenario": float(plan["scenario_spend"].sum()),
                "baseline_contribution_est": float(plan["baseline_contribution_est"].sum()),
                "scenario_contribution_est": float(plan["scenario_contribution_est"].sum()),
                "estimated_contribution_uplift": float(plan["contribution_change_est"].sum()),
                "efficient_channels_after_policy": int((plan["efficiency_status"] == "efficient").sum()),
                "inefficient_channels_after_policy": int((plan["efficiency_status"] == "inefficient").sum()),
            }
        ]
    )
    return plan, summary


def build_stress_test_summary(plan: pd.DataFrame) -> pd.DataFrame:
    """Evaluate policy output under best/base/worst CAC and LTV shocks."""
    baseline_total = float(plan["baseline_contribution_est"].sum())
    rows: list[dict[str, float | str]] = []

    for scenario_name, cfg in STRESS_SCENARIOS.items():
        cac_multiplier = float(cfg["cac_multiplier"])
        ltv_multiplier = float(cfg["ltv_multiplier"])

        scenario_customers = np.where(
            (plan["CAC"] * cac_multiplier) > 0,
            plan["scenario_spend"] / (plan["CAC"] * cac_multiplier),
            np.nan,
        )
        scenario_contribution = scenario_customers * (plan["average_LTV"] * ltv_multiplier)

        rows.append(
            {
                "scenario_name": scenario_name,
                "cac_multiplier": cac_multiplier,
                "ltv_multiplier": ltv_multiplier,
                "scenario_customers_est": float(np.nansum(scenario_customers)),
                "scenario_contribution_est": float(np.nansum(scenario_contribution)),
                "estimated_uplift_vs_baseline": float(np.nansum(scenario_contribution) - baseline_total),
            }
        )

    stress = pd.DataFrame(rows)
    base_value = float(
        stress.loc[stress["scenario_name"] == "base_case", "scenario_contribution_est"].iloc[0]
    )
    stress["estimated_uplift_vs_base_case"] = stress["scenario_contribution_est"] - base_value

    order = {"best_case": 0, "base_case": 1, "worst_case": 2}
    return stress.sort_values(
        by="scenario_name",
        key=lambda s: s.map(order),
        ignore_index=True,
    )


def write_outputs(plan: pd.DataFrame, summary: pd.DataFrame, stress_summary: pd.DataFrame) -> None:
    OUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    OUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    plan_out = plan.copy()
    summary_out = summary.copy()
    stress_out = stress_summary.copy()
    numeric_cols = [
        "baseline_spend",
        "scenario_spend",
        "spend_change",
        "CAC",
        "average_LTV",
        "LTV_to_CAC",
        "approximate_payback_period",
        "baseline_customers_est",
        "scenario_customers_est",
        "baseline_contribution_est",
        "scenario_contribution_est",
        "contribution_change_est",
    ]
    plan_out[numeric_cols] = plan_out[numeric_cols].round(4)
    summary_out = summary_out.round(4)

    plan_out.to_csv(OUT_TABLES_DIR / "scenario_reallocation_plan.csv", index=False)
    summary_out.to_csv(OUT_TABLES_DIR / "scenario_outcomes_summary.csv", index=False)
    stress_out.round(4).to_csv(OUT_TABLES_DIR / "scenario_stress_test_summary.csv", index=False)

    s = summary_out.iloc[0]
    stress_rows = []
    for r in stress_out.itertuples(index=False):
        stress_rows.append(
            "| "
            + " | ".join(
                [
                    str(r.scenario_name),
                    f"{float(r.cac_multiplier):.2f}x",
                    f"{float(r.ltv_multiplier):.2f}x",
                    f"${float(r.scenario_contribution_est):,.2f}",
                    f"${float(r.estimated_uplift_vs_baseline):,.2f}",
                    f"${float(r.estimated_uplift_vs_base_case):,.2f}",
                ]
            )
            + " |"
        )

    report = f"""# Scenario Decision Engine Report

## Scenario
- Name: `{s['scenario_name']}`
- Policy: cut inefficient channels, hold borderline channels, and reallocate to efficient channels while keeping total budget constant.

## Governance Thresholds Used
- Efficient: `LTV/CAC >= {EFFICIENCY_THRESHOLDS.ltv_cac_target}` and `payback <= {EFFICIENCY_THRESHOLDS.payback_target_months} months`
- Inefficient: `LTV/CAC < {EFFICIENCY_THRESHOLDS.ineff_ltv_cac}` or `payback > {EFFICIENCY_THRESHOLDS.ineff_payback_months} months`

## Estimated Outcome
- Baseline total budget: `${s['total_budget_baseline']:,.2f}`
- Scenario total budget: `${s['total_budget_scenario']:,.2f}`
- Baseline estimated contribution: `${s['baseline_contribution_est']:,.2f}`
- Scenario estimated contribution: `${s['scenario_contribution_est']:,.2f}`
- Estimated contribution uplift: `${s['estimated_contribution_uplift']:,.2f}`

## Stress Test (CAC and LTV shocks)
| scenario_name | CAC shock | LTV shock | scenario contribution | uplift vs baseline | uplift vs base case |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(stress_rows)}

## Interpretation
- This is a policy simulation, not a forecast.
- Estimates assume channel CAC and average LTV remain stable under spend changes.
- Use as directional decision support for budget steering and experimentation priorities.
"""
    (OUT_REPORTS_DIR / "scenario_decision_engine_report.md").write_text(report, encoding="utf-8")


def run() -> None:
    unit_economics, marketing_spend = load_inputs()
    plan, summary = build_reallocation_plan(unit_economics, marketing_spend)
    stress_summary = build_stress_test_summary(plan)
    write_outputs(plan, summary, stress_summary)

    print("Scenario decision engine completed.")
    print(f"plan: {OUT_TABLES_DIR / 'scenario_reallocation_plan.csv'}")
    print(f"summary: {OUT_TABLES_DIR / 'scenario_outcomes_summary.csv'}")
    print(f"stress_summary: {OUT_TABLES_DIR / 'scenario_stress_test_summary.csv'}")
    print(f"report: {OUT_REPORTS_DIR / 'scenario_decision_engine_report.md'}")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
