# Scenario Benchmark Report

## Scope
- Seeds benchmarked: `7, 21, 42, 84, 126`
- Per-seed workflow: data generation -> feature engineering -> scenario decision engine
- Baseline model restored to seed `42` after benchmark completion.

## Uplift Stability Summary
- Mean estimated uplift: `$19,593,091.26`
- Median estimated uplift: `$19,486,132.12`
- Min estimated uplift: `$18,492,825.07`
- Max estimated uplift: `$20,620,885.72`
- Std deviation: `$786,280.12`
- Positive uplift rate: `100.0%`

## Interpretation
- Benchmarking indicates how sensitive the policy engine is to synthetic draw variation.
- Directional consistency across seeds supports stronger interview defensibility.

## Output Files
- `outputs/tables/scenario_benchmark_by_seed.csv`
- `outputs/reports/scenario_benchmark_report.md`