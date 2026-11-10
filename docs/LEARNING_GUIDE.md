# Interview learning guide (after the two-day build)

The MVP can be built quickly with AI assistance; confidently explaining and modifying it requires deliberate practice. Use the generated data, not memorized answers.

## Day 1 — explain the system

- Draw the flow from simulated source → connector → validation → upsert → SQL KPI → Streamlit/Power BI.
- Explain why connector interfaces, composite keys and source/dashboard reconciliation exist.
- Give a two-minute project explanation without notes, then a five-minute version with trade-offs.
- Say clearly: “These are simulated connectors designed for later credential integration; I have not called the production vendor APIs in this project.”

Checkpoint: explain every box in `docs/ARCHITECTURE.md` and one limitation of each design choice.

## Day 2 — Python ETL and validation

- Trace one Google Ads record through extraction, validation and database upsert.
- Change the simulation seed; prove the same seed is deterministic.
- Add a validation rule (for example, clicks cannot exceed impressions) and its test.
- Explain full vs incremental loads, idempotency, retries and dead-letter/quarantine handling.

Checkpoint: modify a validator and pass the tests without copying a finished answer.

## Day 3 — SQL and KPI reasoning

- Type the daily KPI query from scratch using `JOIN`, `GROUP BY`, `CASE`, `COALESCE` and `NULLIF`.
- Change it to weekly totals and then campaign totals.
- Explain why CPL uses CRM leads, CPA uses won customers, and ROAS depends on attribution.
- Compare SQL totals with `data/exports/reconciliation.csv`.

Exercises:

```sql
-- Find campaigns spending money with no CRM leads.
-- Rank campaigns by ROAS within each source.
-- Return the latest successful pipeline run per day.
```

## Day 4 — failed pipeline diagnosis

- Run the deliberate failure in `docs/FAILURE_RUNBOOK.md`.
- Diagnose it first from logs, then compare your answer with the generated diagnostic JSON.
- Explain why valid rows load while the run becomes `success_with_warnings`.
- Practice an incident update: symptom, scope, cause, correction, prevention.

Checkpoint: recover and reconcile the same date window without deleting the database.

## Day 5 — APIs, authentication and pagination

- Explain OAuth 2.0 versus API keys and refresh/access tokens.
- Sketch a pagination loop using `next_page_token`; discuss rate limits, exponential backoff with jitter, timeouts and retryable status codes.
- Explain how each vendor payload would map to the connector's canonical fields.
- Explain webhooks versus polling, HMAC verification, replay protection and deduplication.

Suggested pseudocode:

```text
token = null
do:
  response = GET(endpoint, auth, page_token=token, timeout=30)
  if 429/5xx: retry with capped exponential backoff + jitter
  validate and yield response.records
  token = response.next_page_token
until token is null
```

## Day 6 — BI and reconciliation

- Build the four Power BI pages in `docs/POWER_BI_GUIDE.md`.
- Apply source/date filters and prove the dashboard total matches SQL for the same grain.
- Deliberately remove one fact row, refresh, and show how reconciliation catches the variance.
- Explain data freshness, semantic measures, filter context and why divide-by-zero returns blank.

Checkpoint: demo Power BI first, then use Streamlit to show engineering monitoring.

## Day 7 — security and mock interview

- Explain `.env`, ignored files, GitHub secrets, least privilege, RLS and credential rotation.
- Explain why browser code must never receive a database service-role key.
- Record a 10-minute walkthrough and remove filler or unsupported claims.
- Answer: biggest limitation, production hardening priorities, what you personally implemented, and what remains simulated.

## Honest interview summary

“I built a working local portfolio pipeline with deterministic simulated Google Ads, Meta Ads, GA4 and CRM connectors. It validates and upserts data into a PostgreSQL-compatible model, computes marketing/CRM KPIs, detects anomalies, monitors runs, reconciles BI totals and optionally asks Claude to summarize sanitized logs. I used simulated data and did not claim production API access. The connector boundary shows how authentication, pagination and vendor mapping would be added.”

