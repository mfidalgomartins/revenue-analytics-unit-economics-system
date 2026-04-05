# Project Execution Plan

## Objective
Determine whether top-line revenue growth is economically sustainable by linking growth to contribution margins, acquisition efficiency, and retention behavior.

## Stage Plan

### Stage 0 - Environment and Structure Setup
- Confirm folder layout and package boundaries.
- Install dependencies from `requirements.txt`.

Expected outputs:
- repository structure ready for reproducible analytics work

### Stage 1 - Synthetic Data Generation (Current Implemented Stage)
- Generate `customers`, `transactions`, and `marketing_spend` synthetic datasets.
- Encode realistic business behavior: channel-quality differences, margin variation, churn, skewed revenue distribution, and high-value cohorts.
- Save raw files to `data/raw`.

Expected outputs:
- `data/raw/customers.csv`
- `data/raw/transactions.csv`
- `data/raw/marketing_spend.csv`
- synthetic data note in `docs/synthetic_data_generation_note.md`

### Stage 2 - Data Validation
- Validate schema, null rates, duplicates, value ranges, and date consistency.
- Flag suspicious observations and data quality risks.

Expected outputs:
- validation summary table in `outputs/tables`
- validation logs in `docs` or `outputs/tables`

### Stage 3 - Data Profiling
- Profile distributions and anomalies across segments/channels/products.
- Assess transaction concentration and customer heterogeneity.

Expected outputs:
- profiling tables and histograms in `outputs/tables` and `outputs/charts`

### Stage 4 - Feature Engineering
- Build customer-level and cohort-level features (e.g., CAC proxy, gross margin per customer, payback periods, retention proxies).
- Save curated modeling/analysis tables to `data/processed`.

Expected outputs:
- processed feature tables in `data/processed`

### Stage 5 - Unit Economics Analysis
- Compute growth quality KPIs by segment/channel/region.
- Evaluate sustainable growth via margin-adjusted growth lenses.

Expected outputs:
- analytical KPI tables in `outputs/tables`
- narrative summary in `docs`

### Stage 6 - Visualization and Dashboard Assets
- Build production-ready chart assets and dashboard-ready extracts.

Expected outputs:
- chart exports in `outputs/charts`
- dashboard tables/files in `dashboard`

### Stage 7 - Scenario Decision Engine
- Build budget-reallocation scenario to prioritize efficient channels and de-risk inefficient growth.
- Keep total budget constant and estimate directional contribution uplift.
- Run stress-case overlays (`best_case`, `base_case`, `worst_case`) with CAC and LTV shocks.
- Run multi-seed benchmark pack to test policy stability against synthetic draw variance.

Expected outputs:
- `outputs/tables/scenario_reallocation_plan.csv`
- `outputs/tables/scenario_outcomes_summary.csv`
- `outputs/tables/scenario_stress_test_summary.csv`
- `outputs/tables/scenario_benchmark_by_seed.csv`
- `outputs/reports/scenario_decision_engine_report.md`
- `outputs/reports/scenario_benchmark_report.md`

### Stage 8 - Governance Publication
- Publish metric governance registry.
- Publish lightweight data catalog with ownership and business purpose.
- Publish upgrade/diagnostic status artifacts.
- Publish release governance artifacts (semantic version + changelog alignment).
- Synchronize canonical reports to docs mirror to avoid documentation drift.

Expected outputs:
- `outputs/reports/metric_governance_registry.md`
- `outputs/tables/data_catalog.csv`
- `outputs/reports/data_catalog.md`
- `outputs/reports/final_upgrades_needed.md`
- `outputs/reports/total_perfection_diagnostic.md`
- `outputs/tables/release_manifest.csv`
- `outputs/reports/release_governance.md`
- synchronized `docs/*.md` mirrors

## Script Execution Order
Preferred orchestration:
1. `src/run_pipeline.py`

Manual order:
1. `src/data_generation/generate_synthetic_data.py`
2. `src/validation/validate_raw_data.py`
3. `src/data_profiling/profile_raw_data.py`
4. `src/feature_engineering/build_features.py`
5. `src/analysis/unit_economics_analysis.py`
6. `src/scenario_engine/build_scenarios.py`
7. `src/scenario_engine/build_scenario_benchmark.py`
8. `src/visualization/generate_visuals.py`
9. `src/dashboard_builder/build_dashboard_assets.py`
10. `src/validation/validate_final_outputs.py`
11. `src/governance/publish_governance_artifacts.py`

## Governance Notes
- Keep random seeds fixed in synthetic generation for reproducibility.
- Use idempotent scripts where possible.
- Separate raw, processed, and output artifacts to preserve lineage.
