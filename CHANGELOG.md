# Changelog

All notable changes to this project are documented in this file.

## [1.0.0] - 2026-04-02
### Added
- Metric contract tests for deterministic golden aggregates.
- Dashboard KPI snapshot parity tests.
- Multi-scenario stress testing output (`best_case`, `base_case`, `worst_case`).
- Data catalog artifacts with ownership and business-use mapping.
- QA checks for dashboard size and payload performance budgets.
- Multi-seed scenario benchmark pack (`outputs/tables/scenario_benchmark_by_seed.csv`).
- Release governance artifacts (`VERSION`, release manifest, release policy report).
- Tag-triggered GitHub release workflow.

### Changed
- Governance publication now refreshes upgrade and diagnostic reports automatically.
- Validation now verifies scenario stress outputs and monotonicity assumptions.
