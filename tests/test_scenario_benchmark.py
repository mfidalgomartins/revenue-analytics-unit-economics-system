from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_scenario_benchmark_seed_coverage_contract() -> None:
    benchmark = pd.read_csv(PROJECT_ROOT / "outputs" / "tables" / "scenario_benchmark_by_seed.csv")
    seeds = sorted(benchmark["seed"].astype(int).tolist())
    assert seeds == [7, 21, 42, 84, 126]


def test_scenario_benchmark_positive_uplift_contract() -> None:
    benchmark = pd.read_csv(PROJECT_ROOT / "outputs" / "tables" / "scenario_benchmark_by_seed.csv")
    assert (benchmark["estimated_contribution_uplift"] > 0).all()
