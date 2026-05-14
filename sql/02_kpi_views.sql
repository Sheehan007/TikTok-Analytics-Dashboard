-- KPI views that can be materialized in a warehouse or connected to BI tools.

CREATE VIEW vw_weekly_product_kpis AS
SELECT
    week_start,
    region,
    country,
    advertiser_segment,
    campaign_objective,
    ad_product,
    SUM(spend) AS spend,
    SUM(impressions) AS impressions,
    SUM(clicks) AS clicks,
    SUM(conversions) AS conversions,
    SUM(revenue) AS revenue,
    CAST(SUM(clicks) AS REAL) / NULLIF(SUM(impressions), 0) AS ctr,
    CAST(SUM(conversions) AS REAL) / NULLIF(SUM(clicks), 0) AS cvr,
    SUM(spend) / NULLIF(SUM(clicks), 0) AS cpc,
    SUM(spend) / NULLIF(SUM(impressions), 0) * 1000 AS cpm,
    SUM(spend) / NULLIF(SUM(conversions), 0) AS cpa,
    SUM(revenue) / NULLIF(SUM(spend), 0) AS roas,
    CAST(SUM(retained_advertisers_d30) AS REAL) / NULLIF(SUM(advertiser_cohort), 0) AS d30_retention
FROM fact_campaign_weekly_performance
GROUP BY
    week_start,
    region,
    country,
    advertiser_segment,
    campaign_objective,
    ad_product;

CREATE VIEW vw_country_scorecard AS
SELECT
    region,
    country,
    SUM(spend) AS spend,
    SUM(revenue) AS revenue,
    SUM(impressions) AS impressions,
    SUM(clicks) AS clicks,
    SUM(conversions) AS conversions,
    SUM(revenue) / NULLIF(SUM(spend), 0) AS roas,
    SUM(spend) / NULLIF(SUM(conversions), 0) AS cpa,
    CAST(SUM(clicks) AS REAL) / NULLIF(SUM(impressions), 0) AS ctr,
    CAST(SUM(conversions) AS REAL) / NULLIF(SUM(clicks), 0) AS cvr,
    CAST(SUM(retained_advertisers_d30) AS REAL) / NULLIF(SUM(advertiser_cohort), 0) AS d30_retention
FROM fact_campaign_weekly_performance
GROUP BY region, country;

CREATE VIEW vw_segment_objective_diagnostics AS
SELECT
    region,
    advertiser_segment,
    campaign_objective,
    ad_product,
    SUM(spend) AS spend,
    SUM(revenue) AS revenue,
    SUM(revenue) / NULLIF(SUM(spend), 0) AS roas,
    SUM(spend) / NULLIF(SUM(conversions), 0) AS cpa,
    CAST(SUM(conversions) AS REAL) / NULLIF(SUM(clicks), 0) AS cvr,
    CAST(SUM(retained_advertisers_d30) AS REAL) / NULLIF(SUM(advertiser_cohort), 0) AS d30_retention
FROM fact_campaign_weekly_performance
GROUP BY region, advertiser_segment, campaign_objective, ad_product;
