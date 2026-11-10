from marketing_pipeline.monitoring.anomalies import detect_anomalies


def test_detects_large_spike():
    rows = [{"source": "google_ads", "event_date": f"2026-01-{i:02}", "spend": 10}
            for i in range(1, 10)]
    rows.append({"source": "google_ads", "event_date": "2026-01-10", "spend": 1000})
    result = detect_anomalies(rows, threshold=2)
    assert len(result) == 1
    assert result[0]["event_date"] == "2026-01-10"

