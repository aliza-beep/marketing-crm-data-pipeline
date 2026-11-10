from __future__ import annotations

import argparse
import json
import uuid
from datetime import UTC, date, datetime, timedelta

from .config import Settings, settings
from .connectors import all_simulated_connectors
from .database import Database
from .logging_utils import configure_logging
from .monitoring import detect_anomalies
from .validation import validate_rows


def run_pipeline(start_date: date, end_date: date, config: Settings = settings,
                 inject_failure: str | None = None) -> dict:
    run_id = str(uuid.uuid4())
    logger = configure_logging(config.log_path, config.log_level)
    db = Database(config)
    db.initialize()
    p = db.placeholder
    started = datetime.now(UTC).isoformat()
    db.execute(f"INSERT INTO pipeline_runs(run_id,started_at,status) VALUES({p},{p},{p})",
               (run_id, started, "running"))
    extracted = loaded = rejected = 0
    ad_rows = []
    try:
        for connector in all_simulated_connectors(config.simulation_seed):
            result = connector.extract(start_date, end_date)
            if inject_failure == result.source:
                result.rows[0].pop("campaign_id", None)
            extracted += len(result.rows)
            validated = validate_rows(result.source, result.rows)
            rejected += len(validated.rejected)
            logger.info("extract_complete", extra={"run_id": run_id, "source": result.source,
                                                     "rows": len(result.rows), "stage": "extract"})
            if validated.rejected:
                logger.error("validation_rejected_rows: " + "; ".join(validated.reasons[:5]),
                             extra={"run_id": run_id, "source": result.source,
                                    "rows": len(validated.rejected), "stage": "validate",
                                    "error_type": "DataValidationError"})
            if result.source in {"google_ads", "meta_ads"}:
                loaded += db.upsert_many("ad_performance", validated.valid,
                                         ["event_date", "source", "campaign_id"])
                ad_rows.extend(validated.valid)
            elif result.source == "ga4":
                loaded += db.upsert_many("web_analytics", validated.valid,
                                         ["event_date", "source", "campaign_id"])
            else:
                loaded += db.upsert_many("crm_leads", validated.valid, ["lead_id"])

        check_status = "pass" if rejected == 0 else "warn"
        db.execute(f"INSERT INTO data_quality_results(run_id,checked_at,check_name,status,details) "
                   f"VALUES({p},{p},{p},{p},{p})",
                   (run_id, datetime.now(UTC).isoformat(), "schema_and_range_validation",
                    check_status, json.dumps({"rejected_rows": rejected})))
        anomalies = detect_anomalies(ad_rows)
        for anomaly in anomalies:
            db.execute(f"INSERT INTO anomalies(run_id,event_date,source,metric,observed_value,"
                       f"baseline_value,severity,description) VALUES({','.join([p] * 8)})",
                       (run_id, *anomaly.values()))
        status = "success_with_warnings" if rejected else "success"
        db.execute(f"UPDATE pipeline_runs SET completed_at={p},status={p},rows_extracted={p},"
                   f"rows_loaded={p} WHERE run_id={p}",
                   (datetime.now(UTC).isoformat(), status, extracted, loaded, run_id))
        logger.info("pipeline_complete", extra={"run_id": run_id, "rows": loaded, "stage": "load"})
        return {"run_id": run_id, "status": status, "extracted": extracted,
                "loaded": loaded, "rejected": rejected, "anomalies": len(anomalies)}
    except Exception as exc:
        db.execute(f"UPDATE pipeline_runs SET completed_at={p},status={p},error_message={p} "
                   f"WHERE run_id={p}",
                   (datetime.now(UTC).isoformat(), "failed", str(exc), run_id))
        logger.exception("pipeline_failed", extra={"run_id": run_id, "stage": "pipeline",
                                                    "error_type": type(exc).__name__})
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the simulated marketing ETL pipeline")
    parser.add_argument("--start", type=date.fromisoformat)
    parser.add_argument("--end", type=date.fromisoformat)
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--inject-failure", choices=["google_ads", "meta_ads", "ga4", "crm"])
    args = parser.parse_args()
    end = args.end or date.today()
    start = args.start or end - timedelta(days=args.days - 1)
    print(json.dumps(run_pipeline(start, end, inject_failure=args.inject_failure), indent=2))


if __name__ == "__main__":
    main()

