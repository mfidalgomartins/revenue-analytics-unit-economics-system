"""Profile raw datasets and produce a formal data quality review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"


@dataclass(frozen=True)
class TableSpec:
    name: str
    file_name: str
    grain: str
    candidate_keys: list[list[str]]
    date_columns: list[str]
    categorical_columns: list[str]
    likely_dimensions: list[str]
    likely_metrics: list[str]


TABLE_SPECS = [
    TableSpec(
        name="customers",
        file_name="customers.csv",
        grain="One row per customer_id",
        candidate_keys=[["customer_id"]],
        date_columns=["signup_date"],
        categorical_columns=["segment", "region", "acquisition_channel"],
        likely_dimensions=["segment", "region", "acquisition_channel", "signup_date"],
        likely_metrics=["customer_count"],
    ),
    TableSpec(
        name="transactions",
        file_name="transactions.csv",
        grain="One row per transaction_id",
        candidate_keys=[["transaction_id"]],
        date_columns=["transaction_date"],
        categorical_columns=["product_type", "customer_id"],
        likely_dimensions=["transaction_date", "product_type", "customer_id"],
        likely_metrics=["revenue", "cost", "gross_margin", "gross_margin_pct", "transaction_count"],
    ),
    TableSpec(
        name="marketing_spend",
        file_name="marketing_spend.csv",
        grain="One row per date x acquisition_channel",
        candidate_keys=[["date", "acquisition_channel"]],
        date_columns=["date"],
        categorical_columns=["acquisition_channel"],
        likely_dimensions=["date", "acquisition_channel"],
        likely_metrics=["spend"],
    ),
]

CUSTOMER_ALLOWED_SEGMENTS = {"Startup", "SMB", "Mid-Market", "Enterprise"}
CUSTOMER_ALLOWED_REGIONS = {"North America", "EMEA", "LATAM", "APAC"}
ALLOWED_CHANNELS = {"paid_search", "social_ads", "referral", "organic", "partners", "email"}
ALLOWED_PRODUCT_TYPES = {"Core", "Add-on", "Premium", "Services"}


def load_tables() -> dict[str, pd.DataFrame]:
    tables: dict[str, pd.DataFrame] = {}
    for spec in TABLE_SPECS:
        path = RAW_DIR / spec.file_name
        parse_dates = spec.date_columns if spec.date_columns else None
        tables[spec.name] = pd.read_csv(path, parse_dates=parse_dates)
    return tables


def detect_candidate_key(df: pd.DataFrame, candidate_keys: list[list[str]]) -> tuple[str, int]:
    for key_columns in candidate_keys:
        key_nulls = int(df[key_columns].isna().any(axis=1).sum())
        duplicate_key_rows = int(df.duplicated(subset=key_columns).sum())
        if key_nulls == 0 and duplicate_key_rows == 0:
            return ", ".join(key_columns), duplicate_key_rows
    fallback = ", ".join(candidate_keys[0]) if candidate_keys else "None"
    fallback_dupes = int(df.duplicated(subset=candidate_keys[0]).sum()) if candidate_keys else int(df.duplicated().sum())
    return f"{fallback} (not unique)", fallback_dupes


def build_null_profile(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    row_count = len(df)
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        rows.append(
            {
                "table_name": table_name,
                "column_name": col,
                "dtype": str(df[col].dtype),
                "null_count": null_count,
                "null_rate": (null_count / row_count) if row_count else 0.0,
            }
        )
    return pd.DataFrame(rows)


def build_cardinality_profile(table_name: str, df: pd.DataFrame, categorical_columns: list[str]) -> pd.DataFrame:
    rows = []
    row_count = len(df)
    for col in categorical_columns:
        if col not in df.columns:
            continue
        distinct_count = int(df[col].nunique(dropna=True))
        rows.append(
            {
                "table_name": table_name,
                "column_name": col,
                "distinct_count": distinct_count,
                "distinct_rate": (distinct_count / row_count) if row_count else 0.0,
            }
        )
    return pd.DataFrame(rows)


def classify_columns() -> pd.DataFrame:
    records = [
        ("customers", "customer_id", "identifier"),
        ("customers", "signup_date", "temporal_field"),
        ("customers", "segment", "dimension"),
        ("customers", "region", "dimension"),
        ("customers", "acquisition_channel", "dimension"),
        ("transactions", "transaction_id", "identifier"),
        ("transactions", "customer_id", "identifier"),
        ("transactions", "transaction_date", "temporal_field"),
        ("transactions", "revenue", "metric"),
        ("transactions", "cost", "metric"),
        ("transactions", "product_type", "dimension"),
        ("marketing_spend", "date", "temporal_field"),
        ("marketing_spend", "acquisition_channel", "dimension"),
        ("marketing_spend", "spend", "metric"),
    ]
    df = pd.DataFrame(records, columns=["table_name", "column_name", "semantic_role"])
    df["is_boolean"] = False
    df["is_text_field"] = False
    return df


def make_issue(
    table_name: str,
    column_name: str,
    check_name: str,
    severity: str,
    issue_count: int,
    row_count: int,
    description: str,
) -> dict:
    issue_rate = (issue_count / row_count) if row_count else 0.0
    return {
        "table_name": table_name,
        "column_name": column_name,
        "check_name": check_name,
        "severity": severity,
        "issue_count": int(issue_count),
        "issue_rate": issue_rate,
        "description": description,
    }


def evaluate_data_quality(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    customers = tables["customers"].copy()
    transactions = tables["transactions"].copy()
    marketing = tables["marketing_spend"].copy()

    issues: list[dict] = []

    customers_rows = len(customers)
    transactions_rows = len(transactions)
    marketing_rows = len(marketing)

    # Customers checks.
    issues.append(
        make_issue(
            "customers",
            "customer_id",
            "duplicate_customer_id",
            "high",
            int(customers.duplicated(subset=["customer_id"]).sum()),
            customers_rows,
            "customer_id should be unique at customer grain.",
        )
    )
    invalid_segments = int((~customers["segment"].isin(CUSTOMER_ALLOWED_SEGMENTS)).sum())
    issues.append(
        make_issue(
            "customers",
            "segment",
            "invalid_segment_value",
            "medium",
            invalid_segments,
            customers_rows,
            "segment contains unexpected categories.",
        )
    )
    invalid_regions = int((~customers["region"].isin(CUSTOMER_ALLOWED_REGIONS)).sum())
    issues.append(
        make_issue(
            "customers",
            "region",
            "invalid_region_value",
            "medium",
            invalid_regions,
            customers_rows,
            "region contains unexpected categories.",
        )
    )
    invalid_customer_channels = int((~customers["acquisition_channel"].isin(ALLOWED_CHANNELS)).sum())
    issues.append(
        make_issue(
            "customers",
            "acquisition_channel",
            "invalid_channel_value",
            "medium",
            invalid_customer_channels,
            customers_rows,
            "acquisition_channel contains unexpected categories.",
        )
    )

    # Transactions checks.
    issues.append(
        make_issue(
            "transactions",
            "transaction_id",
            "duplicate_transaction_id",
            "high",
            int(transactions.duplicated(subset=["transaction_id"]).sum()),
            transactions_rows,
            "transaction_id should be unique at transaction grain.",
        )
    )
    invalid_customer_fk = int((~transactions["customer_id"].isin(customers["customer_id"])).sum())
    issues.append(
        make_issue(
            "transactions",
            "customer_id",
            "orphan_customer_id",
            "high",
            invalid_customer_fk,
            transactions_rows,
            "transactions.customer_id must exist in customers.customer_id.",
        )
    )
    invalid_product_types = int((~transactions["product_type"].isin(ALLOWED_PRODUCT_TYPES)).sum())
    issues.append(
        make_issue(
            "transactions",
            "product_type",
            "invalid_product_type",
            "medium",
            invalid_product_types,
            transactions_rows,
            "product_type contains unexpected categories.",
        )
    )
    non_positive_revenue = int((transactions["revenue"] <= 0).sum())
    issues.append(
        make_issue(
            "transactions",
            "revenue",
            "non_positive_revenue",
            "high",
            non_positive_revenue,
            transactions_rows,
            "revenue should be strictly positive.",
        )
    )
    negative_cost = int((transactions["cost"] < 0).sum())
    issues.append(
        make_issue(
            "transactions",
            "cost",
            "negative_cost",
            "high",
            negative_cost,
            transactions_rows,
            "cost should not be negative.",
        )
    )
    cost_above_revenue = int((transactions["cost"] > transactions["revenue"]).sum())
    issues.append(
        make_issue(
            "transactions",
            "cost",
            "cost_exceeds_revenue",
            "medium",
            cost_above_revenue,
            transactions_rows,
            "cost > revenue indicates negative gross margin; suspicious but not impossible.",
        )
    )

    joined = transactions.merge(customers[["customer_id", "signup_date"]], on="customer_id", how="left")
    tx_before_signup = int((joined["transaction_date"] < joined["signup_date"]).sum())
    issues.append(
        make_issue(
            "transactions",
            "transaction_date",
            "transaction_before_signup",
            "high",
            tx_before_signup,
            transactions_rows,
            "transaction_date should not be earlier than the customer's signup_date.",
        )
    )

    # Marketing checks.
    issues.append(
        make_issue(
            "marketing_spend",
            "date, acquisition_channel",
            "duplicate_marketing_grain",
            "high",
            int(marketing.duplicated(subset=["date", "acquisition_channel"]).sum()),
            marketing_rows,
            "date + acquisition_channel should define a unique row.",
        )
    )
    invalid_marketing_channels = int((~marketing["acquisition_channel"].isin(ALLOWED_CHANNELS)).sum())
    issues.append(
        make_issue(
            "marketing_spend",
            "acquisition_channel",
            "invalid_channel_value",
            "medium",
            invalid_marketing_channels,
            marketing_rows,
            "acquisition_channel contains unexpected categories.",
        )
    )
    negative_spend = int((marketing["spend"] < 0).sum())
    issues.append(
        make_issue(
            "marketing_spend",
            "spend",
            "negative_spend",
            "high",
            negative_spend,
            marketing_rows,
            "marketing spend should not be negative.",
        )
    )
    zero_spend = int((marketing["spend"] == 0).sum())
    issues.append(
        make_issue(
            "marketing_spend",
            "spend",
            "zero_spend",
            "low",
            zero_spend,
            marketing_rows,
            "zero spend rows can be valid but should be reviewed for campaign inactivity.",
        )
    )

    expected_dates = pd.date_range(marketing["date"].min(), marketing["date"].max(), freq="D")
    expected_pairs = len(expected_dates) * len(ALLOWED_CHANNELS)
    missing_pairs = max(0, expected_pairs - len(marketing))
    issues.append(
        make_issue(
            "marketing_spend",
            "date, acquisition_channel",
            "missing_date_channel_pairs",
            "medium",
            missing_pairs,
            expected_pairs,
            "missing date-channel combinations can break CAC and time-series analysis.",
        )
    )

    issues_df = pd.DataFrame(issues)
    return issues_df


def summarize_tables(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for spec in TABLE_SPECS:
        df = tables[spec.name]
        candidate_pk, duplicate_pk_rows = detect_candidate_key(df, spec.candidate_keys)
        duplicate_rows = int(df.duplicated().sum())
        date_min = ""
        date_max = ""
        if spec.date_columns:
            date_col = spec.date_columns[0]
            date_min = str(df[date_col].min().date()) if pd.notna(df[date_col].min()) else ""
            date_max = str(df[date_col].max().date()) if pd.notna(df[date_col].max()) else ""

        rows.append(
            {
                "table_name": spec.name,
                "grain": spec.grain,
                "row_count": len(df),
                "column_count": len(df.columns),
                "candidate_primary_key": candidate_pk,
                "duplicate_rows": duplicate_rows,
                "duplicate_candidate_key_rows": duplicate_pk_rows,
                "date_min": date_min,
                "date_max": date_max,
                "likely_useful_dimensions": ", ".join(spec.likely_dimensions),
                "likely_useful_metrics": ", ".join(spec.likely_metrics),
            }
        )
    return pd.DataFrame(rows)


def write_quality_report(
    summary_df: pd.DataFrame,
    issues_df: pd.DataFrame,
    classifications_df: pd.DataFrame,
) -> None:
    def to_markdown_fallback(df: pd.DataFrame) -> str:
        cols = list(df.columns)
        header = "| " + " | ".join(cols) + " |"
        divider = "| " + " | ".join(["---"] * len(cols)) + " |"
        rows = []
        for rec in df.itertuples(index=False):
            rows.append("| " + " | ".join(str(value) for value in rec) + " |")
        return "\n".join([header, divider] + rows)

    issue_view = issues_df[issues_df["issue_count"] > 0].sort_values(["severity", "table_name", "check_name"])
    if issue_view.empty:
        issue_lines = "- No active issues detected from the implemented checks."
    else:
        lines = []
        for row in issue_view.itertuples(index=False):
            lines.append(
                f"- [{row.severity.upper()}] `{row.table_name}` - `{row.check_name}` "
                f"({row.column_name}): {row.issue_count:,} rows ({row.issue_rate:.2%}). {row.description}"
            )
        issue_lines = "\n".join(lines)

    counts = classifications_df["semantic_role"].value_counts()
    identifiers = int(counts.get("identifier", 0))
    dimensions = int(counts.get("dimension", 0))
    metrics = int(counts.get("metric", 0))
    temporal = int(counts.get("temporal_field", 0))

    focus_text = (
        "## Recommended Analytical Focus\n\n"
        "1. Prioritize margin-adjusted growth by channel and segment using `transactions` + `customers`.\n"
        "2. Build CAC and spend-efficiency cuts by joining `marketing_spend` to customer acquisition channel over time.\n"
        "3. Segment negative gross margin transactions (`cost > revenue`) to isolate unprofitable growth pockets.\n"
        "4. Use signup cohorts and transaction recency to evaluate retention quality before scaling paid channels.\n"
        "5. Keep key quality gates in place: transaction/customer referential integrity and channel value validation.\n"
    )

    report = (
        "# Data Quality Issues Report\n\n"
        "This report summarizes profiling and quality checks for raw datasets in the Revenue Analytics & Unit Economics System.\n\n"
        "## Data Profile Summary (High Level)\n\n"
        f"{to_markdown_fallback(summary_df)}\n\n"
        "## Data Quality Findings\n\n"
        f"{issue_lines}\n\n"
        "## Column Classification Coverage\n\n"
        f"- Identifiers: {identifiers}\n"
        f"- Dimensions: {dimensions}\n"
        f"- Metrics: {metrics}\n"
        f"- Temporal fields: {temporal}\n"
        "- Booleans: 0\n"
        "- Text fields: 0\n\n"
        f"{focus_text}"
    )
    (REPORTS_DIR / "data_quality_issues_report.md").write_text(report, encoding="utf-8")
    (REPORTS_DIR / "recommended_analytical_focus.md").write_text(focus_text, encoding="utf-8")


def run() -> None:
    OUTPUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    tables = load_tables()
    summary_df = summarize_tables(tables)
    issues_df = evaluate_data_quality(tables)
    classifications_df = classify_columns()

    null_profiles = []
    cardinality_profiles = []
    for spec in TABLE_SPECS:
        df = tables[spec.name]
        null_profiles.append(build_null_profile(spec.name, df))
        cardinality_profiles.append(
            build_cardinality_profile(spec.name, df, spec.categorical_columns)
        )

    null_profile_df = pd.concat(null_profiles, ignore_index=True)
    cardinality_df = pd.concat(cardinality_profiles, ignore_index=True)

    summary_df.to_csv(OUTPUT_TABLES_DIR / "data_profile_summary.csv", index=False)
    null_profile_df.to_csv(OUTPUT_TABLES_DIR / "null_profile_by_column.csv", index=False)
    cardinality_df.to_csv(OUTPUT_TABLES_DIR / "categorical_cardinality_profile.csv", index=False)
    issues_df.to_csv(OUTPUT_TABLES_DIR / "data_quality_issues.csv", index=False)
    classifications_df.to_csv(OUTPUT_TABLES_DIR / "column_classification.csv", index=False)

    write_quality_report(summary_df, issues_df, classifications_df)

    print("Profiling and data quality review completed.")
    print(f"summary_table: {OUTPUT_TABLES_DIR / 'data_profile_summary.csv'}")
    print(f"null_profile: {OUTPUT_TABLES_DIR / 'null_profile_by_column.csv'}")
    print(f"quality_issues: {OUTPUT_TABLES_DIR / 'data_quality_issues.csv'}")
    print(f"classification: {OUTPUT_TABLES_DIR / 'column_classification.csv'}")
    print(f"report: {REPORTS_DIR / 'data_quality_issues_report.md'}")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
