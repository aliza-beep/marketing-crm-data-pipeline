from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationResult:
    valid: list[dict[str, Any]]
    rejected: list[dict[str, Any]]
    reasons: list[str]


REQUIRED = {
    "google_ads": {"event_date", "source", "campaign_id", "spend", "clicks", "impressions"},
    "meta_ads": {"event_date", "source", "campaign_id", "spend", "clicks", "impressions"},
    "ga4": {"event_date", "source", "campaign_id", "sessions", "engaged_sessions"},
    "crm": {"lead_id", "created_date", "source", "campaign_id", "lead_score", "status", "revenue"},
}


def validate_rows(source: str, rows: list[dict[str, Any]]) -> ValidationResult:
    valid, rejected, reasons = [], [], []
    for index, row in enumerate(rows):
        missing = sorted(REQUIRED[source] - row.keys())
        numeric_negative = any(row.get(k, 0) < 0 for k in
                               ("spend", "clicks", "impressions", "sessions", "revenue"))
        score_invalid = source == "crm" and not 0 <= row.get("lead_score", -1) <= 100
        reason = None
        if missing: reason = f"row {index}: missing {','.join(missing)}"
        elif numeric_negative: reason = f"row {index}: negative metric"
        elif score_invalid: reason = f"row {index}: lead_score outside 0..100"
        if reason:
            rejected.append(row); reasons.append(reason)
        else:
            valid.append(row)
    return ValidationResult(valid, rejected, reasons)

