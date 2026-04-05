"""Build a self-contained executive HTML dashboard with embedded data."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

if str(Path(__file__).resolve().parents[2]) not in sys.path:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.governance.metric_registry import to_payload_dict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    customers = pd.read_csv(RAW_DIR / "customers.csv", parse_dates=["signup_date"])
    transactions = pd.read_csv(RAW_DIR / "transactions.csv", parse_dates=["transaction_date"])
    marketing = pd.read_csv(RAW_DIR / "marketing_spend.csv", parse_dates=["date"])
    return customers, transactions, marketing


def build_embedded_payload(
    customers: pd.DataFrame,
    transactions: pd.DataFrame,
    marketing: pd.DataFrame,
) -> dict:
    tx = transactions.copy()

    tx_records = []
    for row in tx.itertuples(index=False):
        tx_records.append(
            {
                "d": pd.Timestamp(row.transaction_date).strftime("%Y-%m-%d"),
                "cid": row.customer_id,
                "prod": row.product_type,
                "rev": round(float(row.revenue), 2),
                "cost": round(float(row.cost), 2),
            }
        )

    customer_records = []
    for row in customers.itertuples(index=False):
        customer_records.append(
            {
                "cid": row.customer_id,
                "sd": pd.Timestamp(row.signup_date).strftime("%Y-%m-%d"),
                "seg": row.segment,
                "reg": row.region,
                "ch": row.acquisition_channel,
            }
        )

    marketing_records = []
    for row in marketing.itertuples(index=False):
        marketing_records.append(
            {
                "d": pd.Timestamp(row.date).strftime("%Y-%m-%d"),
                "ch": row.acquisition_channel,
                "spend": round(float(row.spend), 2),
            }
        )

    coverage_start = min(min(t["d"] for t in tx_records), min(m["d"] for m in marketing_records))
    coverage_end = max(max(t["d"] for t in tx_records), max(m["d"] for m in marketing_records))

    payload = {
        "meta": {
            "project_name": "Revenue Analytics & Unit Economics System",
            "dashboard_title": "Executive Growth Quality Dashboard",
            "question": "Is the company growing sustainably, or is it relying on unprofitable growth?",
            "coverage_start": coverage_start,
            "coverage_end": coverage_end,
            "data_fingerprint": int(
                int(pd.util.hash_pandas_object(customers.assign(_table="customers")).sum())
                + int(pd.util.hash_pandas_object(transactions.assign(_table="transactions")).sum())
                + int(pd.util.hash_pandas_object(marketing.assign(_table="marketing")).sum())
            ),
            "values": {
                "segments": sorted(customers["segment"].dropna().unique().tolist()),
                "regions": sorted(customers["region"].dropna().unique().tolist()),
                "acquisition_channels": sorted(
                    customers["acquisition_channel"].dropna().unique().tolist()
                ),
                "product_types": sorted(transactions["product_type"].dropna().unique().tolist()),
            },
            "metric_policy": to_payload_dict(),
        },
        "customers": customer_records,
        "transactions": tx_records,
        "marketing_spend": marketing_records,
    }
    return payload


def build_dashboard_html(payload: dict) -> str:
    data_json = json.dumps(payload, separators=(",", ":"))

    template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Executive Growth Quality Dashboard</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7fb;
      --panel: #ffffff;
      --panel-soft: #f8fafc;
      --ink: #0f172a;
      --sub: #475569;
      --line: #d6dde8;
      --line-soft: #e2e8f0;
      --brand: #1d4ed8;
      --good: #059669;
      --bad: #b91c1c;
      --warn: #a16207;
      --rev: #0b4f6c;
      --cost: #c44536;
      --margin: #2a9d8f;
      --accent: #ffb703;
      --bar: #264653;
      --header-grad-a: #ffffff;
      --header-grad-b: #eef2ff;
      --chip-bg: #eef2ff;
      --chip-border: #c7d2fe;
      --chip-ink: #3730a3;
      --control-bg: #ffffff;
      --control-border: #cbd5e1;
      --table-head-bg: #f8fafc;
      --table-row-hover: #f8fafc;
      --chart-grid: #e5e7eb;
      --chart-axis: #94a3b8;
      --chart-text: #334155;
      --chart-muted: #64748b;
      --tooltip-bg: rgba(15, 23, 42, 0.92);
      --shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
    }

    body[data-theme="dark"] {
      color-scheme: dark;
      --bg: #081224;
      --panel: #0f1d33;
      --panel-soft: #132640;
      --ink: #e6edf8;
      --sub: #a9bbd6;
      --line: #203a5f;
      --line-soft: #29466e;
      --brand: #60a5fa;
      --good: #34d399;
      --bad: #f87171;
      --warn: #fbbf24;
      --rev: #7dd3fc;
      --cost: #fca5a5;
      --margin: #5eead4;
      --accent: #fcd34d;
      --bar: #93c5fd;
      --header-grad-a: #0f1d33;
      --header-grad-b: #142744;
      --chip-bg: #172e50;
      --chip-border: #2d4f7b;
      --chip-ink: #dbeafe;
      --control-bg: #12243d;
      --control-border: #345680;
      --table-head-bg: #12243d;
      --table-row-hover: #122a49;
      --chart-grid: #2a4569;
      --chart-axis: #6f8fb5;
      --chart-text: #c6d6ee;
      --chart-muted: #8ea8ca;
      --tooltip-bg: rgba(2, 6, 23, 0.96);
      --shadow: 0 8px 24px rgba(2, 6, 23, 0.45);
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      background: var(--bg);
      color: var(--ink);
      transition: background 180ms ease, color 180ms ease;
    }

    .container {
      width: min(1400px, 96vw);
      margin: 20px auto 48px;
      display: grid;
      gap: 14px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 12px;
      box-shadow: var(--shadow);
      padding: 16px;
    }

    .header-panel {
      display: grid;
      gap: 14px;
      background: linear-gradient(145deg, var(--header-grad-a), var(--header-grad-b));
    }

    .header-top {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      flex-wrap: wrap;
    }

    h1 {
      margin: 0;
      font-size: 28px;
      line-height: 1.2;
      color: var(--ink);
    }

    .subtitle {
      margin-top: 4px;
      color: var(--sub);
      font-size: 15px;
      max-width: 900px;
    }

    .header-tools {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .meta-chip {
      background: var(--chip-bg);
      border: 1px solid var(--chip-border);
      color: var(--chip-ink);
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
      white-space: nowrap;
    }

    .theme-btn {
      border: 1px solid var(--chip-border);
      background: var(--panel);
      color: var(--ink);
      border-radius: 999px;
      padding: 6px 11px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
    }

    .theme-btn:hover {
      background: var(--panel-soft);
    }

    .filter-grid {
      display: grid;
      grid-template-columns: repeat(6, minmax(140px, 1fr));
      gap: 10px;
      align-items: end;
    }

    .filter-group label {
      display: block;
      font-size: 12px;
      color: var(--sub);
      margin-bottom: 4px;
      font-weight: 600;
    }

    input[type="date"], select {
      width: 100%;
      border: 1px solid var(--control-border);
      border-radius: 8px;
      padding: 7px 8px;
      font-size: 13px;
      background: var(--control-bg);
      color: var(--ink);
    }

    select[multiple] {
      min-height: 82px;
      padding: 6px;
    }

    .filter-actions {
      display: flex;
      gap: 8px;
      align-items: center;
    }

    .btn {
      border: 1px solid var(--control-border);
      background: var(--panel-soft);
      color: var(--ink);
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
    }

    .btn:hover { background: var(--control-bg); }

    .summary-strip {
      display: grid;
      grid-template-columns: repeat(4, minmax(180px, 1fr));
      gap: 10px;
    }

    .summary-card {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px 12px;
      background: var(--panel);
    }

    .summary-title {
      font-size: 12px;
      color: var(--sub);
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.2px;
      margin-bottom: 5px;
    }

    .summary-text {
      font-size: 13px;
      line-height: 1.35;
      color: var(--ink);
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(7, minmax(120px, 1fr));
      gap: 8px;
    }

    .kpi-card {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px 10px;
      background: var(--panel);
      min-height: 106px;
    }

    .kpi-label {
      font-size: 12px;
      color: var(--sub);
      font-weight: 700;
      margin-bottom: 5px;
      text-transform: uppercase;
    }

    .kpi-value {
      font-size: 22px;
      font-weight: 800;
      line-height: 1.1;
      color: var(--ink);
      margin-bottom: 4px;
    }

    .kpi-delta { font-size: 12px; font-weight: 700; }
    .kpi-note { font-size: 11px; color: #475569; margin-top: 2px; line-height: 1.25; }

    .section-head {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 10px;
      gap: 12px;
    }

    .section-head h2 {
      margin: 0;
      font-size: 19px;
      color: var(--ink);
    }

    .section-head p {
      margin: 0;
      font-size: 12px;
      color: var(--sub);
    }

    .chart-grid-primary {
      display: grid;
      grid-template-columns: repeat(2, minmax(280px, 1fr));
      gap: 10px;
    }

    .chart-grid-primary .chart-card:nth-child(5) {
      grid-column: span 2;
    }

    .chart-grid-diagnostic {
      display: grid;
      grid-template-columns: repeat(2, minmax(280px, 1fr));
      gap: 10px;
    }

    .chart-card {
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--panel);
      padding: 10px;
      min-height: 318px;
      display: grid;
      grid-template-rows: auto auto 1fr;
      gap: 4px;
    }

    .chart-title {
      font-size: 14px;
      font-weight: 700;
      color: var(--ink);
      margin: 0;
    }

    .chart-subtitle {
      margin: 0;
      font-size: 12px;
      color: var(--sub);
    }

    .chart-surface {
      width: 100%;
      height: 248px;
      position: relative;
    }

    .chart-empty {
      width: 100%;
      height: 248px;
      display: grid;
      place-items: center;
      color: var(--chart-muted);
      font-size: 13px;
      border: 1px dashed var(--control-border);
      border-radius: 8px;
      background: var(--panel-soft);
    }

    .table-wrap {
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      max-height: 248px;
    }

    table {
      border-collapse: collapse;
      width: 100%;
      font-size: 12px;
      background: var(--panel);
    }

    th, td {
      padding: 8px 9px;
      border-bottom: 1px solid var(--line-soft);
      text-align: left;
      vertical-align: top;
    }

    th {
      background: var(--table-head-bg);
      color: var(--chart-text);
      cursor: pointer;
      position: sticky;
      top: 0;
      z-index: 1;
      user-select: none;
    }

    tr:hover td { background: var(--table-row-hover); }

    .footer-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(220px, 1fr));
      gap: 10px;
      font-size: 12px;
      color: var(--chart-text);
    }

    .foot-block {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: var(--panel);
      line-height: 1.35;
    }

    .foot-block strong {
      display: block;
      margin-bottom: 4px;
      color: var(--ink);
    }

    .tooltip {
      position: fixed;
      pointer-events: none;
      background: var(--tooltip-bg);
      color: #fff;
      font-size: 12px;
      border-radius: 6px;
      padding: 6px 8px;
      z-index: 9999;
      display: none;
      max-width: 320px;
      line-height: 1.3;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
    }

    @media (max-width: 1280px) {
      .kpi-grid { grid-template-columns: repeat(4, minmax(130px, 1fr)); }
      .summary-strip { grid-template-columns: repeat(2, minmax(220px, 1fr)); }
      .filter-grid { grid-template-columns: repeat(3, minmax(160px, 1fr)); }
    }

    @media (max-width: 900px) {
      .chart-grid-primary,
      .chart-grid-diagnostic {
        grid-template-columns: 1fr;
      }
      .chart-grid-primary .chart-card:nth-child(5) { grid-column: span 1; }
      .kpi-grid { grid-template-columns: repeat(2, minmax(120px, 1fr)); }
      .summary-strip { grid-template-columns: 1fr; }
      .filter-grid { grid-template-columns: 1fr; }
      .footer-grid { grid-template-columns: 1fr; }
      .header-tools { width: 100%; justify-content: flex-start; }
    }
  </style>
</head>
<body>
  <div class="container">
    <section class="panel header-panel">
      <div class="header-top">
        <div>
          <h1 id="dashboard-title">Executive Growth Quality Dashboard</h1>
          <div class="subtitle" id="dashboard-subtitle"></div>
        </div>
        <div class="header-tools">
          <button class="theme-btn" id="btn-theme" type="button" aria-label="Toggle theme"></button>
          <div class="meta-chip" id="coverage-chip"></div>
        </div>
      </div>

      <div class="filter-grid">
        <div class="filter-group">
          <label for="filter-start">Date Start</label>
          <input id="filter-start" type="date" />
        </div>
        <div class="filter-group">
          <label for="filter-end">Date End</label>
          <input id="filter-end" type="date" />
        </div>
        <div class="filter-group">
          <label for="filter-segment">Segment (multi-select)</label>
          <select id="filter-segment" multiple></select>
        </div>
        <div class="filter-group">
          <label for="filter-region">Region (multi-select)</label>
          <select id="filter-region" multiple></select>
        </div>
        <div class="filter-group">
          <label for="filter-channel">Acquisition Channel (multi-select)</label>
          <select id="filter-channel" multiple></select>
        </div>
        <div class="filter-group">
          <label for="filter-product">Product Type (multi-select)</label>
          <select id="filter-product" multiple></select>
          <div class="filter-actions" style="margin-top:8px;">
            <button class="btn" id="btn-select-all">Select All</button>
            <button class="btn" id="btn-reset">Reset</button>
          </div>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="section-head">
        <h2>Executive Summary Signals</h2>
        <p id="summary-context"></p>
      </div>
      <div class="summary-strip" id="summary-strip"></div>
    </section>

    <section class="panel">
      <div class="section-head">
        <h2>KPI Pulse</h2>
        <p>Values are filter-aware and benchmarked against the immediately prior period of equal length.</p>
      </div>
      <div class="kpi-grid" id="kpi-grid"></div>
    </section>

    <section class="panel">
      <div class="section-head">
        <h2>Primary Analysis</h2>
        <p>Core sustainability diagnostics for growth, margin quality, retention, and channel economics.</p>
      </div>
      <div class="chart-grid-primary">
        <div class="chart-card">
          <h3 class="chart-title">Revenue momentum remains strong across the selected window</h3>
          <p class="chart-subtitle">Monthly total revenue</p>
          <div id="chart-revenue" class="chart-surface"></div>
        </div>
        <div class="chart-card">
          <h3 class="chart-title">Contribution margin expansion is the core quality test</h3>
          <p class="chart-subtitle">Monthly contribution margin</p>
          <div id="chart-margin" class="chart-surface"></div>
        </div>
        <div class="chart-card">
          <h3 class="chart-title">Revenue versus cost reveals operating leverage pressure points</h3>
          <p class="chart-subtitle">Monthly revenue and cost trend</p>
          <div id="chart-revenue-cost" class="chart-surface"></div>
        </div>
        <div class="chart-card">
          <h3 class="chart-title">Revenue retention decay indicates dependence on new acquisition</h3>
          <p class="chart-subtitle">Median cohort revenue retention by month since signup</p>
          <div id="chart-cohort-retention" class="chart-surface"></div>
        </div>
        <div class="chart-card">
          <h3 class="chart-title">Channel unit economics separate scalable growth from value destruction</h3>
          <p class="chart-subtitle">Average LTV versus CAC by acquisition channel</p>
          <div id="chart-ltv-cac" class="chart-surface"></div>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="section-head">
        <h2>Diagnostic Section</h2>
        <p>Profitability and commercial mix diagnostics for targeted intervention.</p>
      </div>
      <div class="chart-grid-diagnostic">
        <div class="chart-card">
          <h3 class="chart-title">Segment margin dollars are concentrated but rate quality varies</h3>
          <p class="chart-subtitle">Contribution margin by segment</p>
          <div id="chart-segment-margin" class="chart-surface"></div>
        </div>
        <div class="chart-card">
          <h3 class="chart-title">Ticket-size differences reveal monetization concentration by segment</h3>
          <p class="chart-subtitle">Average revenue per transaction by segment</p>
          <div id="chart-arpt-segment" class="chart-surface"></div>
        </div>
        <div class="chart-card">
          <h3 class="chart-title">Customer revenue is long-tailed and concentrated</h3>
          <p class="chart-subtitle">Distribution of customer revenue in selected scope</p>
          <div id="chart-revenue-distribution" class="chart-surface"></div>
        </div>
        <div class="chart-card">
          <h3 class="chart-title">Regional profitability comparison</h3>
          <p class="chart-subtitle">Sortable table for margin quality by region</p>
          <div class="table-wrap">
            <table id="region-table"></table>
          </div>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="section-head">
        <h2>Risk / Priority Ranking</h2>
        <p>Top ranked concerns based on unit economics, margin weakness, and cohort deterioration.</p>
      </div>
      <div class="table-wrap" style="max-height:none;">
        <table id="risk-table"></table>
      </div>
    </section>

    <section class="panel">
      <div class="footer-grid">
        <div class="foot-block">
          <strong>How To Read</strong>
          This view balances growth pace with profitability quality, retention durability, and acquisition efficiency.
          Use it to decide where to scale confidently and where to intervene.
        </div>
        <div class="foot-block">
          <strong>Scope Caveat</strong>
          Insights are based on synthetic data and observed in-window performance.
          Treat results as directional decision support rather than forward-looking forecast precision.
        </div>
      </div>
    </section>
  </div>

  <div class="tooltip" id="tooltip"></div>

  <script>
    const DASHBOARD_DATA = __DATA_JSON__;
    const CUSTOMER_BY_ID = new Map((DASHBOARD_DATA.customers || []).map(c => [c.cid, c]));
    const METRIC_POLICY = DASHBOARD_DATA.meta.metric_policy || {};
    const EFF_THRESH = METRIC_POLICY.efficiency_thresholds || {
      ltv_cac_target: 3.0,
      payback_target_months: 12.0,
      ineff_ltv_cac: 1.0,
      ineff_payback_months: 24.0
    };
    const RISK_WEIGHTS = METRIC_POLICY.risk_score_weights || {
      low_efficiency_base: 90.0,
      borderline_base: 60.0,
      payback_cap_points: 40.0,
      segment_margin_floor: 0.35,
      segment_base: 60.0,
      cohort_base: 55.0
    };
    const THEME_KEY = 'exec_dashboard_theme';

    const state = {
      regionSort: { key: 'marginPct', dir: 'desc' },
      riskSort: { key: 'priorityScore', dir: 'desc' },
    };

    const tooltipEl = document.getElementById('tooltip');

    function cssVar(name, fallback) {
      const value = getComputedStyle(document.body).getPropertyValue(name).trim();
      return value || fallback;
    }

    function themeColors() {
      return {
        rev: cssVar('--rev', '#0b4f6c'),
        cost: cssVar('--cost', '#c44536'),
        margin: cssVar('--margin', '#2a9d8f'),
        accent: cssVar('--accent', '#ffb703'),
        bar: cssVar('--bar', '#264653'),
        good: cssVar('--good', '#059669'),
        bad: cssVar('--bad', '#b91c1c'),
        warn: cssVar('--warn', '#a16207'),
        grid: cssVar('--chart-grid', '#e5e7eb'),
        axis: cssVar('--chart-axis', '#94a3b8'),
        text: cssVar('--chart-text', '#334155'),
        muted: cssVar('--chart-muted', '#64748b'),
      };
    }

    function applyTheme(theme) {
      const normalized = theme === 'dark' ? 'dark' : 'light';
      document.body.setAttribute('data-theme', normalized);
      const btn = document.getElementById('btn-theme');
      btn.textContent = normalized === 'dark' ? 'Light Mode' : 'Dark Mode';
      btn.setAttribute(
        'aria-label',
        normalized === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
      );
    }

    function resolveInitialTheme() {
      const saved = window.localStorage.getItem(THEME_KEY);
      if (saved === 'dark' || saved === 'light') return saved;
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function toggleTheme() {
      const current = document.body.getAttribute('data-theme') || 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      window.localStorage.setItem(THEME_KEY, next);
      applyTheme(next);
      computeAndRender();
    }

    function fmtCurrency(value) {
      if (!Number.isFinite(value)) return 'n/a';
      const abs = Math.abs(value);
      if (abs >= 1_000_000) return '$' + (value / 1_000_000).toFixed(2) + 'M';
      if (abs >= 1_000) return '$' + (value / 1_000).toFixed(1) + 'K';
      return '$' + value.toFixed(0);
    }

    function fmtCurrencyFull(value) {
      if (!Number.isFinite(value)) return 'n/a';
      return '$' + value.toLocaleString(undefined, { maximumFractionDigits: 2 });
    }

    function fmtPct(value) {
      if (!Number.isFinite(value)) return 'n/a';
      return (value * 100).toFixed(1) + '%';
    }

    function fmtNum(value, digits = 2) {
      if (!Number.isFinite(value)) return 'n/a';
      return value.toLocaleString(undefined, { maximumFractionDigits: digits });
    }

    function dateToTs(dateStr) {
      return new Date(dateStr + 'T00:00:00').getTime();
    }

    function monthKey(dateStr) {
      return dateStr.slice(0, 7);
    }

    function monthLabel(monthStr) {
      const parts = monthStr.split('-');
      const d = new Date(Number(parts[0]), Number(parts[1]) - 1, 1);
      return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short' });
    }

    function diffMonths(startMonth, endMonth) {
      const sy = Number(startMonth.slice(0, 4));
      const sm = Number(startMonth.slice(5, 7));
      const ey = Number(endMonth.slice(0, 4));
      const em = Number(endMonth.slice(5, 7));
      return (ey - sy) * 12 + (em - sm);
    }

    function median(values) {
      if (!values.length) return NaN;
      const arr = [...values].sort((a, b) => a - b);
      const mid = Math.floor(arr.length / 2);
      return arr.length % 2 ? arr[mid] : (arr[mid - 1] + arr[mid]) / 2;
    }

    function quantile(values, q) {
      if (!values.length) return NaN;
      const arr = [...values].sort((a, b) => a - b);
      const pos = (arr.length - 1) * q;
      const base = Math.floor(pos);
      const rest = pos - base;
      if (arr[base + 1] !== undefined) return arr[base] + rest * (arr[base + 1] - arr[base]);
      return arr[base];
    }

    function setTooltip(target, html) {
      target.addEventListener('mouseenter', () => {
        tooltipEl.innerHTML = html;
        tooltipEl.style.display = 'block';
      });
      target.addEventListener('mousemove', (e) => {
        tooltipEl.style.left = (e.clientX + 14) + 'px';
        tooltipEl.style.top = (e.clientY + 14) + 'px';
      });
      target.addEventListener('mouseleave', () => {
        tooltipEl.style.display = 'none';
      });
    }

    function clearNode(id) {
      const el = document.getElementById(id);
      el.innerHTML = '';
      return el;
    }

    function renderNoData(id, message = 'No data for selected filters') {
      const container = clearNode(id);
      const div = document.createElement('div');
      div.className = 'chart-empty';
      div.textContent = message;
      container.appendChild(div);
    }

    function createSvg(container, height = 248) {
      const width = Math.max(340, container.clientWidth - 6);
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('width', width);
      svg.setAttribute('height', height);
      svg.style.width = '100%';
      svg.style.height = height + 'px';
      container.appendChild(svg);
      return { svg, width, height };
    }

    function addSvgLine(svg, x1, y1, x2, y2, color, width = 1, dash = null, opacity = 1) {
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', x1); line.setAttribute('y1', y1);
      line.setAttribute('x2', x2); line.setAttribute('y2', y2);
      line.setAttribute('stroke', color);
      line.setAttribute('stroke-width', width);
      line.setAttribute('opacity', opacity);
      if (dash) line.setAttribute('stroke-dasharray', dash);
      svg.appendChild(line);
      return line;
    }

    function addSvgText(svg, x, y, text, opts = {}) {
      const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      t.setAttribute('x', x);
      t.setAttribute('y', y);
      t.setAttribute('fill', opts.color || cssVar('--chart-text', '#475569'));
      t.setAttribute('font-size', opts.size || '11');
      t.setAttribute('text-anchor', opts.anchor || 'start');
      t.setAttribute('font-weight', opts.weight || '400');
      t.textContent = text;
      svg.appendChild(t);
      return t;
    }

    function linePath(points) {
      if (!points.length) return '';
      let d = `M ${points[0].x} ${points[0].y}`;
      for (let i = 1; i < points.length; i += 1) d += ` L ${points[i].x} ${points[i].y}`;
      return d;
    }

    function renderLineChart(id, rows, series, yFormatter) {
      if (!rows.length) {
        renderNoData(id);
        return;
      }
      const palette = themeColors();

      const container = clearNode(id);
      const { svg, width, height } = createSvg(container);
      const m = { top: 14, right: 18, bottom: 36, left: 58 };
      const innerW = width - m.left - m.right;
      const innerH = height - m.top - m.bottom;

      const xVals = rows.map(r => r.x);
      const xMin = Math.min(...xVals);
      const xMax = Math.max(...xVals);

      let yMax = 0;
      series.forEach(s => {
        rows.forEach(r => { yMax = Math.max(yMax, Number(r[s.key]) || 0); });
      });
      yMax = yMax <= 0 ? 1 : yMax * 1.1;

      const sx = (x) => m.left + ((x - xMin) / Math.max(1, (xMax - xMin))) * innerW;
      const sy = (y) => m.top + innerH - (y / yMax) * innerH;

      for (let i = 0; i <= 5; i += 1) {
        const y = m.top + (i / 5) * innerH;
        addSvgLine(svg, m.left, y, width - m.right, y, palette.grid, 1);
        const value = yMax * (1 - i / 5);
        addSvgText(svg, m.left - 8, y + 4, yFormatter(value), { anchor: 'end', size: '10' });
      }

      const tickCount = Math.min(6, rows.length);
      for (let i = 0; i < tickCount; i += 1) {
        const idx = Math.round((i / Math.max(1, tickCount - 1)) * (rows.length - 1));
        const row = rows[idx];
        const x = sx(row.x);
        addSvgLine(svg, x, height - m.bottom, x, height - m.bottom + 4, palette.axis, 1);
        addSvgText(svg, x, height - m.bottom + 16, row.label, { anchor: 'middle', size: '10' });
      }

      addSvgLine(svg, m.left, m.top + innerH, width - m.right, m.top + innerH, palette.axis, 1.2);
      addSvgLine(svg, m.left, m.top, m.left, m.top + innerH, palette.axis, 1.2);

      series.forEach(s => {
        const pts = rows.map(r => ({ x: sx(r.x), y: sy(r[s.key]), raw: r[s.key], label: r.label }));
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', linePath(pts));
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', s.color);
        path.setAttribute('stroke-width', s.width || 2.3);
        svg.appendChild(path);

        pts.forEach(p => {
          const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
          c.setAttribute('cx', p.x);
          c.setAttribute('cy', p.y);
          c.setAttribute('r', 3);
          c.setAttribute('fill', s.color);
          c.setAttribute('opacity', '0.95');
          svg.appendChild(c);
          setTooltip(c, `<strong>${s.label}</strong><br>${p.label}: ${yFormatter(p.raw)}`);
        });
      });

      if (series.length > 1) {
        let lx = m.left;
        const ly = m.top - 2;
        series.forEach(s => {
          addSvgLine(svg, lx, ly, lx + 18, ly, s.color, 2.4);
          addSvgText(svg, lx + 22, ly + 4, s.label, { size: '10' });
          lx += 100;
        });
      }
    }

    function renderScatterChart(id, rows) {
      if (!rows.length) {
        renderNoData(id);
        return;
      }
      const palette = themeColors();

      const container = clearNode(id);
      const { svg, width, height } = createSvg(container);
      const m = { top: 16, right: 18, bottom: 40, left: 60 };
      const innerW = width - m.left - m.right;
      const innerH = height - m.top - m.bottom;

      const xMax = Math.max(1, ...rows.map(r => r.CAC)) * 1.15;
      const yMax = Math.max(1, ...rows.map(r => r.avgLTV)) * 1.15;

      const sx = (x) => m.left + (x / xMax) * innerW;
      const sy = (y) => m.top + innerH - (y / yMax) * innerH;

      for (let i = 0; i <= 5; i += 1) {
        const x = m.left + (i / 5) * innerW;
        const v = xMax * (i / 5);
        addSvgLine(svg, x, m.top + innerH, x, m.top + innerH + 4, palette.axis, 1);
        addSvgText(svg, x, m.top + innerH + 16, fmtCurrency(v), { anchor: 'middle', size: '10' });
      }

      for (let i = 0; i <= 5; i += 1) {
        const y = m.top + (i / 5) * innerH;
        const v = yMax * (1 - i / 5);
        addSvgLine(svg, m.left - 4, y, m.left, y, palette.axis, 1);
        addSvgText(svg, m.left - 8, y + 4, fmtCurrency(v), { anchor: 'end', size: '10' });
      }

      addSvgLine(svg, m.left, m.top + innerH, width - m.right, m.top + innerH, palette.axis, 1.2);
      addSvgLine(svg, m.left, m.top, m.left, m.top + innerH, palette.axis, 1.2);

      const diagStart = { x: 0, y: 0 };
      const diagEnd = { x: Math.min(xMax, yMax), y: Math.min(xMax, yMax) };
      addSvgLine(svg, sx(diagStart.x), sy(diagStart.y), sx(diagEnd.x), sy(diagEnd.y), palette.axis, 1, '4 4', 0.9);

      rows.forEach(r => {
        const cx = sx(r.CAC);
        const cy = sy(r.avgLTV);
        const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        c.setAttribute('cx', cx);
        c.setAttribute('cy', cy);
        c.setAttribute('r', 6);
        c.setAttribute('fill', r.status === 'inefficient' ? palette.bad : (r.status === 'efficient' ? palette.good : palette.warn));
        c.setAttribute('opacity', '0.9');
        svg.appendChild(c);
        addSvgText(svg, cx + 7, cy - 8, r.channel, { size: '10', color: palette.text });
        setTooltip(c,
          `<strong>${r.channel}</strong><br>` +
          `CAC: ${fmtCurrencyFull(r.CAC)}<br>` +
          `Avg LTV: ${fmtCurrencyFull(r.avgLTV)}<br>` +
          `LTV/CAC: ${fmtNum(r.ltvToCac, 2)}<br>` +
          `Payback: ${Number.isFinite(r.payback) ? fmtNum(r.payback, 1) + ' months' : 'n/a'}`
        );
      });
    }

    function renderBarChart(id, rows, key, labelKey, yFormatter, color) {
      if (!rows.length) {
        renderNoData(id);
        return;
      }
      const palette = themeColors();

      const container = clearNode(id);
      const { svg, width, height } = createSvg(container);
      const m = { top: 16, right: 18, bottom: 44, left: 60 };
      const innerW = width - m.left - m.right;
      const innerH = height - m.top - m.bottom;

      const yMax = Math.max(1, ...rows.map(r => Number(r[key]) || 0)) * 1.15;
      const barW = innerW / rows.length * 0.65;
      const gap = innerW / rows.length;

      const sy = (y) => m.top + innerH - (y / yMax) * innerH;

      for (let i = 0; i <= 5; i += 1) {
        const y = m.top + (i / 5) * innerH;
        addSvgLine(svg, m.left, y, width - m.right, y, palette.grid, 1);
        const v = yMax * (1 - i / 5);
        addSvgText(svg, m.left - 8, y + 4, yFormatter(v), { anchor: 'end', size: '10' });
      }

      addSvgLine(svg, m.left, m.top + innerH, width - m.right, m.top + innerH, palette.axis, 1.2);
      addSvgLine(svg, m.left, m.top, m.left, m.top + innerH, palette.axis, 1.2);

      rows.forEach((r, idx) => {
        const x = m.left + idx * gap + (gap - barW) / 2;
        const y = sy(Number(r[key]) || 0);
        const h = m.top + innerH - y;

        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', x);
        rect.setAttribute('y', y);
        rect.setAttribute('width', barW);
        rect.setAttribute('height', Math.max(1, h));
        rect.setAttribute('fill', color);
        rect.setAttribute('opacity', '0.9');
        svg.appendChild(rect);

        addSvgText(svg, x + barW / 2, m.top + innerH + 16, String(r[labelKey]), { anchor: 'middle', size: '10' });
        setTooltip(rect, `<strong>${r[labelKey]}</strong><br>${yFormatter(r[key])}` + (r.marginPct !== undefined ? `<br>Margin %: ${fmtPct(r.marginPct)}` : ''));
      });
    }

    function renderHistogram(id, values) {
      if (!values.length) {
        renderNoData(id);
        return;
      }
      const palette = themeColors();

      const clean = values.filter(v => Number.isFinite(v) && v > 0);
      if (!clean.length) {
        renderNoData(id, 'No positive revenue observations in selected scope');
        return;
      }

      const p99 = quantile(clean, 0.99);
      const clipped = clean.map(v => Math.min(v, p99));
      const bins = 24;
      const min = Math.min(...clipped);
      const max = Math.max(...clipped);
      const step = Math.max(1e-9, (max - min) / bins);
      const counts = new Array(bins).fill(0);
      clipped.forEach(v => {
        const idx = Math.min(bins - 1, Math.floor((v - min) / step));
        counts[idx] += 1;
      });

      const rows = counts.map((c, i) => ({
        bucketStart: min + i * step,
        bucketEnd: min + (i + 1) * step,
        count: c,
        label: i,
      }));

      const container = clearNode(id);
      const { svg, width, height } = createSvg(container);
      const m = { top: 16, right: 18, bottom: 40, left: 52 };
      const innerW = width - m.left - m.right;
      const innerH = height - m.top - m.bottom;

      const yMax = Math.max(1, ...rows.map(r => r.count)) * 1.1;
      const barW = innerW / rows.length;

      for (let i = 0; i <= 4; i += 1) {
        const y = m.top + (i / 4) * innerH;
        const v = yMax * (1 - i / 4);
        addSvgLine(svg, m.left, y, width - m.right, y, palette.grid, 1);
        addSvgText(svg, m.left - 8, y + 4, Math.round(v).toString(), { anchor: 'end', size: '10' });
      }

      addSvgLine(svg, m.left, m.top + innerH, width - m.right, m.top + innerH, palette.axis, 1.2);
      addSvgLine(svg, m.left, m.top, m.left, m.top + innerH, palette.axis, 1.2);

      rows.forEach((r, i) => {
        const h = (r.count / yMax) * innerH;
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', m.left + i * barW + 0.5);
        rect.setAttribute('y', m.top + innerH - h);
        rect.setAttribute('width', Math.max(1, barW - 1));
        rect.setAttribute('height', Math.max(1, h));
        rect.setAttribute('fill', palette.bar);
        rect.setAttribute('opacity', '0.88');
        svg.appendChild(rect);
        setTooltip(rect, `Revenue bucket: ${fmtCurrencyFull(r.bucketStart)} - ${fmtCurrencyFull(r.bucketEnd)}<br>Customers: ${r.count}`);
      });

      addSvgText(svg, m.left, height - 8, 'Distribution clipped at P99 to reduce outlier distortion', { size: '10', color: palette.muted });
    }

    function populateMultiSelect(id, values) {
      const select = document.getElementById(id);
      select.innerHTML = '';
      values.forEach(v => {
        const opt = document.createElement('option');
        opt.value = v;
        opt.textContent = v;
        opt.selected = true;
        select.appendChild(opt);
      });
    }

    function getSelectedSet(id, allValues) {
      const options = Array.from(document.getElementById(id).options);
      const selected = options.filter(o => o.selected).map(o => o.value);
      if (!selected.length) return new Set(allValues);
      return new Set(selected);
    }

    function applyFilters(startDate, endDate, selected) {
      const startTs = dateToTs(startDate);
      const endTs = dateToTs(endDate);

      const filteredTx = [];
      for (const r of DASHBOARD_DATA.transactions) {
        const customer = CUSTOMER_BY_ID.get(r.cid);
        if (!customer) continue;
        const ts = dateToTs(r.d);
        if (ts < startTs || ts > endTs) continue;
        if (!selected.segments.has(customer.seg)) continue;
        if (!selected.regions.has(customer.reg)) continue;
        if (!selected.channels.has(customer.ch)) continue;
        if (!selected.products.has(r.prod)) continue;
        filteredTx.push({
          ...r,
          sd: customer.sd,
          seg: customer.seg,
          reg: customer.reg,
          ch: customer.ch,
        });
      }

      const filteredCustomers = [];
      for (const c of DASHBOARD_DATA.customers) {
        const ts = dateToTs(c.sd);
        if (ts < startTs || ts > endTs) continue;
        if (!selected.segments.has(c.seg)) continue;
        if (!selected.regions.has(c.reg)) continue;
        if (!selected.channels.has(c.ch)) continue;
        filteredCustomers.push(c);
      }

      const filteredSpend = [];
      for (const m of DASHBOARD_DATA.marketing_spend) {
        const ts = dateToTs(m.d);
        if (ts < startTs || ts > endTs) continue;
        if (!selected.channels.has(m.ch)) continue;
        filteredSpend.push(m);
      }

      return { tx: filteredTx, customers: filteredCustomers, spend: filteredSpend };
    }

    function aggregateMonthly(tx) {
      const map = new Map();
      tx.forEach(r => {
        const k = monthKey(r.d);
        if (!map.has(k)) map.set(k, { month: k, revenue: 0, cost: 0, customers: new Set() });
        const o = map.get(k);
        o.revenue += r.rev;
        o.cost += r.cost;
        o.customers.add(r.cid);
      });

      const rows = Array.from(map.values())
        .map(o => ({
          month: o.month,
          revenue: o.revenue,
          cost: o.cost,
          margin: o.revenue - o.cost,
          activeCustomers: o.customers.size,
        }))
        .sort((a, b) => a.month.localeCompare(b.month));
      return rows;
    }

    function computeSnapshot(tx, customers, spend, startDate, endDate) {
      const revenue = tx.reduce((s, r) => s + r.rev, 0);
      const cost = tx.reduce((s, r) => s + r.cost, 0);
      const margin = revenue - cost;
      const marginPct = revenue > 0 ? margin / revenue : NaN;

      const customerSet = new Set(customers.map(c => c.cid));
      const acquiredCount = customerSet.size;
      const spendTotal = spend.reduce((s, r) => s + r.spend, 0);
      const CAC = acquiredCount > 0 ? spendTotal / acquiredCount : NaN;

      let acquiredCm = 0;
      tx.forEach(r => {
        if (customerSet.has(r.cid)) acquiredCm += (r.rev - r.cost);
      });

      const avgLTV = acquiredCount > 0 ? acquiredCm / acquiredCount : NaN;
      const ltvToCac = (Number.isFinite(CAC) && CAC > 0) ? avgLTV / CAC : NaN;

      const monthStart = monthKey(startDate);
      const monthEnd = monthKey(endDate);
      const months = Math.max(1, diffMonths(monthStart, monthEnd) + 1);
      const monthlyCmPerCustomer = acquiredCount > 0 ? (acquiredCm / acquiredCount) / months : NaN;
      const payback = (Number.isFinite(monthlyCmPerCustomer) && monthlyCmPerCustomer > 0 && Number.isFinite(CAC))
        ? CAC / monthlyCmPerCustomer
        : NaN;

      return {
        revenue,
        cost,
        margin,
        marginPct,
        CAC,
        avgLTV,
        ltvToCac,
        payback,
        acquiredCount,
        spendTotal,
      };
    }

    function shiftDate(dateStr, days) {
      const d = new Date(dateStr + 'T00:00:00');
      d.setDate(d.getDate() + days);
      return d.toISOString().slice(0, 10);
    }

    function dayDiff(startDate, endDate) {
      const ms = dateToTs(endDate) - dateToTs(startDate);
      return Math.floor(ms / 86400000) + 1;
    }

    function computeUnitEconomicsByChannel(filtered, startDate, endDate, selected) {
      const channels = Array.from(selected.channels);
      const customerByChannel = new Map();
      channels.forEach(ch => customerByChannel.set(ch, new Set()));
      filtered.customers.forEach(c => {
        if (!customerByChannel.has(c.ch)) customerByChannel.set(c.ch, new Set());
        customerByChannel.get(c.ch).add(c.cid);
      });

      const spendByChannel = new Map();
      channels.forEach(ch => spendByChannel.set(ch, 0));
      filtered.spend.forEach(m => {
        spendByChannel.set(m.ch, (spendByChannel.get(m.ch) || 0) + m.spend);
      });

      const cmByChannel = new Map();
      channels.forEach(ch => cmByChannel.set(ch, 0));
      filtered.tx.forEach(t => {
        cmByChannel.set(t.ch, (cmByChannel.get(t.ch) || 0) + (t.rev - t.cost));
      });

      const months = Math.max(1, diffMonths(monthKey(startDate), monthKey(endDate)) + 1);

      const rows = channels.map(ch => {
        const cCount = (customerByChannel.get(ch) || new Set()).size;
        const spend = spendByChannel.get(ch) || 0;
        const cm = cmByChannel.get(ch) || 0;
        const CAC = cCount > 0 ? spend / cCount : NaN;
        const avgLTV = cCount > 0 ? cm / cCount : NaN;
        const ltvToCac = (Number.isFinite(CAC) && CAC > 0) ? avgLTV / CAC : NaN;
        const monthlyCmPerCustomer = cCount > 0 ? (cm / cCount) / months : NaN;
        const payback = (Number.isFinite(monthlyCmPerCustomer) && monthlyCmPerCustomer > 0 && Number.isFinite(CAC))
          ? CAC / monthlyCmPerCustomer
          : NaN;

        let status = 'borderline';
        if (!Number.isFinite(ltvToCac) || !Number.isFinite(payback)) status = 'undefined';
        else if (ltvToCac >= EFF_THRESH.ltv_cac_target && payback <= EFF_THRESH.payback_target_months) status = 'efficient';
        else if (ltvToCac < EFF_THRESH.ineff_ltv_cac || payback > EFF_THRESH.ineff_payback_months) status = 'inefficient';

        return { channel: ch, customersAcquired: cCount, totalSpend: spend, CAC, avgLTV, ltvToCac, payback, status };
      });

      return rows.sort((a, b) => (b.ltvToCac || -Infinity) - (a.ltvToCac || -Infinity));
    }

    function computeCohortRetention(tx) {
      const agg = new Map();
      tx.forEach(r => {
        const cohort = monthKey(r.sd);
        const activity = monthKey(r.d);
        const key = cohort + '|' + activity;
        if (!agg.has(key)) agg.set(key, { cohort, activity, revenue: 0, customers: new Set() });
        const o = agg.get(key);
        o.revenue += r.rev;
        o.customers.add(r.cid);
      });

      const rows = Array.from(agg.values()).map(o => ({
        cohort: o.cohort,
        activity: o.activity,
        revenue: o.revenue,
        activeCustomers: o.customers.size,
        monthsSince: diffMonths(o.cohort, o.activity),
      }));

      const baselineMap = new Map();
      rows.forEach(r => {
        if (r.monthsSince === 0) baselineMap.set(r.cohort, { revenue: r.revenue, customers: r.activeCustomers });
      });

      const byMonths = new Map();
      rows.forEach(r => {
        const base = baselineMap.get(r.cohort);
        if (!base || base.revenue <= 0 || base.customers <= 0) return;
        const revRet = r.revenue / base.revenue;
        const actRet = r.activeCustomers / base.customers;
        if (!byMonths.has(r.monthsSince)) byMonths.set(r.monthsSince, { rev: [], act: [] });
        byMonths.get(r.monthsSince).rev.push(revRet);
        byMonths.get(r.monthsSince).act.push(actRet);
      });

      const summary = Array.from(byMonths.entries())
        .map(([monthsSince, vals]) => ({
          monthsSince,
          medianRevenueRetention: median(vals.rev),
          medianActivityRetention: median(vals.act),
        }))
        .sort((a, b) => a.monthsSince - b.monthsSince);

      const decayByCohort = [];
      baselineMap.forEach((base, cohort) => {
        const m6 = rows.find(r => r.cohort === cohort && r.monthsSince === 6);
        if (m6) {
          decayByCohort.push({ cohort, month6RevenueRetention: m6.revenue / base.revenue });
        }
      });

      return { summary, decayByCohort };
    }

    function computeSegmentProfitability(tx) {
      const map = new Map();
      tx.forEach(r => {
        if (!map.has(r.seg)) map.set(r.seg, { segment: r.seg, revenue: 0, cost: 0, transactions: 0 });
        const o = map.get(r.seg);
        o.revenue += r.rev;
        o.cost += r.cost;
        o.transactions += 1;
      });
      return Array.from(map.values()).map(r => ({
        ...r,
        margin: r.revenue - r.cost,
        marginPct: r.revenue > 0 ? (r.revenue - r.cost) / r.revenue : NaN,
      })).sort((a, b) => b.margin - a.margin);
    }

    function computeRegionProfitability(tx) {
      const map = new Map();
      tx.forEach(r => {
        if (!map.has(r.reg)) map.set(r.reg, { region: r.reg, revenue: 0, cost: 0, transactions: 0 });
        const o = map.get(r.reg);
        o.revenue += r.rev;
        o.cost += r.cost;
        o.transactions += 1;
      });
      return Array.from(map.values()).map(r => ({
        ...r,
        margin: r.revenue - r.cost,
        marginPct: r.revenue > 0 ? (r.revenue - r.cost) / r.revenue : NaN,
      }));
    }

    function computeAvgRevenuePerTxBySegment(tx) {
      const map = new Map();
      tx.forEach(r => {
        if (!map.has(r.seg)) map.set(r.seg, { segment: r.seg, revenue: 0, txCount: 0 });
        const o = map.get(r.seg);
        o.revenue += r.rev;
        o.txCount += 1;
      });
      return Array.from(map.values()).map(r => ({
        segment: r.segment,
        avgRevTx: r.txCount > 0 ? r.revenue / r.txCount : NaN,
      })).sort((a, b) => b.avgRevTx - a.avgRevTx);
    }

    function computeRevenueByCustomer(tx) {
      const map = new Map();
      tx.forEach(r => {
        map.set(r.cid, (map.get(r.cid) || 0) + r.rev);
      });
      return Array.from(map.values());
    }

    function computeRiskRows(unitRows, segmentRows, cohortDecayRows) {
      const rows = [];

      unitRows
        .filter(r => Number.isFinite(r.ltvToCac))
        .sort((a, b) => a.ltvToCac - b.ltvToCac)
        .slice(0, 3)
        .forEach(r => {
          const score = (r.ltvToCac < EFF_THRESH.ineff_ltv_cac ? RISK_WEIGHTS.low_efficiency_base : RISK_WEIGHTS.borderline_base)
            + (Number.isFinite(r.payback) ? Math.min(RISK_WEIGHTS.payback_cap_points, r.payback) : 15);
          rows.push({
            entity: `Channel: ${r.channel}`,
            metricValues: `LTV/CAC ${fmtNum(r.ltvToCac, 2)} | Payback ${Number.isFinite(r.payback) ? fmtNum(r.payback, 1) + 'm' : 'n/a'}`,
            riskInterpretation: r.ltvToCac < 1
              ? 'Customer value does not recover acquisition spend.'
              : 'Channel is borderline with slow capital recovery.',
            recommendedAction: r.ltvToCac < 1
              ? 'Reduce budget share and tighten bid/creative efficiency tests.'
              : 'Run CAC reduction plan before scaling spend.',
            priorityScore: score,
          });
        });

      segmentRows
        .filter(r => Number.isFinite(r.marginPct))
        .sort((a, b) => a.marginPct - b.marginPct)
        .slice(0, 2)
        .forEach(r => {
          const score = RISK_WEIGHTS.segment_base + Math.max(0, (RISK_WEIGHTS.segment_margin_floor - r.marginPct) * 100);
          rows.push({
            entity: `Segment: ${r.segment}`,
            metricValues: `Margin ${fmtPct(r.marginPct)} | Contribution ${fmtCurrency(r.margin)}`,
            riskInterpretation: 'Low margin rate weakens growth quality as segment scales.',
            recommendedAction: 'Improve packaging, pricing discipline, and service delivery cost controls.',
            priorityScore: score,
          });
        });

      cohortDecayRows
        .sort((a, b) => a.month6RevenueRetention - b.month6RevenueRetention)
        .slice(0, 2)
        .forEach(r => {
          const score = RISK_WEIGHTS.cohort_base + Math.max(0, (1 - r.month6RevenueRetention) * 100);
          rows.push({
            entity: `Cohort: ${r.cohort}`,
            metricValues: `Month-6 Revenue Retention ${fmtPct(r.month6RevenueRetention)}`,
            riskInterpretation: 'Fast cohort decay implies dependence on constant new acquisition.',
            recommendedAction: 'Strengthen early lifecycle activation and expansion motions for this cohort profile.',
            priorityScore: score,
          });
        });

      return rows.sort((a, b) => b.priorityScore - a.priorityScore);
    }

    function renderSummaryStrip(insights) {
      const wrap = document.getElementById('summary-strip');
      wrap.innerHTML = '';
      insights.forEach(item => {
        const card = document.createElement('div');
        card.className = 'summary-card';
        card.innerHTML = `<div class="summary-title">${item.title}</div><div class="summary-text">${item.text}</div>`;
        wrap.appendChild(card);
      });
    }

    function renderKpis(cards) {
      const wrap = document.getElementById('kpi-grid');
      wrap.innerHTML = '';
      const palette = themeColors();
      cards.forEach(card => {
        const deltaClass = !Number.isFinite(card.delta)
          ? 'kpi-delta'
          : (card.delta >= 0 ? 'kpi-delta' : 'kpi-delta');
        const deltaColor = !Number.isFinite(card.delta)
          ? palette.muted
          : (card.delta >= 0 ? palette.good : palette.bad);

        const el = document.createElement('div');
        el.className = 'kpi-card';
        el.innerHTML = `
          <div class="kpi-label">${card.label}</div>
          <div class="kpi-value">${card.value}</div>
          <div class="${deltaClass}" style="color:${deltaColor};">${card.deltaText}</div>
          <div class="kpi-note">${card.note}</div>
        `;
        wrap.appendChild(el);
      });
    }

    function renderRegionTable(rows) {
      const table = document.getElementById('region-table');
      const sorted = [...rows].sort((a, b) => {
        const k = state.regionSort.key;
        const dir = state.regionSort.dir === 'asc' ? 1 : -1;
        return ((a[k] > b[k]) ? 1 : -1) * dir;
      });

      table.innerHTML = `
        <thead>
          <tr>
            <th data-key="region">Region</th>
            <th data-key="revenue">Revenue</th>
            <th data-key="cost">Cost</th>
            <th data-key="margin">Contribution Margin</th>
            <th data-key="marginPct">Margin %</th>
          </tr>
        </thead>
        <tbody>
          ${sorted.map(r => `
            <tr>
              <td>${r.region}</td>
              <td>${fmtCurrencyFull(r.revenue)}</td>
              <td>${fmtCurrencyFull(r.cost)}</td>
              <td>${fmtCurrencyFull(r.margin)}</td>
              <td>${fmtPct(r.marginPct)}</td>
            </tr>
          `).join('')}
        </tbody>
      `;

      table.querySelectorAll('th').forEach(th => {
        th.addEventListener('click', () => {
          const key = th.dataset.key;
          if (state.regionSort.key === key) {
            state.regionSort.dir = state.regionSort.dir === 'asc' ? 'desc' : 'asc';
          } else {
            state.regionSort.key = key;
            state.regionSort.dir = 'desc';
          }
          renderRegionTable(rows);
        });
      });
    }

    function renderRiskTable(rows) {
      const table = document.getElementById('risk-table');
      const sorted = [...rows].sort((a, b) => {
        const k = state.riskSort.key;
        const dir = state.riskSort.dir === 'asc' ? 1 : -1;
        return ((a[k] > b[k]) ? 1 : -1) * dir;
      });

      table.innerHTML = `
        <thead>
          <tr>
            <th data-key="entity">Entity</th>
            <th data-key="metricValues">Metric Values</th>
            <th data-key="riskInterpretation">Risk Interpretation</th>
            <th data-key="recommendedAction">Recommended Action</th>
            <th data-key="priorityScore">Priority Score</th>
          </tr>
        </thead>
        <tbody>
          ${sorted.map(r => `
            <tr>
              <td>${r.entity}</td>
              <td>${r.metricValues}</td>
              <td>${r.riskInterpretation}</td>
              <td>${r.recommendedAction}</td>
              <td>${fmtNum(r.priorityScore, 1)}</td>
            </tr>
          `).join('')}
        </tbody>
      `;

      table.querySelectorAll('th').forEach(th => {
        th.addEventListener('click', () => {
          const key = th.dataset.key;
          if (state.riskSort.key === key) {
            state.riskSort.dir = state.riskSort.dir === 'asc' ? 'desc' : 'asc';
          } else {
            state.riskSort.key = key;
            state.riskSort.dir = key === 'priorityScore' ? 'desc' : 'asc';
          }
          renderRiskTable(rows);
        });
      });
    }

    function computeAndRender() {
      const startDate = document.getElementById('filter-start').value;
      const endDate = document.getElementById('filter-end').value;

      const selected = {
        segments: getSelectedSet('filter-segment', DASHBOARD_DATA.meta.values.segments),
        regions: getSelectedSet('filter-region', DASHBOARD_DATA.meta.values.regions),
        channels: getSelectedSet('filter-channel', DASHBOARD_DATA.meta.values.acquisition_channels),
        products: getSelectedSet('filter-product', DASHBOARD_DATA.meta.values.product_types),
      };

      const current = applyFilters(startDate, endDate, selected);

      const duration = dayDiff(startDate, endDate);
      const priorEnd = shiftDate(startDate, -1);
      const priorStart = shiftDate(priorEnd, -(duration - 1));
      const prePriorEnd = shiftDate(priorStart, -1);
      const prePriorStart = shiftDate(prePriorEnd, -(duration - 1));

      const prior = applyFilters(priorStart, priorEnd, selected);
      const prePrior = applyFilters(prePriorStart, prePriorEnd, selected);

      const curSnap = computeSnapshot(current.tx, current.customers, current.spend, startDate, endDate);
      const priorSnap = computeSnapshot(prior.tx, prior.customers, prior.spend, priorStart, priorEnd);
      const prePriorSnap = computeSnapshot(prePrior.tx, prePrior.customers, prePrior.spend, prePriorStart, prePriorEnd);

      let growthRate = Number.isFinite(priorSnap.revenue) && priorSnap.revenue > 0
        ? (curSnap.revenue / priorSnap.revenue) - 1
        : NaN;
      let growthMethod = 'prior_period';
      if (!Number.isFinite(growthRate)) {
        const fallbackMonthly = aggregateMonthly(current.tx);
        if (fallbackMonthly.length >= 2) {
          const firstRevenue = fallbackMonthly[0].revenue;
          const lastRevenue = fallbackMonthly[fallbackMonthly.length - 1].revenue;
          if (Number.isFinite(firstRevenue) && Number.isFinite(lastRevenue) && firstRevenue > 0) {
            growthRate = (lastRevenue / firstRevenue) - 1;
            growthMethod = 'first_vs_last_month';
          }
        }
      }
      const priorGrowthRate = Number.isFinite(prePriorSnap.revenue) && prePriorSnap.revenue > 0
        ? (priorSnap.revenue / prePriorSnap.revenue) - 1
        : NaN;

      const delta = (cur, prev) => (Number.isFinite(prev) && prev !== 0 ? (cur / prev) - 1 : NaN);

      const kpis = [
        {
          label: 'Total Revenue',
          value: fmtCurrency(curSnap.revenue),
          delta: delta(curSnap.revenue, priorSnap.revenue),
          deltaText: Number.isFinite(delta(curSnap.revenue, priorSnap.revenue))
            ? `${delta(curSnap.revenue, priorSnap.revenue) >= 0 ? '▲' : '▼'} ${fmtPct(delta(curSnap.revenue, priorSnap.revenue))} vs prior`
            : 'No prior-period baseline',
          note: `Scope revenue from ${startDate} to ${endDate}`,
        },
        {
          label: 'Contribution Margin',
          value: fmtCurrency(curSnap.margin),
          delta: delta(curSnap.margin, priorSnap.margin),
          deltaText: Number.isFinite(delta(curSnap.margin, priorSnap.margin))
            ? `${delta(curSnap.margin, priorSnap.margin) >= 0 ? '▲' : '▼'} ${fmtPct(delta(curSnap.margin, priorSnap.margin))} vs prior`
            : 'No prior-period baseline',
          note: `Margin rate ${fmtPct(curSnap.marginPct)}`,
        },
        {
          label: 'Growth Rate',
          value: fmtPct(growthRate),
          delta: growthMethod === 'prior_period' && Number.isFinite(growthRate) && Number.isFinite(priorGrowthRate)
            ? (growthRate - priorGrowthRate)
            : NaN,
          deltaText: growthMethod === 'prior_period' && Number.isFinite(growthRate) && Number.isFinite(priorGrowthRate)
            ? `${growthRate - priorGrowthRate >= 0 ? '▲' : '▼'} ${(Math.abs(growthRate - priorGrowthRate) * 100).toFixed(1)}pp trend shift`
            : (growthMethod === 'first_vs_last_month'
              ? 'Fallback: first vs last month in selected range'
              : 'No baseline available'),
          note: growthMethod === 'prior_period'
            ? 'Period-over-period top-line growth'
            : 'Fallback growth estimate within selected scope',
        },
        {
          label: 'CAC',
          value: fmtCurrency(curSnap.CAC),
          delta: delta(curSnap.CAC, priorSnap.CAC),
          deltaText: Number.isFinite(delta(curSnap.CAC, priorSnap.CAC))
            ? `${delta(curSnap.CAC, priorSnap.CAC) <= 0 ? '▲' : '▼'} ${fmtPct(Math.abs(delta(curSnap.CAC, priorSnap.CAC)))} efficiency move`
            : 'No prior-period baseline',
          note: `${fmtNum(curSnap.acquiredCount, 0)} acquired customers in scope`,
        },
        {
          label: 'Average LTV',
          value: fmtCurrency(curSnap.avgLTV),
          delta: delta(curSnap.avgLTV, priorSnap.avgLTV),
          deltaText: Number.isFinite(delta(curSnap.avgLTV, priorSnap.avgLTV))
            ? `${delta(curSnap.avgLTV, priorSnap.avgLTV) >= 0 ? '▲' : '▼'} ${fmtPct(delta(curSnap.avgLTV, priorSnap.avgLTV))} vs prior`
            : 'No prior-period baseline',
          note: 'Observed contribution margin per acquired customer',
        },
        {
          label: 'LTV / CAC',
          value: fmtNum(curSnap.ltvToCac, 2),
          delta: delta(curSnap.ltvToCac, priorSnap.ltvToCac),
          deltaText: Number.isFinite(delta(curSnap.ltvToCac, priorSnap.ltvToCac))
            ? `${delta(curSnap.ltvToCac, priorSnap.ltvToCac) >= 0 ? '▲' : '▼'} ${fmtPct(delta(curSnap.ltvToCac, priorSnap.ltvToCac))} vs prior`
            : 'No prior-period baseline',
          note: `Higher is better; threshold target >= ${fmtNum(EFF_THRESH.ltv_cac_target, 1)}`,
        },
        {
          label: 'Approx. Payback',
          value: Number.isFinite(curSnap.payback) ? fmtNum(curSnap.payback, 1) + 'm' : 'n/a',
          delta: delta(curSnap.payback, priorSnap.payback),
          deltaText: Number.isFinite(delta(curSnap.payback, priorSnap.payback))
            ? `${delta(curSnap.payback, priorSnap.payback) <= 0 ? '▲' : '▼'} ${fmtPct(Math.abs(delta(curSnap.payback, priorSnap.payback)))} vs prior`
            : 'No prior-period baseline',
          note: 'Estimated CAC recovery period in months',
        },
      ];
      renderKpis(kpis);
      const palette = themeColors();

      const monthly = aggregateMonthly(current.tx);
      const monthlyRows = monthly.map(r => ({ x: dateToTs(r.month + '-01'), label: monthLabel(r.month), ...r }));

      renderLineChart('chart-revenue', monthlyRows, [{ key: 'revenue', label: 'Revenue', color: palette.rev }], fmtCurrency);
      renderLineChart('chart-margin', monthlyRows, [{ key: 'margin', label: 'Contribution Margin', color: palette.margin }], fmtCurrency);
      renderLineChart(
        'chart-revenue-cost',
        monthlyRows,
        [
          { key: 'revenue', label: 'Revenue', color: palette.rev },
          { key: 'cost', label: 'Cost', color: palette.cost },
        ],
        fmtCurrency
      );

      const cohort = computeCohortRetention(current.tx);
      const cohortRows = cohort.summary
        .filter(r => r.monthsSince <= 24)
        .map(r => ({ x: r.monthsSince, label: 'M' + r.monthsSince, retention: r.medianRevenueRetention || 0 }));
      renderLineChart('chart-cohort-retention', cohortRows, [{ key: 'retention', label: 'Revenue Retention', color: palette.bar }], fmtPct);

      const unitRows = computeUnitEconomicsByChannel(current, startDate, endDate, selected);
      renderScatterChart('chart-ltv-cac', unitRows);

      const segmentRows = computeSegmentProfitability(current.tx);
      renderBarChart('chart-segment-margin', segmentRows, 'margin', 'segment', fmtCurrency, palette.margin);

      const arptRows = computeAvgRevenuePerTxBySegment(current.tx);
      renderBarChart('chart-arpt-segment', arptRows, 'avgRevTx', 'segment', fmtCurrency, palette.accent);

      const customerRevenue = computeRevenueByCustomer(current.tx);
      renderHistogram('chart-revenue-distribution', customerRevenue);

      const regionRows = computeRegionProfitability(current.tx);
      renderRegionTable(regionRows.map(r => ({
        region: r.region,
        revenue: r.revenue,
        cost: r.cost,
        margin: r.margin,
        marginPct: r.marginPct,
      })));

      const risks = computeRiskRows(unitRows, segmentRows, cohort.decayByCohort);
      renderRiskTable(risks);

      const inefficient = unitRows.filter(r => r.status === 'inefficient').map(r => r.channel);
      const m6 = cohort.summary.find(r => r.monthsSince === 6);
      const m12 = cohort.summary.find(r => r.monthsSince === 12);
      const weakestSegment = [...segmentRows].sort((a, b) => a.marginPct - b.marginPct)[0];
      const revenueShareTop10 = (() => {
        const vals = [...customerRevenue].sort((a, b) => b - a);
        if (!vals.length) return NaN;
        const topN = Math.max(1, Math.floor(vals.length * 0.1));
        const total = vals.reduce((s, v) => s + v, 0);
        const top = vals.slice(0, topN).reduce((s, v) => s + v, 0);
        return total > 0 ? top / total : NaN;
      })();

      const insights = [
        {
          title: 'Growth vs Margin Quality',
          text: `Revenue changed ${fmtPct(growthRate)} vs prior period while margin rate sits at ${fmtPct(curSnap.marginPct)}.`
        },
        {
          title: 'Channel Efficiency Risk',
          text: inefficient.length
            ? `Inefficient channels detected: ${inefficient.join(', ')} (LTV/CAC < ${fmtNum(EFF_THRESH.ineff_ltv_cac, 1)} or payback > ${fmtNum(EFF_THRESH.ineff_payback_months, 0)} months).`
            : 'No channels flagged as inefficient under current filters.'
        },
        {
          title: 'Cohort Durability',
          text: `Median revenue retention is ${m6 ? fmtPct(m6.medianRevenueRetention) : 'n/a'} at month 6 and ${m12 ? fmtPct(m12.medianRevenueRetention) : 'n/a'} at month 12.`
        },
        {
          title: 'Profitability Concentration',
          text: weakestSegment
            ? `${weakestSegment.segment} is the weakest-margin segment at ${fmtPct(weakestSegment.marginPct)}; top decile customers contribute ${fmtPct(revenueShareTop10)} of revenue.`
            : 'Segment profitability view unavailable for current filters.'
        },
      ];
      renderSummaryStrip(insights);

      document.getElementById('summary-context').textContent =
        `Current scope: ${fmtNum(current.tx.length, 0)} transactions | ${fmtNum(new Set(current.tx.map(r => r.cid)).size, 0)} active customers`;
    }

    function selectAllFilters() {
      ['filter-segment', 'filter-region', 'filter-channel', 'filter-product'].forEach(id => {
        Array.from(document.getElementById(id).options).forEach(o => { o.selected = true; });
      });
    }

    function resetFilters() {
      document.getElementById('filter-start').value = DASHBOARD_DATA.meta.coverage_start;
      document.getElementById('filter-end').value = DASHBOARD_DATA.meta.coverage_end;
      selectAllFilters();
      computeAndRender();
    }

    function init() {
      applyTheme(resolveInitialTheme());
      document.getElementById('dashboard-title').textContent = DASHBOARD_DATA.meta.dashboard_title;
      document.getElementById('dashboard-subtitle').textContent = DASHBOARD_DATA.meta.question;
      document.getElementById('coverage-chip').textContent =
        `Data coverage: ${DASHBOARD_DATA.meta.coverage_start} to ${DASHBOARD_DATA.meta.coverage_end}`;
      populateMultiSelect('filter-segment', DASHBOARD_DATA.meta.values.segments);
      populateMultiSelect('filter-region', DASHBOARD_DATA.meta.values.regions);
      populateMultiSelect('filter-channel', DASHBOARD_DATA.meta.values.acquisition_channels);
      populateMultiSelect('filter-product', DASHBOARD_DATA.meta.values.product_types);

      document.getElementById('filter-start').value = DASHBOARD_DATA.meta.coverage_start;
      document.getElementById('filter-end').value = DASHBOARD_DATA.meta.coverage_end;
      document.getElementById('filter-start').min = DASHBOARD_DATA.meta.coverage_start;
      document.getElementById('filter-start').max = DASHBOARD_DATA.meta.coverage_end;
      document.getElementById('filter-end').min = DASHBOARD_DATA.meta.coverage_start;
      document.getElementById('filter-end').max = DASHBOARD_DATA.meta.coverage_end;

      ['filter-start', 'filter-end', 'filter-segment', 'filter-region', 'filter-channel', 'filter-product']
        .forEach(id => document.getElementById(id).addEventListener('change', () => {
          const start = document.getElementById('filter-start').value;
          const end = document.getElementById('filter-end').value;
          if (start > end) {
            document.getElementById('filter-end').value = start;
          }
          computeAndRender();
        }));

      document.getElementById('btn-select-all').addEventListener('click', () => {
        selectAllFilters();
        computeAndRender();
      });

      document.getElementById('btn-reset').addEventListener('click', resetFilters);
      document.getElementById('btn-theme').addEventListener('click', toggleTheme);

      computeAndRender();
      window.addEventListener('resize', () => computeAndRender());

      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addEventListener('change', (event) => {
        const hasManualChoice = !!window.localStorage.getItem(THEME_KEY);
        if (!hasManualChoice) {
          applyTheme(event.matches ? 'dark' : 'light');
          computeAndRender();
        }
      });
    }

    init();
  </script>
</body>
</html>
"""

    return template.replace("__DATA_JSON__", data_json)


