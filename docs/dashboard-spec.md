# Dashboard Specification

## Data Model

### Fact Tables

- `fact_campaign_weekly_performance`
  - Grain: one campaign, one week.
  - Measures: spend, impressions, clicks, conversions, revenue, retained advertisers, advertiser cohort.
- `fact_advertiser_retention_cohort`
  - Grain: region, country, segment, objective, cohort month.
  - Measures: cohort size, retained day 7, retained day 30, retained day 90.

### Dimensions

- `dim_advertiser`
- `dim_campaign`
- `dim_market`
- `dim_calendar`
- `dim_campaign_objective`
- `dim_ad_product`

## Power BI Measures

```DAX
Spend = SUM(fact_campaign_weekly_performance[spend])
Revenue = SUM(fact_campaign_weekly_performance[revenue])
Impressions = SUM(fact_campaign_weekly_performance[impressions])
Clicks = SUM(fact_campaign_weekly_performance[clicks])
Conversions = SUM(fact_campaign_weekly_performance[conversions])

CTR = DIVIDE([Clicks], [Impressions])
CVR = DIVIDE([Conversions], [Clicks])
CPC = DIVIDE([Spend], [Clicks])
CPM = DIVIDE([Spend], [Impressions]) * 1000
CPA = DIVIDE([Spend], [Conversions])
ROAS = DIVIDE([Revenue], [Spend])

D30 Retention =
DIVIDE(
    SUM(fact_campaign_weekly_performance[retained_advertisers_d30]),
    SUM(fact_campaign_weekly_performance[advertiser_cohort])
)

Revenue Growth =
VAR CurrentRevenue = [Revenue]
VAR PreviousRevenue =
    CALCULATE(
        [Revenue],
        DATEADD(dim_calendar[week_start], -28, DAY)
    )
RETURN DIVIDE(CurrentRevenue - PreviousRevenue, PreviousRevenue)
```

## Tableau Calculations

```text
CTR = SUM([Clicks]) / SUM([Impressions])
CVR = SUM([Conversions]) / SUM([Clicks])
CPC = SUM([Spend]) / SUM([Clicks])
CPM = SUM([Spend]) / SUM([Impressions]) * 1000
CPA = SUM([Spend]) / SUM([Conversions])
ROAS = SUM([Revenue]) / SUM([Spend])
D30 Retention = SUM([Retained Advertisers D30]) / SUM([Advertiser Cohort])
Revenue Growth = (SUM([Revenue]) - LOOKUP(SUM([Revenue]), -4)) / LOOKUP(SUM([Revenue]), -4)
```

## Recommended Pages

1. Executive Overview
   - KPI scorecards, revenue and spend trend, market efficiency map.
2. Regional Performance
   - Region and country ROAS, CPA, revenue growth, and retention.
3. Funnel Diagnostics
   - Impressions to clicks, clicks to conversions, conversions to revenue.
4. Segment and Objective Drilldown
   - SMB, Mid-Market, Enterprise, and Agency views by objective and ad product.
5. Product Recommendations
   - Prioritized underperforming segments with action, expected impact, and owner.

## Interaction Design

- Filters: period, region, country, advertiser segment, campaign objective, ad product.
- Drilldowns: region to country, segment to objective, product to campaign.
- Alerts: ROAS below 1.8, CPA above segment benchmark, CVR below benchmark, negative four-week revenue growth.
- Exports: weekly business review CSV and recommendation list.
