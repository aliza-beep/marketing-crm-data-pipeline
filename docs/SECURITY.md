# Security and credentials

- Copy `.env.example` to `.env`; `.env` is ignored by Git.
- Never put service keys, database passwords, access tokens, or webhook secrets in code, screenshots, logs, commits, or Streamlit public secrets.
- Prefer Supabase's transaction pooler connection string with SSL. Use a dedicated least-privilege database role in production.
- The backend uses parameterized values. Table names in the bulk loader are allow-listed.
- Webhooks use an HMAC-SHA256 signature and constant-time comparison. Production should also add replay protection, timestamp tolerance, rate limiting and event-id deduplication.
- Supabase Data API: enable Row Level Security before exposing tables. Do not expose the service-role key to a browser.
- GitHub Actions: store secrets in repository/environment secrets, restrict workflow permissions, pin dependencies and rotate compromised credentials.
- The optional Claude request includes recent logs; production logs must be scrubbed of PII and secrets first. This demo generates no personal data.
- If a secret is committed: revoke/rotate it first, then remove it from Git history. Deleting the visible line alone is insufficient.

