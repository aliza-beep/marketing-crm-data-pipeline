# Moving from simulation to authenticated APIs

Do not enable these changes until the account owner authorizes access and provides credentials through a secret manager.

| Source | Typical auth | Pagination/checkpoint | Canonical mapping |
|---|---|---|---|
| Google Ads | OAuth refresh token + developer token | date segments / page token | cost micros → spend; campaign resource name → ID |
| Meta Ads | long-lived system-user token | `paging.next` cursor | spend, impressions, clicks, actions |
| GA4 Data API | OAuth/service account | offset/limit or date partitions | sessions and engagedSessions by source/campaign |
| CRM | OAuth/API token | cursor + updated-since watermark | lead ID, source/campaign, score, stage, revenue |

Implementation sequence:

1. Implement the existing `Connector.extract(start_date, end_date)` contract in a new module.
2. Read secrets only from environment variables or a managed secret store.
3. Set connect/read timeouts; retry only safe transient failures with capped exponential backoff and jitter.
4. Persist a per-source high-water mark and vendor request ID.
5. Normalize vendor types and currencies; retain a raw response landing zone for audit.
6. Add contract tests with recorded, redacted fixtures; never use live tokens in CI.
7. Validate totals in the vendor UI against the warehouse and Power BI using the same date, timezone and attribution settings.

