# TikTok Ads Product Performance Analytics Dashboard

An end-to-end product analytics project for evaluating advertising product performance across regions, campaign objectives, advertiser segments, products, and weekly periods.

The project includes a SQL data model, a deterministic Python data pipeline, generated KPI marts, Tableau/Power BI measure definitions, and an interactive dashboard built with vanilla HTML, CSS, and JavaScript.

## Business Questions

- Which regions, countries, advertiser segments, objectives, and ad products are driving the highest ROAS?
- Where does the impressions to clicks to conversions to revenue funnel lose the most value?
- Which product segments are underperforming relative to spend, CPA, CVR, and revenue growth?
- Which markets should product marketing prioritize for scale, enablement, or workflow improvements?

## Core KPIs

| Metric | Definition |
| --- | --- |
| CTR | Clicks / impressions |
| CVR | Conversions / clicks |
| CPC | Spend / clicks |
| CPM | Spend / impressions * 1000 |
| CPA | Spend / conversions |
| ROAS | Revenue / spend |
| D30 retention | Retained advertisers at day 30 / advertiser cohort |
| Revenue growth | Current period revenue vs previous matched period |

## Project Structure

```text
.
├── index.html                         # Interactive dashboard
├── assets/
│   ├── dashboard.js                    # Dashboard interactions and chart rendering
│   ├── data.js                         # Generated dashboard dataset
│   └── styles.css                      # Dashboard design system
├── data/
│   ├── raw/                            # Generated source-like dimensional data
│   ├── facts/                          # Campaign weekly performance and cohorts
│   └── marts/                          # Aggregated KPI tables used by the dashboard
├── docs/
│   ├── dashboard-spec.md               # Tableau/Power BI implementation spec
│   └── insights.md                     # Product recommendations and analysis summary
├── scripts/
│   ├── generate_project_data.py        # Deterministic data generator and mart builder
│   └── metrics.py                      # KPI helper functions
├── sql/
│   ├── 01_schema.sql                   # Warehouse schema
│   ├── 02_kpi_views.sql                # KPI views
│   └── 03_business_review_queries.sql  # Business review queries
└── tests/
    └── test_metrics.py                 # KPI calculation tests
```

## Run Locally

Generate the data and dashboard payload:

```bash
npm run build:data
```

Run tests:

```bash
npm test
```

Preview the dashboard:

```bash
npm run serve
```

Then open `http://localhost:4317`.

## Dashboard Views

- Executive KPI scorecard for spend, revenue, ROAS, CTR, CVR, CPA, and retention.
- Weekly trend monitoring for revenue and spend.
- Regional and country performance comparisons.
- Funnel analysis from impressions to clicks to conversions to revenue.
- Advertiser segment diagnostics with prioritized recommendations.
- Campaign objective and ad product efficiency views for weekly business reviews.
