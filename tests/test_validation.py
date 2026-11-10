from marketing_pipeline.validation import validate_rows


def test_rejects_missing_campaign():
    result = validate_rows("google_ads", [{"event_date": "2026-01-01", "source": "google_ads",
                                            "spend": 1, "clicks": 1, "impressions": 10}])
    assert not result.valid
    assert "campaign_id" in result.reasons[0]


def test_rejects_bad_lead_score():
    row = {"lead_id": "1", "created_date": "2026-01-01", "source": "crm",
           "campaign_id": "x", "lead_score": 101, "status": "new", "revenue": 0}
    assert len(validate_rows("crm", [row]).rejected) == 1