def write_supporting_notes() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    build_note = """# Dashboard Build Note

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
"""

    section_decisions = """# Dashboard Sections and Decision Support

1. Header and Filters
- Decision supported: which slice of the business should be evaluated right now.

2. Executive Summary Strip
- Decision supported: immediate understanding of whether growth quality is improving or degrading.

3. KPI Row
- Decision supported: performance tracking vs prior period for revenue quality and unit economics.

4. Primary Analysis Section
- Decision supported: whether current growth is sustainable across trend, retention, and acquisition efficiency.

5. Diagnostic Section
- Decision supported: where profitability and monetization issues are concentrated (segment, region, transaction quality).

6. Risk / Priority Section
- Decision supported: what to act on first, with concrete risk interpretation and recommended actions.

7. Footer Notes
- Decision supported: confidence framing and methodological guardrails for interpretation.
"""

    (REPORTS_DIR / "dashboard_build_note.md").write_text(build_note, encoding="utf-8")
    (REPORTS_DIR / "dashboard_sections_decision_support.md").write_text(
        section_decisions, encoding="utf-8"
    )


def run() -> None:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)

    customers, transactions, marketing = load_inputs()
    payload = build_embedded_payload(customers, transactions, marketing)
    html = build_dashboard_html(payload)

    out_path = DASHBOARD_DIR / "executive_dashboard.html"
    out_path.write_text(html, encoding="utf-8")

    write_supporting_notes()

    print("Executive dashboard assets built.")
    print(f"dashboard_html: {out_path}")
    print(f"build_note: {REPORTS_DIR / 'dashboard_build_note.md'}")
    print(f"section_decisions: {REPORTS_DIR / 'dashboard_sections_decision_support.md'}")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
