from __future__ import annotations

import hashlib
import random
from datetime import date, timedelta

from .base import Connector, ExtractResult

CAMPAIGNS = {
    "google_ads": [("g-search-brand", "Search | Brand"), ("g-search-data", "Search | Data Services")],
    "meta_ads": [("m-leadgen", "Lead Gen | DE Teams"), ("m-retarget", "Retargeting | Site")],
}


def _stable_seed(seed: int, *parts: object) -> int:
    digest = hashlib.sha256("|".join(map(str, (seed, *parts))).encode()).hexdigest()
    return int(digest[:12], 16)


def _days(start: date, end: date):
    for offset in range((end - start).days + 1):
        yield start + timedelta(days=offset)


class SimulatedAdConnector(Connector):
    def __init__(self, source: str, seed: int = 42):
        if source not in CAMPAIGNS:
            raise ValueError(f"Unsupported simulated ad source: {source}")
        self.source, self.seed = source, seed

    def extract(self, start_date: date, end_date: date) -> ExtractResult:
        rows = []
        for day in _days(start_date, end_date):
            for campaign_id, campaign_name in CAMPAIGNS[self.source]:
                rng = random.Random(_stable_seed(self.seed, self.source, day, campaign_id))
                impressions = rng.randint(1400, 8500)
                clicks = max(1, int(impressions * rng.uniform(0.018, 0.065)))
                spend = round(clicks * rng.uniform(1.4, 5.8), 2)
                conversions = max(0, int(clicks * rng.uniform(0.025, 0.11)))
                rows.append({
                    "event_date": day.isoformat(), "source": self.source,
                    "campaign_id": campaign_id, "campaign_name": campaign_name,
                    "impressions": impressions, "clicks": clicks, "spend": spend,
                    "platform_conversions": conversions, "currency": "USD",
                    "is_simulated": True,
                })
        return ExtractResult(self.source, rows)


class SimulatedGA4Connector(Connector):
    source = "ga4"

    def __init__(self, seed: int = 42): self.seed = seed

    def extract(self, start_date: date, end_date: date) -> ExtractResult:
        rows = []
        mappings = [("google_ads", "g-search-brand"), ("google_ads", "g-search-data"),
                    ("meta_ads", "m-leadgen"), ("meta_ads", "m-retarget")]
        for day in _days(start_date, end_date):
            for source, campaign_id in mappings:
                rng = random.Random(_stable_seed(self.seed, self.source, day, campaign_id))
                sessions = rng.randint(35, 320)
                rows.append({"event_date": day.isoformat(), "source": source,
                             "campaign_id": campaign_id, "sessions": sessions,
                             "engaged_sessions": int(sessions * rng.uniform(.48, .82)),
                             "is_simulated": True})
        return ExtractResult(self.source, rows)


class SimulatedCRMConnector(Connector):
    source = "crm"

    def __init__(self, seed: int = 42): self.seed = seed

    def extract(self, start_date: date, end_date: date) -> ExtractResult:
        rows = []
        mappings = [("google_ads", "g-search-brand"), ("google_ads", "g-search-data"),
                    ("meta_ads", "m-leadgen"), ("meta_ads", "m-retarget"),
                    ("organic", "unattributed")]
        counter = 0
        for day in _days(start_date, end_date):
            for source, campaign_id in mappings:
                rng = random.Random(_stable_seed(self.seed, self.source, day, campaign_id))
                for _ in range(rng.randint(1, 8)):
                    counter += 1
                    score = rng.randint(18, 100)
                    status = "won" if score >= 82 and rng.random() > .35 else (
                        "qualified" if score >= 60 else "new")
                    revenue = round(rng.uniform(1800, 12000), 2) if status == "won" else 0.0
                    rows.append({"lead_id": f"SIM-{day:%Y%m%d}-{counter:04d}",
                                 "created_date": day.isoformat(), "source": source,
                                 "campaign_id": campaign_id, "lead_score": score,
                                 "status": status, "revenue": revenue, "is_simulated": True})
        return ExtractResult(self.source, rows)


def all_simulated_connectors(seed: int = 42) -> list[Connector]:
    return [SimulatedAdConnector("google_ads", seed), SimulatedAdConnector("meta_ads", seed),
            SimulatedGA4Connector(seed), SimulatedCRMConnector(seed)]

