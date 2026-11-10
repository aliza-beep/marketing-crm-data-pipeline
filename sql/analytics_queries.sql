-- Interview-ready examples; PostgreSQL syntax.
-- 1) Daily funnel and KPIs. NULLIF prevents divide-by-zero.
WITH crm AS (
 SELECT created_date, source, campaign_id, COUNT(*) leads,
  COUNT(*) FILTER (WHERE lead_score >= 60) qualified_leads,
  COUNT(*) FILTER (WHERE status = 'won') customers, SUM(revenue) revenue
 FROM crm_leads GROUP BY 1,2,3
)
SELECT a.event_date, a.source, a.campaign_name, a.spend,
 COALESCE(c.leads,0) leads, COALESCE(c.customers,0) customers, COALESCE(c.revenue,0) revenue,
 a.spend / NULLIF(c.leads,0) AS cpl,
 a.spend / NULLIF(c.customers,0) AS cpa,
 COALESCE(c.revenue,0) / NULLIF(a.spend,0) AS roas,
 c.qualified_leads::numeric / NULLIF(c.leads,0) AS lead_quality_rate
FROM ad_performance a LEFT JOIN crm c USING (source,campaign_id)
 AND c.created_date=a.event_date ORDER BY a.event_date DESC;

-- 2) Dashboard reconciliation: must return zeros after a correct export.
SELECT source, SUM(spend) source_spend FROM ad_performance GROUP BY source;

-- 3) Pipeline health in the last seven days.
SELECT status, COUNT(*) runs, MAX(started_at) latest_run
FROM pipeline_runs WHERE started_at >= now() - interval '7 days' GROUP BY status;

