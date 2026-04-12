"""Generate a lightweight business-facing data catalog for governance."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROC_DIR = PROJECT_ROOT / "data" / "processed"
OUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"

DATASETS = [
    ("raw", "customers", RAW_DIR / "customers.csv"),
    ("raw", "transactions", RAW_DIR / "transactions.csv"),
    ("raw", "marketing_spend", RAW_DIR / "marketing_spend.csv"),
    ("processed", "customer_metrics", PROC_DIR / "customer_metrics.csv"),
    ("processed", "cohort_table", PROC_DIR / "cohort_table.csv"),
    ("processed", "unit_economics", PROC_DIR / "unit_economics.csv"),
    ("output", "monthly_revenue_health", OUT_TABLES_DIR / "monthly_revenue_health.csv"),
    ("output", "main_analysis_findings", OUT_TABLES_DIR / "main_analysis_findings.csv"),
]

FIELD_DEFINITIONS: dict[str, tuple[str, str]] = {
    "customer_id": (
        "Unique customer identifier.",
        "Join key across customer and transaction-level views.",
    ),
    "transaction_id": (
        "Unique transaction identifier.",
        "Traceability and duplicate-control for transactional facts.",
    ),
    "revenue": ("Gross revenue booked on each transaction.", "Top-line growth and mix analysis."),
    "cost": ("Direct delivery cost linked to each transaction.", "Contribution margin and unit economics."),
    "contribution_margin": (
        "Revenue minus direct cost.",
        "Primary profitability measure for sustainable growth decisions.",
    ),
    "contribution_margin_pct": (
        "Contribution margin divided by revenue.",
        "Margin quality signal for trend and segment diagnostics.",
    ),
    "CAC": (
        "Customer acquisition cost by channel: total spend divided by customers acquired.",
        "Channel efficiency and budget reallocation decisions.",
    ),
    "LTV_to_CAC": (
        "Lifetime value to CAC ratio by channel.",
        "Scaling guardrail to avoid unprofitable growth.",
    ),
    "approximate_payback_period": (
        "Estimated months to recover CAC using observed contribution margin.",
        "Capital efficiency and risk prioritization.",
    ),
}

LAYER_OWNER = {
    "raw": "Data Engineering",
    "processed": "Analytics Engineering",
    "output": "Analytics Lead",
}


def _infer_role(column: str, dtype: str) -> str:
    c = column.lower()
    if c.endswith("_id") or c in {"cid"}:
        return "identifier"
    if "date" in c or "month" in c:
        return "temporal"
    if c.startswith("is_") or c.startswith("has_"):
        return "boolean"
    if "float" in dtype or "int" in dtype:
        return "metric"
    return "dimension"


def build_data_catalog() -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for layer, dataset, path in DATASETS:
        if not path.exists():
            continue
        frame = pd.read_csv(path, nrows=200)
        for col, dtype in frame.dtypes.items():
            definition, business_use = FIELD_DEFINITIONS.get(
                col,
                (
                    f"{dataset}.{col} field in {layer} layer.",
                    "Operationalized in profiling, analysis, or dashboarding workflows.",
                ),
            )
            rows.append(
                {
                    "layer": layer,
                    "dataset": dataset,
                    "column": col,
                    "dtype": str(dtype),
                    "role": _infer_role(col, str(dtype)),
                    "owner": LAYER_OWNER[layer],
                    "definition": definition,
                    "business_use": business_use,
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["layer", "dataset", "column"], ignore_index=True
    )


def write_data_catalog_artifacts() -> None:
    OUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)

    catalog = build_data_catalog()
    catalog.to_csv(OUT_TABLES_DIR / "data_catalog.csv", index=False)
