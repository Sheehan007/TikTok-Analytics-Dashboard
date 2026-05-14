"""Generate deterministic sample data and KPI marts for the dashboard.

The dataset is synthetic, but the schema and calculations mirror a practical ads
product analytics workflow: campaign performance, advertiser cohorts, weekly
market reporting, funnel diagnostics, and segment recommendations.
"""

from __future__ import annotations

import csv
import json
import math
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from metrics import cpa, cpc, cpm, ctr, cvr, growth, retention, roas


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
FACT_DIR = ROOT / "data" / "facts"
MART_DIR = ROOT / "data" / "marts"
ASSET_DIR = ROOT / "assets"
START_WEEK = date(2025, 1, 6)
WEEK_COUNT = 52
RANDOM_SEED = 20260514


COUNTRIES = [
    {"region": "North America", "country": "United States", "market_size": 1.35, "commerce": 1.18, "setup": 1.08},
    {"region": "North America", "country": "Canada", "market_size": 0.72, "commerce": 1.08, "setup": 1.03},
    {"region": "Europe", "country": "United Kingdom", "market_size": 0.92, "commerce": 1.12, "setup": 1.05},
    {"region": "Europe", "country": "Germany", "market_size": 0.84, "commerce": 1.06, "setup": 1.01},
    {"region": "Europe", "country": "France", "market_size": 0.76, "commerce": 0.98, "setup": 0.96},
    {"region": "Middle East & Africa", "country": "United Arab Emirates", "market_size": 0.66, "commerce": 1.22, "setup": 1.04},
    {"region": "Middle East & Africa", "country": "Saudi Arabia", "market_size": 0.74, "commerce": 1.15, "setup": 0.97},
    {"region": "Middle East & Africa", "country": "South Africa", "market_size": 0.58, "commerce": 0.91, "setup": 0.88},
    {"region": "Asia Pacific", "country": "Japan", "market_size": 0.86, "commerce": 1.16, "setup": 1.02},
    {"region": "Asia Pacific", "country": "South Korea", "market_size": 0.78, "commerce": 1.14, "setup": 1.01},
    {"region": "Asia Pacific", "country": "Australia", "market_size": 0.68, "commerce": 1.09, "setup": 1.04},
    {"region": "Asia Pacific", "country": "Indonesia", "market_size": 0.98, "commerce": 0.93, "setup": 0.9},
]

SEGMENTS = {
    "SMB": {"budget": 0.62, "ctr": 1.02, "cvr": 0.76, "retention": 0.78, "aov": 0.78},
    "Mid-Market": {"budget": 1.0, "ctr": 1.06, "cvr": 0.96, "retention": 0.94, "aov": 1.0},
    "Enterprise": {"budget": 1.72, "ctr": 1.0, "cvr": 1.18, "retention": 1.12, "aov": 1.26},
    "Agency": {"budget": 1.36, "ctr": 1.11, "cvr": 1.08, "retention": 1.04, "aov": 1.12},
}

OBJECTIVES = {
    "Conversions": {"ctr": 0.92, "cvr": 1.28, "cpm": 1.16, "value": 1.18},
    "Traffic": {"ctr": 1.24, "cvr": 0.64, "cpm": 0.82, "value": 0.72},
    "Lead Generation": {"ctr": 1.02, "cvr": 1.12, "cpm": 0.96, "value": 0.9},
    "App Installs": {"ctr": 0.96, "cvr": 0.86, "cpm": 1.02, "value": 0.84},
    "Catalog Sales": {"ctr": 1.06, "cvr": 1.18, "cpm": 1.08, "value": 1.24},
}

PRODUCTS = {
    "Spark Ads": {"ctr": 1.16, "cvr": 1.02, "cpm": 1.04, "retention": 1.04},
    "Smart Performance Campaign": {"ctr": 1.02, "cvr": 1.2, "cpm": 1.12, "retention": 1.1},
    "Lead Gen Forms": {"ctr": 0.98, "cvr": 1.16, "cpm": 0.92, "retention": 1.02},
    "App Promotion": {"ctr": 1.0, "cvr": 0.9, "cpm": 1.0, "retention": 0.96},
    "Catalog Ads": {"ctr": 1.1, "cvr": 1.14, "cpm": 1.08, "retention": 1.08},
}

INDUSTRIES = [
    "Retail",
    "Gaming",
    "Beauty",
    "Fintech",
    "Travel",
    "Education",
    "Consumer Apps",
    "Food & Beverage",
]

