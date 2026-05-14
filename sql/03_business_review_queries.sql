-- Weekly business review queries.

-- 1. Last 8 weeks of product trend monitoring.
SELECT
    week_start,
    ad_product,
    SUM(spend) AS spend,
    SUM(revenue) AS revenue,
    SUM(revenue) / NULLIF(SUM(spend), 0) AS roas,
    SUM(spend) / NULLIF(SUM(conversions), 0) AS cpa
FROM fact_campaign_weekly_performance
WHERE week_start >= DATE((SELECT MAX(week_start) FROM fact_campaign_weekly_performance), '-56 day')
GROUP BY week_start, ad_product
ORDER BY week_start, ad_product;

-- 2. Country-level markets with high spend and low ROAS.
SELECT
    region,
    country,
    SUM(spend) AS spend,
    SUM(revenue) AS revenue,
    SUM(revenue) / NULLIF(SUM(spend), 0) AS roas,
    SUM(spend) / NULLIF(SUM(conversions), 0) AS cpa
FROM fact_campaign_weekly_performance
GROUP BY region, country
HAVING spend > 250000 AND roas < 2.0
ORDER BY spend DESC;

-- 3. Funnel drop-off by segment and objective.
SELECT
    advertiser_segment,
    campaign_objective,
    SUM(impressions) AS impressions,
    SUM(clicks) AS clicks,
    SUM(conversions) AS conversions,
    SUM(revenue) AS revenue,
    CAST(SUM(clicks) AS REAL) / NULLIF(SUM(impressions), 0) AS impression_to_click_rate,
    CAST(SUM(conversions) AS REAL) / NULLIF(SUM(clicks), 0) AS click_to_conversion_rate,
    SUM(revenue) / NULLIF(SUM(conversions), 0) AS revenue_per_conversion
FROM fact_campaign_weekly_performance
GROUP BY advertiser_segment, campaign_objective
ORDER BY revenue DESC;

-- 4. Product recommendation candidates.
WITH segment_rollup AS (
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
    GROUP BY region, advertiser_segment, campaign_objective, ad_product
)
SELECT *
FROM segment_rollup
WHERE roas < 1.8 OR cvr < 0.055 OR d30_retention < 0.48
ORDER BY spend DESC
LIMIT 20;
