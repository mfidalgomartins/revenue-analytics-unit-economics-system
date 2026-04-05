from __future__ import annotations

import math

import pandas as pd

from src.feature_engineering.build_features import (
    build_customer_metrics,
    build_unit_economics,
)


def test_build_customer_metrics_computes_expected_fields() -> None:
    customers = pd.DataFrame(
        {
            "customer_id": ["C1", "C2"],
            "signup_date": pd.to_datetime(["2024-01-01", "2024-01-05"]),
            "segment": ["Startup", "SMB"],
            "region": ["EMEA", "North America"],
            "acquisition_channel": ["paid_search", "organic"],
        }
    )
    transactions = pd.DataFrame(
        {
            "transaction_id": ["T1", "T2"],
            "customer_id": ["C1", "C1"],
            "transaction_date": pd.to_datetime(["2024-01-10", "2024-01-15"]),
            "revenue": [100.0, 300.0],
            "cost": [60.0, 150.0],
            "product_type": ["Core", "Premium"],
        }
    )

    out = build_customer_metrics(customers, transactions)
    c1 = out.loc[out["customer_id"] == "C1"].iloc[0]
    c2 = out.loc[out["customer_id"] == "C2"].iloc[0]

    assert c1["total_revenue"] == 400.0
    assert c1["total_cost"] == 210.0
    assert c1["contribution_margin"] == 190.0
    assert math.isclose(c1["contribution_margin_pct"], 0.475, rel_tol=0, abs_tol=1e-6)
    assert c1["transaction_count"] == 2
    assert c1["lifetime_days"] == 6
    assert c1["avg_revenue_per_transaction"] == 200.0
    assert math.isclose(c1["revenue_per_day"], 66.67, rel_tol=0, abs_tol=0.01)

    assert c2["transaction_count"] == 0
    assert c2["total_revenue"] == 0.0
    assert c2["total_cost"] == 0.0
    assert c2["lifetime_days"] == 0
    assert c2["contribution_margin"] == 0.0


def test_build_unit_economics_handles_positive_and_negative_payback() -> None:
    customers = pd.DataFrame(
        {
            "customer_id": ["C1", "C2", "C3", "C4"],
            "signup_date": pd.to_datetime(["2024-01-01"] * 4),
            "segment": ["Startup", "SMB", "SMB", "Startup"],
            "region": ["EMEA", "EMEA", "EMEA", "EMEA"],
            "acquisition_channel": ["paid_search", "organic", "organic", "social_ads"],
        }
    )

    marketing_spend = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-02-01",
                    "2024-01-01",
                    "2024-02-01",
                    "2024-01-01",
                    "2024-02-01",
                ]
            ),
            "acquisition_channel": [
                "paid_search",
                "paid_search",
                "organic",
                "organic",
                "social_ads",
                "social_ads",
            ],
            "spend": [100.0, 100.0, 60.0, 60.0, 50.0, 50.0],
        }
    )

    customer_metrics = pd.DataFrame(
        {
            "customer_id": ["C1", "C2", "C3", "C4"],
            "segment": ["Startup", "SMB", "SMB", "Startup"],
            "region": ["EMEA", "EMEA", "EMEA", "EMEA"],
            "acquisition_channel": ["paid_search", "organic", "organic", "social_ads"],
            "first_transaction_date": [None, None, None, None],
            "last_transaction_date": [None, None, None, None],
            "lifetime_days": [0, 0, 0, 0],
            "total_revenue": [0.0, 0.0, 0.0, 0.0],
            "total_cost": [0.0, 0.0, 0.0, 0.0],
            "contribution_margin": [200.0, 120.0, 80.0, -10.0],
            "contribution_margin_pct": [0.0, 0.0, 0.0, 0.0],
            "transaction_count": [0, 0, 0, 0],
            "avg_revenue_per_transaction": [0.0, 0.0, 0.0, 0.0],
            "revenue_per_day": [0.0, 0.0, 0.0, 0.0],
        }
    )

    out = build_unit_economics(customers, marketing_spend, customer_metrics)

    paid = out.loc[out["acquisition_channel"] == "paid_search"].iloc[0]
    organic = out.loc[out["acquisition_channel"] == "organic"].iloc[0]
    social = out.loc[out["acquisition_channel"] == "social_ads"].iloc[0]

    assert math.isclose(paid["CAC"], 200.0, rel_tol=0, abs_tol=1e-4)
    assert math.isclose(paid["average_LTV"], 200.0, rel_tol=0, abs_tol=1e-4)
    assert math.isclose(paid["LTV_to_CAC"], 1.0, rel_tol=0, abs_tol=1e-4)
    assert math.isclose(paid["approximate_payback_period"], 2.0, rel_tol=0, abs_tol=1e-4)

    assert math.isclose(organic["CAC"], 60.0, rel_tol=0, abs_tol=1e-4)
    assert math.isclose(organic["average_LTV"], 100.0, rel_tol=0, abs_tol=1e-4)
    assert math.isclose(organic["LTV_to_CAC"], 1.6667, rel_tol=0, abs_tol=1e-4)
    assert math.isclose(organic["approximate_payback_period"], 1.2, rel_tol=0, abs_tol=1e-4)

    assert math.isnan(float(social["approximate_payback_period"]))
