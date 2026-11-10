from __future__ import annotations

import csv
from pathlib import Path

from .config import settings
from .database import Database
from .metrics import reconcile

FACT_QUERY = """
WITH crm AS (
 SELECT created_date, source, campaign_id, COUNT(*) AS leads,
        SUM(CASE WHEN lead_score >= 60 THEN 1 ELSE 0 END) AS qualified_leads,
        SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) AS customers,
        SUM(revenue) AS revenue
 FROM crm_leads GROUP BY created_date, source, campaign_id
), web AS (
 SELECT event_date, source, campaign_id, SUM(sessions) AS sessions,
        SUM(engaged_sessions) AS engaged_sessions
 FROM web_analytics GROUP BY event_date, source, campaign_id
)
SELECT a.event_date, a.source, a.campaign_id, a.campaign_name, a.impressions,
 a.clicks, a.spend, a.platform_conversions, a.currency,
 COALESCE(w.sessions,0) AS sessions, COALESCE(w.engaged_sessions,0) AS engaged_sessions,
 COALESCE(c.leads,0) AS leads, COALESCE(c.qualified_leads,0) AS qualified_leads,
 COALESCE(c.customers,0) AS customers, COALESCE(c.revenue,0) AS revenue,
 CASE WHEN COALESCE(c.leads,0)=0 THEN NULL ELSE a.spend/c.leads END AS cpl,
 CASE WHEN COALESCE(c.customers,0)=0 THEN NULL ELSE a.spend/c.customers END AS cpa,
 CASE WHEN a.spend=0 THEN NULL ELSE COALESCE(c.revenue,0)/a.spend END AS roas,
 CASE WHEN COALESCE(c.leads,0)=0 THEN NULL ELSE 1.0*c.qualified_leads/c.leads END AS lead_quality_rate,
 a.is_simulated
FROM ad_performance a
LEFT JOIN web w ON a.event_date=w.event_date AND a.source=w.source AND a.campaign_id=w.campaign_id
LEFT JOIN crm c ON a.event_date=c.created_date AND a.source=c.source AND a.campaign_id=c.campaign_id
ORDER BY a.event_date, a.source, a.campaign_id
"""


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows: return
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)


def export_power_bi(output_dir: Path = Path("data/exports")) -> list[Path]:
    db = Database(settings); db.initialize()
    fact = db.query(FACT_QUERY)
    campaigns = db.query("SELECT DISTINCT source,campaign_id,campaign_name FROM ad_performance ORDER BY source,campaign_id")
    dates = db.query("SELECT DISTINCT event_date AS date FROM ad_performance ORDER BY event_date")
    runs = db.query("SELECT * FROM pipeline_runs ORDER BY started_at DESC")
    anomalies = db.query("SELECT * FROM anomalies ORDER BY event_date DESC")
    raw_ads = db.query("SELECT * FROM ad_performance")
    recon = reconcile(raw_ads, fact)
    outputs = {"fact_marketing_performance.csv": fact, "dim_campaign.csv": campaigns,
               "dim_date.csv": dates, "pipeline_runs.csv": runs,
               "anomalies.csv": anomalies, "reconciliation.csv": recon}
    for name, rows in outputs.items(): write_csv(output_dir / name, rows)
    readme = output_dir / "README.txt"
    readme.write_text("SIMULATED PORTFOLIO DATA. Import all CSV files into Power BI Desktop. "
                      "See docs/POWER_BI_GUIDE.md for relationships, DAX, and pages.\n", encoding="utf-8")
    return [output_dir / name for name in outputs] + [readme]


def main() -> None:
    for path in export_power_bi(): print(path)


if __name__ == "__main__": main()

