# Power BI recognised BI deliverable

This repository produces a real Power BI-compatible star-schema dataset in `data/exports/`. It does **not** include a `.pbix`, because Power BI Desktop is not installed in the build environment. The CSVs, model, DAX and page specification below are the reproducible BI output.

## Build in Power BI Desktop

1. Run `python -m marketing_pipeline.export`.
2. Get Data → Text/CSV and load every CSV in `data/exports/`.
3. Set `dim_date[date]` and `fact_marketing_performance[event_date]` to Date.
4. Create relationships:
   - `dim_date[date]` 1 → * `fact_marketing_performance[event_date]`
   - `dim_campaign[campaign_id]` 1 → * `fact_marketing_performance[campaign_id]`
5. Mark `dim_date` as the date table. Hide foreign keys from report view.
6. Add a visible red banner: **SIMULATED PORTFOLIO DATA — NOT LIVE PLATFORM DATA**.

## Measures (DAX)

```DAX
Total Spend = SUM(fact_marketing_performance[spend])
Total Leads = SUM(fact_marketing_performance[leads])
Qualified Leads = SUM(fact_marketing_performance[qualified_leads])
Customers = SUM(fact_marketing_performance[customers])
Revenue = SUM(fact_marketing_performance[revenue])
CPL = DIVIDE([Total Spend], [Total Leads])
CPA = DIVIDE([Total Spend], [Customers])
ROAS = DIVIDE([Revenue], [Total Spend])
Lead Quality Rate = DIVIDE([Qualified Leads], [Total Leads])
Spend Variance = SUM(reconciliation[source_spend]) - SUM(reconciliation[dashboard_spend])
```

## Report pages

1. **Executive performance:** KPI cards for spend, leads, CPL, CPA, ROAS and lead quality; date/source slicers; spend vs revenue trend; campaign matrix.
2. **Funnel and lead quality:** sessions → leads → qualified → won; lead-quality bar by source; CPL/CPA scatter.
3. **Pipeline health:** latest run status, rows loaded, anomalies by severity, failed run table.
4. **Reconciliation:** source and dashboard totals side-by-side; variance cards conditionally red when non-zero.

## Acceptance checks

- Spend and click variances are zero after a complete export.
- All fact records show `is_simulated = TRUE`.
- Totals match `sql/analytics_queries.sql` for the same filters.
- Empty denominators display blank, never infinity or an invented zero.

