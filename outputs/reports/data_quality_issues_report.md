# Data Quality Issues Report

This report summarizes profiling and quality checks for raw datasets in the Revenue Analytics & Unit Economics System.

## Data Profile Summary (High Level)

| table_name | grain | row_count | column_count | candidate_primary_key | duplicate_rows | duplicate_candidate_key_rows | date_min | date_max | likely_useful_dimensions | likely_useful_metrics |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| customers | One row per customer_id | 9000 | 5 | customer_id | 0 | 0 | 2023-01-01 | 2025-12-31 | segment, region, acquisition_channel, signup_date | customer_count |
| transactions | One row per transaction_id | 69950 | 6 | transaction_id | 0 | 0 | 2023-01-03 | 2025-12-31 | transaction_date, product_type, customer_id | revenue, cost, gross_margin, gross_margin_pct, transaction_count |
| marketing_spend | One row per date x acquisition_channel | 6576 | 3 | date, acquisition_channel | 0 | 0 | 2023-01-01 | 2025-12-31 | date, acquisition_channel | spend |

## Data Quality Findings

- [MEDIUM] `transactions` - `cost_exceeds_revenue` (cost): 258 rows (0.37%). cost > revenue indicates negative gross margin; suspicious but not impossible.

## Column Classification Coverage

- Identifiers: 3
- Dimensions: 5
- Metrics: 3
- Temporal fields: 3
- Booleans: 0
- Text fields: 0

## Recommended Analytical Focus

1. Prioritize margin-adjusted growth by channel and segment using `transactions` + `customers`.
2. Build CAC and spend-efficiency cuts by joining `marketing_spend` to customer acquisition channel over time.
3. Segment negative gross margin transactions (`cost > revenue`) to isolate unprofitable growth pockets.
4. Use signup cohorts and transaction recency to evaluate retention quality before scaling paid channels.
5. Keep key quality gates in place: transaction/customer referential integrity and channel value validation.
