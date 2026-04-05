# Data Catalog

This catalog documents field ownership, role, and business purpose across raw, processed, and output layers.

## Coverage Summary
- Total cataloged fields: 57
- Raw fields: 14
- Processed fields: 27
- Output fields: 16

## Dataset Field Counts
| dataset | field_count |
| --- | --- |
| customer_metrics | 14 |
| monthly_revenue_health | 10 |
| unit_economics | 8 |
| main_analysis_findings | 6 |
| transactions | 6 |
| cohort_table | 5 |
| customers | 5 |
| marketing_spend | 3 |

## Owner Model
- Data Engineering owns raw ingestion contracts and schema stability.
- Analytics Engineering owns processed semantic tables and metric definitions.
- Analytics Lead owns decision-facing output artifacts and business interpretation guardrails.

## Full Catalog File
- `outputs/tables/data_catalog.csv`