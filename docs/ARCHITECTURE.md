# Architecture

All four source systems in this MVP are **simulators**, not live APIs. Each implements the same connector interface a real authenticated, paginated connector would use.

```mermaid
flowchart LR
  subgraph Sources[Simulated source systems]
    G[Google Ads]
    M[Meta Ads]
    A[GA4]
    C[CRM]
  end
  W[Signed CRM webhook] --> V
  G & M & A & C --> E[Python connector interface]
  E --> V[Schema/range validation]
  V -->|valid| L[Idempotent upsert]
  V -->|rejected| Q[JSON failure log]
  L --> P[(SQLite local / Supabase PostgreSQL)]
  P --> K[SQL KPI + reconciliation layer]
  K --> S[Streamlit engineering demo]
  K --> B[Power BI star-schema CSV output]
  P --> D[Anomaly + pipeline monitoring]
  Q & D --> AI[Deterministic diagnostic agent]
  AI -. optional key .-> CL[Claude enhancement]
  GH[GitHub Actions schedule] --> E
```

## Design decisions

- Connector boundary isolates vendor authentication, pagination, rate limiting, and schema mapping.
- Natural composite keys make daily loads idempotent.
- Raw-ish normalized tables keep platform and CRM measures auditable before KPI calculation.
- Attribution is intentionally simple: same date + source + campaign. Production needs an agreed attribution window and identity strategy.
- The local SQLite path makes the demo free. PostgreSQL DDL is included for Supabase.
- The diagnostic path never depends on an LLM: a structured fallback always works.

