from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from src.dashboard_builder.kpi_snapshot import compute_kpi_snapshot


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_kpi_snapshot_contract_full_coverage() -> None:
    customers = pd.read_csv(
        PROJECT_ROOT / "data" / "raw" / "customers.csv", parse_dates=["signup_date"]
    )
    transactions = pd.read_csv(
        PROJECT_ROOT / "data" / "raw" / "transactions.csv",
        parse_dates=["transaction_date"],
    )
    marketing = pd.read_csv(
        PROJECT_ROOT / "data" / "raw" / "marketing_spend.csv", parse_dates=["date"]
    )

    coverage_start = min(transactions["transaction_date"].min(), marketing["date"].min())
    coverage_end = max(transactions["transaction_date"].max(), marketing["date"].max())

    snapshot = compute_kpi_snapshot(
        customers=customers,
        transactions=transactions,
        marketing_spend=marketing,
        start_date=coverage_start,
        end_date=coverage_end,
    )

    assert snapshot["growth_method"] == "first_vs_last_month"
    assert math.isclose(float(snapshot["revenue"]), 54595966.54, abs_tol=0.01)
    assert math.isclose(float(snapshot["margin"]), 16564030.67, abs_tol=0.01)
    assert math.isclose(float(snapshot["cac"]), 616.9149833333333, abs_tol=1e-9)
    assert math.isclose(float(snapshot["avg_ltv"]), 1840.4478522222223, abs_tol=1e-9)
    assert math.isclose(float(snapshot["ltv_to_cac"]), 2.9833087247741332, abs_tol=1e-12)
    assert math.isclose(float(snapshot["payback_months"]), 12.067138644099117, abs_tol=1e-12)
    assert math.isclose(float(snapshot["growth_rate"]), 46.777783980127055, abs_tol=1e-12)
