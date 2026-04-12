# Revenue Analytics & Unit Economics System

## 1. Business Problem
Many companies can show strong revenue growth while destroying value through poor acquisition efficiency, weak retention, or low-margin product mix.

This project addresses a core executive question:

**Is the company growing sustainably, or is it relying on unprofitable growth?**

## 2. Objective
Build a decision-grade analytics system that:
- evaluates growth quality, not just top-line growth
- quantifies unit economics by channel
- identifies retention decay risk by cohort
- surfaces profitability pockets by segment, region, and product
- translates analytical output into concrete operating recommendations

## 3. Project Structure
```text
revenue-analytics-unit-economics-system/
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── src/
│   ├── analysis/             # Core business analysis narrative
│   ├── dashboard_builder/    # Self-contained executive dashboard
│   ├── data_generation/      # Synthetic business data simulation
│   ├── data_profiling/       # Data profiling + quality checks
│   ├── feature_engineering/  # Customer/cohort/unit economics tables
│   ├── governance/           # Metric registry + artifact publication controls
│   ├── scenario_engine/      # Decision scenarios and reallocation logic
│   ├── validation/           # Pre-delivery QA validation
│   └── visualization/        # Publication-quality chart pack
├── data/
│   ├── raw/                  # Synthetic source tables
│   └── processed/            # Engineered analytical datasets
├── docs/
│   └── ...                   # Curated methodology and run guidance
├── tests/
│   └── ...                   # Automated validation and regression checks
├── sql/
│   └── ...                   # Reference SQL transforms (DuckDB/Postgres style)
├── outputs/
│   ├── charts/               # Chart pack (.png)
│   ├── dashboard/            # Executive HTML dashboard deliverable
│   ├── tables/               # Analysis/profiling/validation tables
│   └── reports/              # Business/reporting markdown outputs
```

## 4. Methodology
The workflow is structured as an end-to-end analytics pipeline:

1. **Data generation**
Synthetic but realistic B2B growth data across customers, transactions, and marketing spend.

2. **Data profiling and quality review**
Schema, uniqueness, null behavior, key consistency, suspicious value checks.

3. **Feature engineering**
Customer-level, cohort-level, and channel-level unit economics tables.

4. **Core analysis**
Five-section analytical narrative:
- revenue health
- revenue decomposition
- cohort retention
- unit economics
- segment/region/product profitability

5. **Visualization and dashboarding**
Executive chart pack + filterable self-contained HTML dashboard.

6. **Scenario decision engine**
Policy-based channel budget reallocation simulation to quantify estimated contribution uplift under explicit guardrails.

7. **Pre-delivery QA**
Cross-table reconciliation, formula verification, analytical integrity checks, visualization QA, and confidence rating.

## 5. Data Generation / Data Source
This portfolio project uses **synthetic data generated in Python** to simulate realistic growth dynamics from **2023-01-01 to 2025-12-31**.

Raw tables:
- `customers`
- `transactions`
- `marketing_spend`

Simulated behaviors include:
- channel-level acquisition quality differences
- segment-level revenue and transaction behavior
- product-level cost variation
- margin variability and negative-margin edge cases
- cohort churn and retention decay
- right-skewed customer revenue distribution (high-value minority)

## 6. Key Engineered Metrics
Key engineered outputs in `data/processed`:

- `customer_metrics.csv`
  - lifetime_days
  - contribution_margin
  - contribution_margin_pct
  - avg_revenue_per_transaction
  - revenue_per_day

- `cohort_table.csv`
  - customers_active
  - cohort_revenue
  - average_revenue_per_active_customer

- `unit_economics.csv`
  - CAC
  - average_LTV
  - median_LTV
  - LTV_to_CAC
  - approximate_payback_period

Assumptions and decision context are summarized in `outputs/reports/decision_brief.md`.

Decision outputs:
- `outputs/tables/scenario_reallocation_plan.csv`
- `outputs/tables/scenario_outcomes_summary.csv`
- `outputs/tables/scenario_stress_test_summary.csv`
- `outputs/tables/scenario_benchmark_by_seed.csv`
- `outputs/tables/data_catalog.csv`
- `outputs/reports/decision_brief.md`