PRODUCT_BY_OBJECTIVE = {
    "Conversions": ["Smart Performance Campaign", "Spark Ads", "Catalog Ads"],
    "Traffic": ["Spark Ads", "Smart Performance Campaign", "App Promotion"],
    "Lead Generation": ["Lead Gen Forms", "Spark Ads", "Smart Performance Campaign"],
    "App Installs": ["App Promotion", "Spark Ads", "Smart Performance Campaign"],
    "Catalog Sales": ["Catalog Ads", "Smart Performance Campaign", "Spark Ads"],
}


def ensure_dirs() -> None:
    for folder in (RAW_DIR, FACT_DIR, MART_DIR, ASSET_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def week_dates() -> list[date]:
    return [START_WEEK + timedelta(days=7 * idx) for idx in range(WEEK_COUNT)]


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def round_money(value: float) -> float:
    return round(value, 2)


def pick_country(rng: random.Random) -> dict:
    weighted = []
    for country in COUNTRIES:
        weighted.extend([country] * max(1, int(country["market_size"] * 10)))
    return rng.choice(weighted)


def generate_advertisers(rng: random.Random, count: int = 180) -> list[dict]:
    advertisers = []
    segment_weights = ["SMB"] * 9 + ["Mid-Market"] * 6 + ["Enterprise"] * 3 + ["Agency"] * 4

    for idx in range(1, count + 1):
        market = pick_country(rng)
        segment = rng.choice(segment_weights)
        industry = rng.choice(INDUSTRIES)
        signup_month = date(2024, rng.randint(1, 12), 1)
        advertisers.append(
            {
                "advertiser_id": f"ADV{idx:04d}",
                "advertiser_name": f"{industry.replace(' ', '')} Signal {idx:03d}",
                "advertiser_segment": segment,
                "industry": industry,
                "region": market["region"],
                "country": market["country"],
                "signup_month": signup_month.isoformat(),
                "market_size": market["market_size"],
                "commerce": market["commerce"],
                "setup": market["setup"],
            }
        )

    return advertisers


def generate_campaigns(rng: random.Random, advertisers: list[dict]) -> list[dict]:
    campaigns = []
    campaign_idx = 1
    objective_weights = (
        ["Conversions"] * 8
        + ["Traffic"] * 5
        + ["Lead Generation"] * 5
        + ["App Installs"] * 4
        + ["Catalog Sales"] * 5
    )

    for advertiser in advertisers:
        campaign_count = {"SMB": 1, "Mid-Market": 2, "Enterprise": 3, "Agency": 3}[advertiser["advertiser_segment"]]
        if rng.random() < 0.22:
            campaign_count += 1

        for ordinal in range(1, campaign_count + 1):
            objective = rng.choice(objective_weights)
            product = rng.choice(PRODUCT_BY_OBJECTIVE[objective])
            launch_offset = rng.randint(0, 13)
            status = "Active" if rng.random() > 0.08 else "Paused"
            campaigns.append(
                {
                    "campaign_id": f"CMP{campaign_idx:05d}",
                    "advertiser_id": advertiser["advertiser_id"],
                    "campaign_name": f"{product} {objective} {ordinal}",
                    "campaign_objective": objective,
                    "ad_product": product,
                    "launch_week": (START_WEEK + timedelta(days=7 * launch_offset)).isoformat(),
                    "status": status,
                }
            )
            campaign_idx += 1

    return campaigns


def performance_row(
    rng: random.Random,
    week: date,
    week_index: int,
    campaign: dict,
    advertiser: dict,
) -> dict | None:
    launch = date.fromisoformat(campaign["launch_week"])
    if week < launch:
        return None

    weeks_since_launch = (week - launch).days // 7
    if campaign["status"] == "Paused" and rng.random() < 0.58:
        return None

    segment = SEGMENTS[advertiser["advertiser_segment"]]
    objective = OBJECTIVES[campaign["campaign_objective"]]
    product = PRODUCTS[campaign["ad_product"]]

    seasonality = 1 + 0.11 * math.sin((week_index / WEEK_COUNT) * math.tau) + 0.05 * math.sin((week_index / 13) * math.tau)
    learning = min(1.12, 0.78 + weeks_since_launch * 0.014)
    budget_noise = rng.uniform(0.72, 1.28)

    base_impressions = 52000
    impressions = int(
        base_impressions
        * advertiser["market_size"]
        * segment["budget"]
        * seasonality
        * learning
        * budget_noise
    )
    impressions = max(2500, impressions)

    ctr_rate = 0.0125 * segment["ctr"] * objective["ctr"] * product["ctr"] * advertiser["setup"] * rng.uniform(0.82, 1.18)
    cvr_rate = 0.068 * segment["cvr"] * objective["cvr"] * product["cvr"] * advertiser["setup"] * rng.uniform(0.78, 1.2)

    clicks = max(1, int(impressions * ctr_rate))
    conversions = max(0, int(clicks * cvr_rate))

    cpm_rate = 8.8 * objective["cpm"] * product["cpm"] * rng.uniform(0.86, 1.18)
    spend = impressions * cpm_rate / 1000

    value_per_conversion = 46 * advertiser["commerce"] * segment["aov"] * objective["value"] * rng.uniform(0.84, 1.22)
    revenue = conversions * value_per_conversion

    retention_rate = min(
        0.92,
        0.46 * segment["retention"] * product["retention"] * advertiser["setup"] * rng.uniform(0.88, 1.1),
    )
    retained = 1 if rng.random() < retention_rate else 0

    return {
        "week_start": week.isoformat(),
        "campaign_id": campaign["campaign_id"],
        "advertiser_id": advertiser["advertiser_id"],
        "region": advertiser["region"],
        "country": advertiser["country"],
        "advertiser_segment": advertiser["advertiser_segment"],
        "campaign_objective": campaign["campaign_objective"],
        "ad_product": campaign["ad_product"],
        "spend": round_money(spend),
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "revenue": round_money(revenue),
        "advertiser_cohort": 1,
        "retained_advertisers_d30": retained,
    }


def generate_performance(
    rng: random.Random,
    advertisers: list[dict],
    campaigns: list[dict],
) -> list[dict]:
    advertiser_by_id = {row["advertiser_id"]: row for row in advertisers}
    rows = []
    for week_index, week in enumerate(week_dates()):
        for campaign in campaigns:
            advertiser = advertiser_by_id[campaign["advertiser_id"]]
            row = performance_row(rng, week, week_index, campaign, advertiser)
            if row:
                rows.append(row)
    return rows


def aggregate(rows: list[dict], keys: list[str]) -> list[dict]:
    buckets = defaultdict(lambda: defaultdict(float))
    for row in rows:
        key = tuple(row[field] for field in keys)
        bucket = buckets[key]
        for metric in (
            "spend",
            "impressions",
            "clicks",
            "conversions",
            "revenue",
            "advertiser_cohort",
            "retained_advertisers_d30",
        ):
            bucket[metric] += row[metric]

    aggregated = []
    for key, values in buckets.items():
        record = {field: key[idx] for idx, field in enumerate(keys)}
        spend = values["spend"]
        impressions = int(values["impressions"])
        clicks = int(values["clicks"])
        conversions = int(values["conversions"])
        revenue = values["revenue"]
        record.update(
            {
                "spend": round_money(spend),
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
                "revenue": round_money(revenue),
                "ctr": round(ctr(clicks, impressions), 5),
                "cvr": round(cvr(conversions, clicks), 5),
                "cpc": round_money(cpc(spend, clicks)),
                "cpm": round_money(cpm(spend, impressions)),
                "cpa": round_money(cpa(spend, conversions)),
                "roas": round(roas(revenue, spend), 3),
                "d30_retention": round(retention(values["retained_advertisers_d30"], values["advertiser_cohort"]), 3),
                "advertiser_cohort": int(values["advertiser_cohort"]),
                "retained_advertisers_d30": int(values["retained_advertisers_d30"]),
            }
        )
        aggregated.append(record)

    return sorted(aggregated, key=lambda item: tuple(item[field] for field in keys))


def generate_retention_cohorts(rng: random.Random) -> list[dict]:
    cohorts = []
    for month in range(1, 13):
        cohort_month = date(2025, month, 1)
        for country in COUNTRIES:
            for segment_name, segment in SEGMENTS.items():
                for objective_name, objective in OBJECTIVES.items():
                    size = max(12, int(24 * country["market_size"] * segment["budget"] * rng.uniform(0.74, 1.24)))
                    d7_rate = min(0.92, 0.68 * segment["retention"] * country["setup"] * rng.uniform(0.92, 1.08))
                    d30_rate = min(0.86, d7_rate * 0.76 * objective["cvr"] * rng.uniform(0.9, 1.05))
                    d90_rate = min(0.72, d30_rate * 0.64 * rng.uniform(0.9, 1.05))
                    cohorts.append(
                        {
                            "cohort_month": cohort_month.isoformat(),
                            "region": country["region"],
                            "country": country["country"],
                            "advertiser_segment": segment_name,
                            "campaign_objective": objective_name,
                            "cohort_size": size,
                            "retained_day_7": int(size * d7_rate),
                            "retained_day_30": int(size * d30_rate),
                            "retained_day_90": int(size * d90_rate),
                        }
                    )
    return cohorts


def recommendation_for(record: dict) -> tuple[str, str]:
    if record["roas"] >= 2.7 and record["revenue_growth"] > 0.08:
        return "Scale", "Increase market budget and package winning setup pattern."
    if record["cvr"] < 0.055 and record["roas"] < 1.9:
        return "High", "Fix conversion setup, pixel readiness, and campaign objective guidance."
    if record["d30_retention"] < 0.48:
        return "High", "Launch retention intervention for first-month advertiser success."
    if record["cpa"] > 38 and record["roas"] < 2.1:
        return "Medium", "Tighten bidding guardrails and creative quality checks."
    return "Monitor", "Track in weekly business review and compare against segment benchmark."


def generate_recommendations(performance_rows: list[dict]) -> list[dict]:
    weeks = sorted({row["week_start"] for row in performance_rows})
    current_weeks = set(weeks[-8:])
    previous_weeks = set(weeks[-16:-8])

    current = aggregate(
        [row for row in performance_rows if row["week_start"] in current_weeks],
        ["region", "advertiser_segment", "campaign_objective", "ad_product"],
    )
    previous = aggregate(
        [row for row in performance_rows if row["week_start"] in previous_weeks],
        ["region", "advertiser_segment", "campaign_objective", "ad_product"],
    )
    previous_by_key = {
        (row["region"], row["advertiser_segment"], row["campaign_objective"], row["ad_product"]): row
        for row in previous
    }

    recommendations = []
    for row in current:
        key = (row["region"], row["advertiser_segment"], row["campaign_objective"], row["ad_product"])
        previous_revenue = previous_by_key.get(key, {}).get("revenue", 0)
        row["revenue_growth"] = round(growth(row["revenue"], previous_revenue), 3)
        priority, action = recommendation_for(row)
        target_roas = 2.4 if priority in {"High", "Medium"} else row["roas"] * 1.12
        upside = max(0, (target_roas * row["spend"]) - row["revenue"])
        recommendations.append(
            {
                "region": row["region"],
                "advertiser_segment": row["advertiser_segment"],
                "campaign_objective": row["campaign_objective"],
                "ad_product": row["ad_product"],
                "spend": row["spend"],
                "revenue": row["revenue"],
                "roas": row["roas"],
                "cvr": row["cvr"],
                "cpa": row["cpa"],
                "d30_retention": row["d30_retention"],
                "revenue_growth": row["revenue_growth"],
                "priority": priority,
                "recommended_action": action,
                "estimated_revenue_upside": round_money(upside),
            }
        )

    priority_order = {"High": 0, "Medium": 1, "Scale": 2, "Monitor": 3}
    return sorted(
        recommendations,
        key=lambda item: (priority_order[item["priority"]], -item["estimated_revenue_upside"], -item["spend"]),
    )[:36]


def dashboard_payload(weekly: list[dict], countries: list[dict], recommendations: list[dict]) -> dict:
    filters = {
        "regions": sorted({row["region"] for row in weekly}),
        "countries": sorted({row["country"] for row in weekly}),
        "segments": sorted({row["advertiser_segment"] for row in weekly}),
        "objectives": sorted({row["campaign_objective"] for row in weekly}),
        "products": sorted({row["ad_product"] for row in weekly}),
    }
    return {
        "metadata": {
            "project": "TikTok Ads Product Performance Analytics Dashboard",
            "generatedOn": date.today().isoformat(),
            "source": "Synthetic campaign, advertiser, and cohort data generated by scripts/generate_project_data.py",
            "weeks": WEEK_COUNT,
            "weeklyRecords": len(weekly),
        },
        "benchmarks": {
            "roas": 2.25,
            "cvr": 0.065,
            "ctr": 0.012,
            "d30Retention": 0.52,
            "cpa": 34,
        },
        "filters": filters,
        "weeklyPerformance": weekly,
        "countryScorecard": countries,
        "segmentRecommendations": recommendations,
    }


def write_dashboard_data(payload: dict) -> None:
    content = "window.ADS_PRODUCT_ANALYTICS = "
    content += json.dumps(payload, indent=2, sort_keys=True)
    content += ";\n"
    (ASSET_DIR / "data.js").write_text(content, encoding="utf-8")


def write_data_readme() -> None:
    readme = """# Data

This folder contains deterministic synthetic data for the TikTok Ads product analytics project.

- `raw/advertisers.csv`: advertiser dimensions and market attributes.
- `raw/campaigns.csv`: campaign objective, product, launch week, and status.
- `facts/campaign_weekly_performance.csv`: weekly campaign spend, impressions, clicks, conversions, revenue, and retention flags.
- `facts/advertiser_retention_cohorts.csv`: advertiser retention cohorts by market, segment, and objective.
- `marts/weekly_product_performance.csv`: dashboard-ready weekly KPI mart.
- `marts/country_scorecard.csv`: country-level rollup for regional comparisons.
- `marts/segment_recommendations.csv`: prioritized product recommendations.
"""
    (ROOT / "data" / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rng = random.Random(RANDOM_SEED)

    advertisers = generate_advertisers(rng)
    campaigns = generate_campaigns(rng, advertisers)
    performance = generate_performance(rng, advertisers, campaigns)
    cohorts = generate_retention_cohorts(rng)

    advertisers_export = [
        {key: row[key] for key in ("advertiser_id", "advertiser_name", "advertiser_segment", "industry", "region", "country", "signup_month")}
        for row in advertisers
    ]
    write_csv(
        RAW_DIR / "advertisers.csv",
        advertisers_export,
        ["advertiser_id", "advertiser_name", "advertiser_segment", "industry", "region", "country", "signup_month"],
    )
    write_csv(
        RAW_DIR / "campaigns.csv",
        campaigns,
        ["campaign_id", "advertiser_id", "campaign_name", "campaign_objective", "ad_product", "launch_week", "status"],
    )
    write_csv(
        FACT_DIR / "campaign_weekly_performance.csv",
        performance,
        [
            "week_start",
            "campaign_id",
            "advertiser_id",
            "region",
            "country",
            "advertiser_segment",
            "campaign_objective",
            "ad_product",
            "spend",
            "impressions",
            "clicks",
            "conversions",
            "revenue",
            "advertiser_cohort",
            "retained_advertisers_d30",
        ],
    )
    write_csv(
        FACT_DIR / "advertiser_retention_cohorts.csv",
        cohorts,
        [
            "cohort_month",
            "region",
            "country",
            "advertiser_segment",
            "campaign_objective",
            "cohort_size",
            "retained_day_7",
            "retained_day_30",
            "retained_day_90",
        ],
    )

    weekly = aggregate(
        performance,
        ["week_start", "region", "country", "advertiser_segment", "campaign_objective", "ad_product"],
    )
    country_scorecard = aggregate(performance, ["region", "country"])
    recommendations = generate_recommendations(performance)

    write_csv(
        MART_DIR / "weekly_product_performance.csv",
        weekly,
        [
            "week_start",
            "region",
            "country",
            "advertiser_segment",
            "campaign_objective",
            "ad_product",
            "spend",
            "impressions",
            "clicks",
            "conversions",
            "revenue",
            "ctr",
            "cvr",
            "cpc",
            "cpm",
            "cpa",
            "roas",
            "d30_retention",
            "advertiser_cohort",
            "retained_advertisers_d30",
        ],
    )
    write_csv(
        MART_DIR / "country_scorecard.csv",
        country_scorecard,
        [
            "region",
            "country",
            "spend",
            "impressions",
            "clicks",
            "conversions",
            "revenue",
            "ctr",
            "cvr",
            "cpc",
            "cpm",
            "cpa",
            "roas",
            "d30_retention",
            "advertiser_cohort",
            "retained_advertisers_d30",
        ],
    )
    write_csv(
        MART_DIR / "segment_recommendations.csv",
        recommendations,
        [
            "region",
            "advertiser_segment",
            "campaign_objective",
            "ad_product",
            "spend",
            "revenue",
            "roas",
            "cvr",
            "cpa",
            "d30_retention",
            "revenue_growth",
            "priority",
            "recommended_action",
            "estimated_revenue_upside",
        ],
    )

    payload = dashboard_payload(weekly, country_scorecard, recommendations)
    write_dashboard_data(payload)
    write_data_readme()

    print(
        "Generated "
        f"{len(advertisers)} advertisers, {len(campaigns)} campaigns, "
        f"{len(performance)} fact rows, and {len(weekly)} dashboard mart rows."
    )


if __name__ == "__main__":
    main()
