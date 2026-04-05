# Dashboard Build Note

## Layout Choices
- Designed as a single-file executive dashboard for offline review in leadership meetings.
- Prioritized scanability: summary strip -> KPI pulse -> primary analysis -> diagnostics -> risk ranking.
- Primary section focuses on growth sustainability tests (trend quality, retention durability, channel economics).
- Diagnostic section isolates structural drivers (segment/region margins, ticket size, customer concentration).
- Risk table is ranked and action-oriented to support weekly planning and budget steering.

## Technical Choices
- No external dependencies; all data and rendering logic are embedded for offline use.
- Uses a lightweight internal SVG rendering layer for charts to keep the file self-contained.
- Filters (date, segment, region, channel, product) propagate to major visuals and KPI calculations.
- Tables are sortable in-browser for fast triage.
- Threshold policy is embedded from the canonical metric registry to keep classification consistent across stack.
- Payload metadata is deterministic (`data_fingerprint`) to reduce reproducibility drift.
