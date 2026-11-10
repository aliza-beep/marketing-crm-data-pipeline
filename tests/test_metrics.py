from marketing_pipeline.metrics import calculate_kpis, reconcile, safe_divide


def test_safe_divide_handles_zero():
    assert safe_divide(10, 0) is None
    assert safe_divide(10, 4) == 2.5


def test_kpis_use_crm_outcomes():
    result = calculate_kpis(spend=1000, leads=20, customers=4, revenue=5000, qualified_leads=12)
    assert result == {"cpl": 50.0, "cpa": 250.0, "roas": 5.0, "lead_quality_rate": 0.6}


def test_reconciliation_finds_variance():
    source = [{"source": "google_ads", "spend": 100, "clicks": 10}]
    dashboard = [{"source": "google_ads", "spend": 90, "clicks": 9}]
    result = reconcile(source, dashboard)[0]
    assert result["spend_variance"] == 10
    assert result["click_variance"] == 1

