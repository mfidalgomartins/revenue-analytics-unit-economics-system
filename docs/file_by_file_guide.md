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

## Notebooks
- `notebooks/`: ad-hoc exploration and stakeholder narrative notebooks.

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
- `src/governance/publish_governance_artifacts.py`: publishes governance artifacts and syncs canonical reports into `docs/`.

## Tests and Automation
- `tests/`: automated checks for feature engineering, raw validation, core analysis, governance policy, scenarios, metric contracts, and dashboard KPI snapshot parity.
- `.github/workflows/ci.yml`: CI workflow running the full pipeline and tests on push/PR.

## Outputs
- `outputs/charts/`: generated static chart files.
- `outputs/tables/`: generated analytical and validation tables.
- `outputs/tables/data_profile_summary.csv`: table-level profiling summary (grain, keys, row/column counts, date coverage).
- `outputs/tables/null_profile_by_column.csv`: null count and null rate by column.
- `outputs/tables/categorical_cardinality_profile.csv`: distinct counts/rates for key categorical fields.
- `outputs/tables/data_quality_issues.csv`: formal issue list with severity, issue counts, and descriptions.
- `outputs/tables/column_classification.csv`: identifier/dimension/metric/temporal/boolean/text semantic mapping.
- `outputs/tables/scenario_reallocation_plan.csv`: channel-level scenario recommendation and estimated impact.
- `outputs/tables/scenario_outcomes_summary.csv`: scenario-level aggregate outcome summary.
- `outputs/tables/scenario_stress_test_summary.csv`: best/base/worst stress outcomes under CAC and LTV shocks.
- `outputs/tables/scenario_benchmark_by_seed.csv`: benchmark stability table across predefined synthetic seeds.
- `outputs/tables/data_catalog.csv`: field-level catalog with role, owner, and business use.
- `outputs/reports/data_catalog.md`: summary note for governance data catalog.
- `outputs/tables/release_manifest.csv`: semantic version and changelog alignment manifest.
- `outputs/reports/release_governance.md`: release governance policy and current-version status.

## Dashboard
- `dashboard/`: dashboard code/config/export files for BI presentation.

## Docs
- `docs/project_execution_plan.md`: end-to-end implementation and run-order plan.
- `docs/synthetic_data_generation_note.md`: assumptions and simulated business behaviors.
- `docs/data_quality_issues_report.md`: narrative data quality review and profiling summary.
- `docs/recommended_analytical_focus.md`: post-profiling analytical priorities.
- `docs/final_upgrades_needed.md`: exceptional-level upgrade checklist and priority plan.
- `docs/metric_governance_registry.md`: canonical metric and threshold governance specification.
- `docs/scenario_decision_engine_report.md`: scenario assumptions and recommended allocation outcomes.
