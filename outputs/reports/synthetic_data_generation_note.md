# Synthetic Data Generation Note

The synthetic data generation layer simulates a B2B company from 2023-01-01 to 2025-12-31.

Simulated business behavior:
- Acquisition channels produce different customer quality and retention levels.
- Segment mix by channel affects average order value and transaction frequency.
- Revenue is intentionally right-skewed to reflect long-tail customer spending.
- A small high-value customer group produces occasional outsized transactions.
- Lower-quality customers churn faster and show lower-value orders.
- Product and channel combinations create margin variation, including some unprofitable transactions.

Generated scale:
- Customers: 9,000
- Transactions: 69,950
- Average gross margin: 30.3%
- Simulation seed: 42
