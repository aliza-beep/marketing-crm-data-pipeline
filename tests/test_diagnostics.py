import json

from marketing_pipeline.ai.diagnostics import diagnose


def test_diagnostic_fallback_finds_validation_error(tmp_path):
    log = tmp_path / "pipeline.jsonl"
    events = [
        {"level": "INFO", "source": "google_ads", "message": "extract_complete"},
        {"level": "ERROR", "source": "crm", "message": "missing lead_id",
         "error_type": "DataValidationError"},
    ]
    log.write_text("\n".join(json.dumps(e) for e in events), encoding="utf-8")
    report = diagnose(log, use_ai=False)
    assert report["status"] == "critical"
    assert report["mode"] == "deterministic_fallback"
    assert report["findings"][0]["category"] == "DataValidationError"

