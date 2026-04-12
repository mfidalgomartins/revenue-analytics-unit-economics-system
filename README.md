# Revenue Analytics & Unit Economics System

**One-line description**
Decision-grade revenue and unit economics system that explains growth quality and trade-offs by channel, segment, and cohort.

**Business problem**
Revenue growth can hide value destruction when acquisition, retention, or margin quality is weak. The executive question is whether growth is sustainable or simply expensive.

**What the system does**
- Simulates realistic revenue, cost, and marketing dynamics.
- Builds governed customer, cohort, and unit economics tables.
- Produces decision-focused analysis, charts, and an executive dashboard.
- Generates a scenario-based reallocation plan with guardrails.

**Decisions supported**
- Which channels to scale or cut based on LTV/CAC and payback.
- Which segments or products are diluting margin.
- Which cohorts show retention decay requiring intervention.
- How to reallocate spend without breaking profitability constraints.

**Project architecture**
Data generation → profiling → feature engineering → analysis → scenario engine → visualization + dashboard → validation + governance.

**Repository structure**
```text
src/            data/           sql/           outputs/
reports/        tests/          docs/
```

**Core outputs**
- Dashboard: `outputs/dashboard/executive_dashboard.html`
- Decision brief: `outputs/reports/decision_brief.md`
- Scenario plan: `outputs/tables/scenario_reallocation_plan.csv`
- Validation report: `outputs/reports/pre_delivery_validation_report.md`

**Why this project is strong**
- Full pipeline from data creation to decision output, not just charts.
- Explicit KPI governance and QA before release.
- Cohort, unit economics, and scenario logic aligned to real executive decisions.

**How to run**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python src/run_pipeline.py
```

**Limitations**
- Synthetic data; results demonstrate methodology, not market truth.
- LTV is observed contribution margin, not a long-term forecast.
- CAC uses simplified attribution assumptions.

**Tools**
Python, SQL, DuckDB, pandas, NumPy, scikit-learn, matplotlib, seaborn, Plotly, Chart.js.
