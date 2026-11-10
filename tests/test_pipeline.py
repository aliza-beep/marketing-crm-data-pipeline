from datetime import date

from marketing_pipeline.config import Settings
from marketing_pipeline.database import Database
from marketing_pipeline.pipeline import run_pipeline


def test_pipeline_is_idempotent(tmp_path):
    config = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}",
                      log_path=tmp_path / "pipeline.jsonl")
    first = run_pipeline(date(2026, 1, 1), date(2026, 1, 3), config)
    second = run_pipeline(date(2026, 1, 1), date(2026, 1, 3), config)
    db = Database(config)
    count = db.query("SELECT COUNT(*) AS n FROM ad_performance")[0]["n"]
    assert first["status"] == second["status"] == "success"
    assert count == 12


def test_injected_bad_row_creates_warning(tmp_path):
    config = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}",
                      log_path=tmp_path / "pipeline.jsonl")
    result = run_pipeline(date(2026, 1, 1), date(2026, 1, 1), config, "crm")
    assert result["status"] == "success_with_warnings"
    assert result["rejected"] == 1

