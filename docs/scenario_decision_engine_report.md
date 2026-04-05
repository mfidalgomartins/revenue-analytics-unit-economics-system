# Scenario Decision Engine Report

## Scenario
- Name: `budget_reallocation_v1`
- Policy: cut inefficient channels, hold borderline channels, and reallocate to efficient channels while keeping total budget constant.

## Governance Thresholds Used
- Efficient: `LTV/CAC >= 3.0` and `payback <= 12.0 months`
- Inefficient: `LTV/CAC < 1.0` or `payback > 24.0 months`

## Estimated Outcome
- Baseline total budget: `$5,552,234.85`
- Scenario total budget: `$5,552,234.85`
- Baseline estimated contribution: `$16,564,031.92`
- Scenario estimated contribution: `$36,877,987.20`
- Estimated contribution uplift: `$20,313,955.28`

## Stress Test (CAC and LTV shocks)
| scenario_name | CAC shock | LTV shock | scenario contribution | uplift vs baseline | uplift vs base case |
| --- | --- | --- | --- | --- | --- |
| best_case | 0.90x | 1.08x | $44,253,584.64 | $27,689,552.72 | $7,375,597.44 |
| base_case | 1.00x | 1.00x | $36,877,987.20 | $20,313,955.28 | $0.00 |
| worst_case | 1.15x | 0.88x | $28,219,677.16 | $11,655,645.24 | $-8,658,310.04 |

## Interpretation
- This is a policy simulation, not a forecast.
- Estimates assume channel CAC and average LTV remain stable under spend changes.
- Use as directional decision support for budget steering and experimentation priorities.