## 7. Key Findings
From the core analytical output:

- **Revenue scale is strong**
  - Total revenue: **$54.60M**
  - Contribution margin: **$16.56M**
  - Overall contribution margin rate: **30.3%**

- **Growth is primarily volume-led**
  - Revenue decomposition indicates customer volume as the dominant driver.

- **Cohort durability weakens over time**
  - Median revenue retention: **88.4% (M3)** -> **68.3% (M6)** -> **49.6% (M12)**

- **Channel economics are highly uneven**
  - Efficient: `organic`, `referral`, `partners`
  - Inefficient: `paid_search`, `social_ads`
  - Worst channel signal: `social_ads` LTV/CAC **0.43**, payback **84.2 months**

- **Profitability pockets matter**
  - Lowest margin product: `Services` (**17.7%**)
  - Lowest margin segment: `Enterprise` (**26.2%**)

## 8. Business Recommendations
Operational recommendations from the analysis:

1. Reallocate budget away from value-destructive channels (`paid_search`, `social_ads`) toward proven efficient channels.
2. Set hard scaling guardrails: **LTV/CAC >= 3** and **payback <= 12 months** for unconstrained spend.
3. Run a focused paid-channel recovery sprint (creative, audience, landing page, bidding) with weekly stop/go criteria.
4. Launch cohort retention interventions for months 0-6 (activation and expansion plays).
5. Execute pricing and cost-to-serve review for low-margin pockets (`Services`, `Enterprise`).

## 9. Dashboard Overview
The project includes an executive-facing, single-file dashboard:

- File: `outputs/dashboard/executive_dashboard.html`
- Fully self-contained and offline-capable (embedded data + rendering logic)
- Includes:
  - executive summary strip
  - KPI pulse row
  - filter-reactive primary analysis visuals
  - diagnostic section
  - ranked risk/priority table with recommended actions
- Filters:
  - date range
  - segment
  - region
  - acquisition channel
  - product type

## 10. How to Run
```bash
# 1) Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# 2) Run full pipeline in one command (recommended)
python src/run_pipeline.py

# 3) Optional: run stages manually
python src/data_generation/generate_synthetic_data.py
python src/validation/validate_raw_data.py
python src/data_profiling/profile_raw_data.py
python src/feature_engineering/build_features.py
python src/analysis/unit_economics_analysis.py
python src/scenario_engine/build_scenarios.py
python src/scenario_engine/build_scenario_benchmark.py
MPLBACKEND=Agg python src/visualization/generate_visuals.py
python src/dashboard_builder/build_dashboard_assets.py
python src/validation/validate_final_outputs.py
python src/governance/publish_governance_artifacts.py

# 4) Run tests
pytest -q
```

Primary outputs:
- Charts: `outputs/charts/`
- Analysis tables: `outputs/tables/`
- Report outputs: `outputs/reports/`
- Dashboard: `outputs/dashboard/executive_dashboard.html`
- Decision brief: `outputs/reports/decision_brief.md`
- Metric governance registry: `outputs/reports/metric_governance_registry.md`
- Pre-delivery QA: `outputs/reports/pre_delivery_validation_report.md`
- Release governance: `outputs/reports/release_governance.md`

## 11. Limitations
- Data is synthetic; it demonstrates analytical design and decision logic, not market forecasting accuracy.
- LTV is observed contribution margin in available history, not a forward lifetime projection.
- CAC is period-level by channel and does not model full attribution lag complexity.
- Revenue decomposition is directional, not formal causal attribution.

## 12. Future Improvements
- Add forecast layer (cohort-based revenue and margin projections).
- Introduce anomaly detection and automated alerting.
- Track benchmark outcome drift across versions and synthetic seed sets.

## 13. Portfolio Value
This project demonstrates practical analytics engineering for business decision-making:
- clear business framing
- reproducible data pipeline
- strong metric definitions
- cross-functional, executive-facing communication
- pre-delivery QA discipline
