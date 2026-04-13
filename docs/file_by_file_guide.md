# File-by-File Guide

## Root
- `README.md`: project context, scope, and quick-start commands.
- `CHANGELOG.md`: change history for release and version governance.
- `VERSION`: canonical semantic project version.
- `requirements.txt`: Python dependencies for baseline pipeline execution.
- `requirements-dev.txt`: development dependencies (baseline + testing).
- `Makefile`: shortcuts for setup, full run, and test execution.
- `pytest.ini`: test discovery and project import settings.

## Data Folders
- `data/raw/`: immutable raw synthetic source tables.
- `data/processed/`: cleaned, joined, and feature-engineered data artifacts.

## Source Modules
- `src/run_pipeline.py`: orchestrates full stage-by-stage pipeline execution.
- `src/data_generation/generate_synthetic_data.py`: creates reproducible synthetic business datasets.
- `src/validation/validate_raw_data.py`: schema and quality checks for raw tables.
- `src/data_profiling/profile_raw_data.py`: formal profiling and data quality review, including summary/output report generation.
- `src/feature_engineering/build_features.py`: customer/cohort/channel feature creation.
- `src/analysis/unit_economics_analysis.py`: profitability and sustainable growth analysis.
- `src/scenario_engine/build_scenarios.py`: decision engine for channel budget reallocation scenarios.
- `src/scenario_engine/build_scenario_benchmark.py`: multi-seed scenario benchmark pack for stability and defensibility.
- `src/visualization/generate_visuals.py`: chart creation and export.
- `src/dashboard_builder/build_dashboard_assets.py`: prepares dashboard-consumable datasets.
- `src/dashboard_builder/kpi_snapshot.py`: deterministic KPI snapshot logic used for dashboard parity tests.
- `src/governance/metric_registry.py`: canonical threshold policy and risk scoring registry.
- `src/governance/data_catalog.py`: builds lightweight field-level data catalog with owner and business use.
- `src/governance/release_governance.py`: semantic version and changelog governance checks/artifacts.
- `src/governance/publish_governance_artifacts.py`: publishes governance artifacts used by validation and release checks.

## Tests and Automation
- `tests/`: automated checks for feature engineering, raw validation, core analysis, governance policy, scenarios, metric contracts, and dashboard KPI snapshot parity.
- `.github/workflows/ci.yml`: CI workflow running the full pipeline and tests on push/PR.

## Outputs
- `outputs/charts/`: generated static chart files.
- `outputs/tables/`: generated analytical and validation tables.
- `outputs/tables/data_profile_summary.csv`: table-level profiling summary (grain, keys, row/column counts, date coverage).
- `outputs/tables/data_quality_issues.csv`: formal issue list with severity, issue counts, and descriptions.
- `outputs/tables/scenario_reallocation_plan.csv`: channel-level scenario recommendation and estimated impact.
- `outputs/tables/scenario_outcomes_summary.csv`: scenario-level aggregate outcome summary.
- `outputs/tables/scenario_stress_test_summary.csv`: best/base/worst stress outcomes under CAC and LTV shocks.
- `outputs/tables/scenario_benchmark_by_seed.csv`: benchmark stability table across predefined synthetic seeds.
- `outputs/tables/data_catalog.csv`: field-level catalog with role, owner, and business use.
- `outputs/reports/decision_brief.md`: consolidated executive brief with findings, scenario impact, and recommendations.
- `outputs/tables/release_manifest.csv`: semantic version and changelog alignment manifest.
- `outputs/reports/release_governance.md`: release governance policy and current-version status.

## SQL
- `sql/`: reference SQL transforms for core analytical tables (DuckDB-style reference logic).

## Dashboard
- `outputs/dashboard/`: executive dashboard export artifacts for BI presentation.

## Docs
- `docs/README.md`: curated documentation index and reading path.
- `docs/project_execution_plan.md`: end-to-end implementation and run-order plan.
