# Main Analysis Notebook Section

This section provides the core analytical narrative for the Revenue Analytics & Unit Economics System.

## 1. Overall Revenue Health
**Question being answered**: Is top-line revenue scaling with improving or deteriorating contribution quality over time?
**Metrics used**: Monthly total_revenue, total_cost, contribution_margin, contribution_margin_pct, monthly growth rates, early-vs-recent 6-month averages
**Result**: Average monthly revenue increased from $292,739 to $2,807,397 (859.0%), while cost increased from $205,676 to $1,951,097 (848.6%). Contribution margin increased 883.5% with latest monthly revenue CAGR around 11.7%.
**Business interpretation**: Revenue is growing in absolute terms, but sustainability depends on whether margin growth keeps pace with spend-driven volume expansion.
**Caveats**: Trends are based on synthetic data and observed period windows; growth rates can be sensitive to chosen comparison window.

## 2. Revenue Decomposition
**Question being answered**: Is revenue growth primarily driven by customer volume, per-customer monetization, or customer-mix shifts?
**Metrics used**: Revenue decomposition between first and last 6 months: customer_volume_effect, average_revenue_effect, mix_effect (segment-mix), residual
**Result**: Revenue changed by $15,087,948 between comparison windows. Volume effect: $10,349,685, average revenue effect: $3,771,454, mix effect: $966,809. Dominant driver: customer_volume_effect.
**Business interpretation**: Growth quality is stronger when monetization and favorable mix support growth; volume-only growth with weak unit economics is less sustainable.
**Caveats**: Decomposition compares aggregated windows and uses segment as the mix dimension; other mix definitions (region/product/channel) may yield different allocations.

## 3. Cohort Analysis
**Question being answered**: Are cohorts retaining activity and revenue over time, or decaying in a way that weakens growth quality?
**Metrics used**: Cohort activity retention and revenue retention at months 3, 6, 12; share of cohorts with month-6 revenue retention > 100%
**Result**: Median activity retention: M3 81.7%, M6 65.1%, M12 42.4%. Median revenue retention: M3 88.4%, M6 68.3%, M12 49.6%. Cohorts with M6 revenue expansion (>100%): 16.7%.
**Business interpretation**: Stable or expanding revenue retention suggests healthy post-acquisition monetization; declining activity retention indicates potential dependency on ongoing acquisition to sustain growth.
**Caveats**: Later-month retention metrics include only mature cohorts; newer cohorts are excluded from long-horizon reads. Cohort decay is visible between M3 and M6.

## 4. Unit Economics
**Question being answered**: Which acquisition channels create efficient growth versus value-destructive growth?
**Metrics used**: CAC, average_LTV, median_LTV, LTV_to_CAC, approximate_payback_period
**Result**: Efficient channels: organic, referral, partners. Inefficient channels: paid_search, social_ads. Best LTV/CAC: organic (20.33), worst: social_ads (0.43).
**Business interpretation**: Channel allocation should prioritize high LTV/CAC and faster payback channels; low-ratio channels likely drive unprofitable growth unless economics improve.
**Caveats**: Unit economics use observed LTV and period-wide spend allocation; attribution and lag effects can alter real-world channel economics. Classification thresholds: efficient when LTV/CAC >= 3.0 and payback <= 12 months.

## 5. Segment Profitability
**Question being answered**: Which segments, regions, and products generate profitable growth, and where are low-margin growth pockets concentrated?
**Metrics used**: Total revenue, total cost, contribution margin, margin_pct, revenue_share by segment/region/product_type
**Result**: Lowest margin segment: Enterprise (26.2%); lowest margin region: LATAM (29.9%); lowest margin product: Services (17.7%). Low-margin growth pockets identified: 1.
**Business interpretation**: Growth concentration in low-margin pockets can inflate revenue while suppressing value creation. Commercial strategy should adjust pricing/mix/cost discipline in weak-margin slices.
**Caveats**: Segment and region profitability use customer-level aggregated costs/revenue, while product profitability is transaction-level; direct comparisons should consider grain differences.

## Structured Outputs
- `outputs/tables/monthly_revenue_health.csv`
- `outputs/tables/revenue_decomposition_effects.csv`
- `outputs/tables/cohort_retention_summary.csv`
- `outputs/tables/unit_economics_channel_diagnostics.csv`
- `outputs/tables/segment_profitability.csv`
- `outputs/tables/region_profitability.csv`
- `outputs/tables/product_profitability.csv`
- `outputs/tables/low_margin_growth_pockets.csv`
- `outputs/tables/main_analysis_findings.csv`
