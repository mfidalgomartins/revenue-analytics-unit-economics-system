"""Deterministic KPI snapshot logic mirroring executive dashboard calculations."""

from __future__ import annotations

from dataclasses import dataclass
import math

import pandas as pd


@dataclass(frozen=True)
class Window:
    start: pd.Timestamp
    end: pd.Timestamp


def _filter_by_window(df: pd.DataFrame, date_col: str, window: Window) -> pd.DataFrame:
    d = pd.to_datetime(df[date_col]).dt.normalize()
    return df[(d >= window.start) & (d <= window.end)].copy()


def _period_snapshot(
    transactions: pd.DataFrame,
    customers: pd.DataFrame,
    marketing_spend: pd.DataFrame,
) -> dict[str, float]:
    revenue = float(transactions["revenue"].sum())
    cost = float(transactions["cost"].sum())
    margin = revenue - cost
    margin_pct = margin / revenue if revenue > 0 else float("nan")

    acquired_count = int(customers["customer_id"].nunique())
    spend_total = float(marketing_spend["spend"].sum())

    cac = spend_total / acquired_count if acquired_count > 0 else float("nan")
    avg_ltv = margin / acquired_count if acquired_count > 0 else float("nan")
    ltv_to_cac = (
        avg_ltv / cac
        if (not math.isnan(cac) and cac > 0 and not math.isnan(avg_ltv))
        else float("nan")
    )

    months_obs = (
        int(transactions["transaction_date"].dt.to_period("M").nunique())
        if not transactions.empty
        else 0
    )
    monthly_margin = margin / months_obs if months_obs > 0 else float("nan")
    monthly_margin_per_customer = (
        monthly_margin / acquired_count
        if (acquired_count > 0 and not math.isnan(monthly_margin))
        else float("nan")
    )
    payback = (
        cac / monthly_margin_per_customer
        if (
            not math.isnan(cac)
            and not math.isnan(monthly_margin_per_customer)
            and monthly_margin_per_customer > 0
        )
        else float("nan")
    )

    return {
        "revenue": revenue,
        "cost": cost,
        "margin": margin,
        "margin_pct": margin_pct,
        "acquired_count": float(acquired_count),
        "cac": cac,
        "avg_ltv": avg_ltv,
        "ltv_to_cac": ltv_to_cac,
        "payback_months": payback,
    }


def compute_kpi_snapshot(
    customers: pd.DataFrame,
    transactions: pd.DataFrame,
    marketing_spend: pd.DataFrame,
    start_date: str | pd.Timestamp,
    end_date: str | pd.Timestamp,
) -> dict[str, float | str]:
    """Compute the dashboard KPI snapshot for a selected date window."""
    start = pd.Timestamp(start_date).normalize()
    end = pd.Timestamp(end_date).normalize()
    window = Window(start=start, end=end)

    duration_days = int((end - start).days) + 1
    prior_end = start - pd.Timedelta(days=1)
    prior_start = prior_end - pd.Timedelta(days=duration_days - 1)
    pre_prior_end = prior_start - pd.Timedelta(days=1)
    pre_prior_start = pre_prior_end - pd.Timedelta(days=duration_days - 1)

    current = _period_snapshot(
        _filter_by_window(transactions, "transaction_date", window),
        _filter_by_window(customers, "signup_date", window),
        _filter_by_window(marketing_spend, "date", window),
    )
    prior = _period_snapshot(
        _filter_by_window(transactions, "transaction_date", Window(prior_start, prior_end)),
        _filter_by_window(customers, "signup_date", Window(prior_start, prior_end)),
        _filter_by_window(marketing_spend, "date", Window(prior_start, prior_end)),
    )
    pre_prior = _period_snapshot(
        _filter_by_window(transactions, "transaction_date", Window(pre_prior_start, pre_prior_end)),
        _filter_by_window(customers, "signup_date", Window(pre_prior_start, pre_prior_end)),
        _filter_by_window(marketing_spend, "date", Window(pre_prior_start, pre_prior_end)),
    )

    growth_rate = (
        (current["revenue"] / prior["revenue"]) - 1
        if (not math.isnan(prior["revenue"]) and prior["revenue"] > 0)
        else float("nan")
    )
    growth_method = "prior_period"
    if math.isnan(growth_rate):
        tx_window = _filter_by_window(transactions, "transaction_date", window)
        monthly = (
            tx_window.assign(month=tx_window["transaction_date"].dt.to_period("M").astype(str))
            .groupby("month", as_index=False)["revenue"]
            .sum()
            .sort_values("month")
        )
        if len(monthly) >= 2:
            first_revenue = float(monthly.iloc[0]["revenue"])
            last_revenue = float(monthly.iloc[-1]["revenue"])
            if first_revenue > 0:
                growth_rate = (last_revenue / first_revenue) - 1
                growth_method = "first_vs_last_month"

    prior_growth_rate = (
        (prior["revenue"] / pre_prior["revenue"]) - 1
        if (not math.isnan(pre_prior["revenue"]) and pre_prior["revenue"] > 0)
        else float("nan")
    )

    return {
        **current,
        "growth_rate": float(growth_rate),
        "growth_method": growth_method,
        "prior_growth_rate": float(prior_growth_rate),
    }
