# Revenue Analytics & Unit Economics System

A decision-grade revenue and unit economics system built to answer the question that actually matters: is growth sustainable, or just expensive. It combines synthetic but realistic commercial data with governed metrics, scenario logic, and executive-ready outputs.

## Why this exists
Top-line growth can mask weak acquisition efficiency, fragile retention, or margin erosion. This project is designed to surface those risks early and make trade-offs explicit.

## What it does, end to end
It simulates customer, transaction, and marketing dynamics, builds customer/cohort/unit economics tables, runs the core analysis, and publishes a dashboard plus decision artifacts. The pipeline is governed with QA and metric definitions so outputs are consistent and auditable.

## Decisions it supports
- Which channels to scale or cut based on LTV/CAC and payback.
- Which segments or products are diluting margin.
- Which cohorts show retention decay requiring intervention.
- How to reallocate spend without breaking profitability guardrails.

## Architecture (fast view)
Data generation → profiling → feature engineering → analysis → scenario engine → visualization + dashboard → validation + governance.

## Repository structure
```text
src/            data/           sql/           outputs/
reports/        tests/          docs/
```

## Core outputs
- `outputs/dashboard/executive-revenue-unit-economics-command-center.html`
- `outputs/reports/decision_brief.md`
- `outputs/tables/scenario_reallocation_plan.csv`
- `outputs/reports/pre_delivery_validation_report.md`

Live dashboard: [https://mfidalgomartins.github.io/revenue-unit-economics-system/](https://mfidalgomartins.github.io/revenue-unit-economics-system/)

## Why this is above a typical portfolio project
This is not a set of charts. It is a full decision system with governed metrics, QA gates, and scenario logic tied to real executive trade-offs.

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python src/run_pipeline.py
```

## Limitations
- Synthetic data; results demonstrate method, not market truth.
- LTV is observed contribution margin, not a forward forecast.
- CAC uses simplified attribution assumptions.

Tools: Python, SQL, DuckDB, pandas, NumPy, scikit-learn, matplotlib, seaborn, Plotly, Chart.js.
