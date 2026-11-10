from __future__ import annotations

from collections import defaultdict
from typing import Any


def safe_divide(numerator: float, denominator: float) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def calculate_kpis(spend: float, leads: int, customers: int, revenue: float,
                   qualified_leads: int) -> dict[str, float | None]:
    return {
        "cpl": safe_divide(spend, leads),
        "cpa": safe_divide(spend, customers),
        "roas": safe_divide(revenue, spend),
        "lead_quality_rate": safe_divide(qualified_leads, leads),
    }


def reconcile(ad_rows: list[dict[str, Any]], fact_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    source = defaultdict(lambda: {"spend": 0.0, "clicks": 0})
    dashboard = defaultdict(lambda: {"spend": 0.0, "clicks": 0})
    for row in ad_rows:
        source[row["source"]]["spend"] += float(row["spend"])
        source[row["source"]]["clicks"] += int(row["clicks"])
    for row in fact_rows:
        dashboard[row["source"]]["spend"] += float(row["spend"])
        dashboard[row["source"]]["clicks"] += int(row["clicks"])
    output = []
    for name in sorted(source.keys() | dashboard.keys()):
        output.append({"source": name, "source_spend": round(source[name]["spend"], 2),
                       "dashboard_spend": round(dashboard[name]["spend"], 2),
                       "spend_variance": round(source[name]["spend"] - dashboard[name]["spend"], 2),
                       "source_clicks": source[name]["clicks"],
                       "dashboard_clicks": dashboard[name]["clicks"],
                       "click_variance": source[name]["clicks"] - dashboard[name]["clicks"]})
    return output

