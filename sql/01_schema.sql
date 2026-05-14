-- Warehouse schema for TikTok Ads product performance analytics.

CREATE TABLE dim_advertiser (
    advertiser_id TEXT PRIMARY KEY,
    advertiser_name TEXT NOT NULL,
    advertiser_segment TEXT NOT NULL,
    industry TEXT NOT NULL,
    region TEXT NOT NULL,
    country TEXT NOT NULL,
    signup_month DATE NOT NULL
);

CREATE TABLE dim_campaign (
    campaign_id TEXT PRIMARY KEY,
    advertiser_id TEXT NOT NULL REFERENCES dim_advertiser(advertiser_id),
    campaign_name TEXT NOT NULL,
    campaign_objective TEXT NOT NULL,
    ad_product TEXT NOT NULL,
    launch_week DATE NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE fact_campaign_weekly_performance (
    week_start DATE NOT NULL,
    campaign_id TEXT NOT NULL REFERENCES dim_campaign(campaign_id),
    advertiser_id TEXT NOT NULL REFERENCES dim_advertiser(advertiser_id),
    region TEXT NOT NULL,
    country TEXT NOT NULL,
    advertiser_segment TEXT NOT NULL,
    campaign_objective TEXT NOT NULL,
    ad_product TEXT NOT NULL,
    spend NUMERIC(14, 2) NOT NULL,
    impressions INTEGER NOT NULL,
    clicks INTEGER NOT NULL,
    conversions INTEGER NOT NULL,
    revenue NUMERIC(14, 2) NOT NULL,
    advertiser_cohort INTEGER NOT NULL,
    retained_advertisers_d30 INTEGER NOT NULL,
    PRIMARY KEY (week_start, campaign_id)
);

CREATE TABLE fact_advertiser_retention_cohort (
    cohort_month DATE NOT NULL,
    region TEXT NOT NULL,
    country TEXT NOT NULL,
    advertiser_segment TEXT NOT NULL,
    campaign_objective TEXT NOT NULL,
    cohort_size INTEGER NOT NULL,
    retained_day_7 INTEGER NOT NULL,
    retained_day_30 INTEGER NOT NULL,
    retained_day_90 INTEGER NOT NULL,
    PRIMARY KEY (cohort_month, region, country, advertiser_segment, campaign_objective)
);

CREATE INDEX idx_campaign_week_country
    ON fact_campaign_weekly_performance (week_start, country);

CREATE INDEX idx_campaign_segment_objective
    ON fact_campaign_weekly_performance (advertiser_segment, campaign_objective);

CREATE INDEX idx_campaign_product
    ON fact_campaign_weekly_performance (ad_product);
