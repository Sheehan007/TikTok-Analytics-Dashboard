"""Reusable KPI helpers for advertising product analytics."""


def safe_divide(numerator, denominator, default=0.0):
    """Return numerator / denominator, protecting dashboards from zero denominators."""
    if denominator in (0, 0.0, None):
        return default
    return numerator / denominator


def ctr(clicks, impressions):
    return safe_divide(clicks, impressions)


def cvr(conversions, clicks):
    return safe_divide(conversions, clicks)


def cpc(spend, clicks):
    return safe_divide(spend, clicks)


def cpm(spend, impressions):
    return safe_divide(spend, impressions) * 1000


def cpa(spend, conversions):
    return safe_divide(spend, conversions)


def roas(revenue, spend):
    return safe_divide(revenue, spend)


def retention(retained, cohort_size):
    return safe_divide(retained, cohort_size)


def growth(current_value, previous_value):
    return safe_divide(current_value - previous_value, previous_value)
