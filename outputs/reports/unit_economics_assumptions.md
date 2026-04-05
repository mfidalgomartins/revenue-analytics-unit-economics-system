# Unit Economics Assumptions

## CAC Assumption
`CAC` is computed at acquisition channel level as:

`CAC = total_channel_marketing_spend / customers_acquired_in_channel`

Interpretation: average paid acquisition cost per customer over the full observed period.

## LTV Assumption
`LTV` is defined as observed contribution margin per customer during available history:

`LTV = total_revenue - total_cost`

Channel-level fields:
- `average_LTV`: mean LTV across all customers acquired via channel.
- `median_LTV`: median LTV across all customers acquired via channel.

Interpretation: realized economic value contribution, not projected lifetime value beyond observed data.

## Payback Assumption
`approximate_payback_period` is estimated in months using:

`approximate_payback_period = CAC / avg_monthly_contribution_margin_per_customer`

where:

`avg_monthly_contribution_margin_per_customer = (total_channel_contribution_margin / observed_months) / customers_acquired`

If `avg_monthly_contribution_margin_per_customer <= 0`, payback is set to null (not economically meaningful under current observations).
