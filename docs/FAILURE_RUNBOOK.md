# Failure runbook

## Deliberate practice failure

Run:

```powershell
python -m marketing_pipeline.pipeline --days 3 --inject-failure crm
python -m marketing_pipeline.ai.diagnostics --no-ai
```

The pipeline removes `campaign_id` from one simulated CRM row. Validation rejects only that row, loads the valid records, marks the run `success_with_warnings`, writes structured evidence, and produces a diagnostic summary.

## Triage sequence

1. Identify run ID, first failing stage, source and error type.
2. Check whether failure is transport/authentication, schema, data quality, database, or dashboard freshness.
3. Confirm the source window and row counts; do not immediately rerun a non-idempotent load.
4. Quarantine invalid records and preserve evidence.
5. Correct mapping/credential/upstream issue, then rerun the same date window.
6. Reconcile source, warehouse and dashboard totals.
7. Document cause, impact, correction and prevention.

## Example evidence

See `docs/sample_failure_log.jsonl`. It is synthetic and contains no credentials or personal data.

