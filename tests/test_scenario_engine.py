from __future__ import annotations

import math

import pandas as pd

from src.scenario_engine.build_scenarios import (
    build_reallocation_plan,
    build_stress_test_summary,
)


def test_reallocation_plan_preserves_total_budget_and_shapes_actions() -> None:
    unit_economics = pd.DataFrame(
        {
            "acquisition_channel": ["organic", "paid_search", "social_ads"],
            "customers_acquired": [100, 100, 100],
            "total_spend": [1000.0, 1000.0, 1000.0],
            "CAC": [100.0, 100.0, 100.0],
            "average_LTV": [400.0, 80.0, 50.0],
            "median_LTV": [350.0, 70.0, 45.0],
            "LTV_to_CAC": [4.0, 0.8, 0.5],
            "approximate_payback_period": [8.0, 30.0, 35.0],
        }
    )
    marketing_spend = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-01", "2024-01-01"]
            ),
            "acquisition_channel": ["organic", "paid_search", "social_ads"],
            "spend": [1000.0, 1000.0, 1000.0],
        }
    )

    plan, summary = build_reallocation_plan(unit_economics, marketing_spend)
    s = summary.iloc[0]

    assert math.isclose(
        float(s["total_budget_baseline"]),
        float(s["total_budget_scenario"]),
        rel_tol=0,
        abs_tol=1e-6,
    )

    organic = plan.loc[plan["acquisition_channel"] == "organic"].iloc[0]
    paid = plan.loc[plan["acquisition_channel"] == "paid_search"].iloc[0]
    social = plan.loc[plan["acquisition_channel"] == "social_ads"].iloc[0]

    assert organic["scenario_spend"] > organic["baseline_spend"]
    assert paid["scenario_spend"] < paid["baseline_spend"]
    assert social["scenario_spend"] < social["baseline_spend"]
    assert "Scale with guardrails" in organic["recommended_action"]

    stress = build_stress_test_summary(plan)
    by_name = stress.set_index("scenario_name")
    assert (
        float(by_name.loc["best_case", "scenario_contribution_est"])
        >= float(by_name.loc["base_case", "scenario_contribution_est"])
        >= float(by_name.loc["worst_case", "scenario_contribution_est"])
    )
