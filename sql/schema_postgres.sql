-- Supabase/PostgreSQL schema. All demo records are explicitly marked is_simulated.
CREATE TABLE IF NOT EXISTS pipeline_runs (
 run_id uuid PRIMARY KEY, started_at timestamptz NOT NULL, completed_at timestamptz,
 status text NOT NULL, rows_extracted integer DEFAULT 0, rows_loaded integer DEFAULT 0,
 error_message text
);
CREATE TABLE IF NOT EXISTS ad_performance (
 event_date date NOT NULL, source text NOT NULL, campaign_id text NOT NULL,
 campaign_name text NOT NULL, impressions integer NOT NULL CHECK(impressions>=0),
 clicks integer NOT NULL CHECK(clicks>=0), spend numeric(14,2) NOT NULL CHECK(spend>=0),
 platform_conversions integer NOT NULL CHECK(platform_conversions>=0), currency char(3) NOT NULL,
 is_simulated boolean NOT NULL DEFAULT true, loaded_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(event_date,source,campaign_id)
);
CREATE TABLE IF NOT EXISTS web_analytics (
 event_date date NOT NULL, source text NOT NULL, campaign_id text NOT NULL,
 sessions integer NOT NULL CHECK(sessions>=0), engaged_sessions integer NOT NULL CHECK(engaged_sessions>=0),
 is_simulated boolean NOT NULL DEFAULT true, loaded_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(event_date,source,campaign_id)
);
CREATE TABLE IF NOT EXISTS crm_leads (
 lead_id text PRIMARY KEY, created_date date NOT NULL, source text NOT NULL, campaign_id text NOT NULL,
 lead_score integer NOT NULL CHECK(lead_score BETWEEN 0 AND 100), status text NOT NULL,
 revenue numeric(14,2) NOT NULL CHECK(revenue>=0), is_simulated boolean NOT NULL DEFAULT true,
 loaded_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS webhook_events (
 event_id uuid PRIMARY KEY, received_at timestamptz NOT NULL DEFAULT now(), event_type text NOT NULL,
 payload_json jsonb NOT NULL, processed boolean NOT NULL DEFAULT false
);
CREATE TABLE IF NOT EXISTS data_quality_results (
 id bigserial PRIMARY KEY, run_id uuid NOT NULL REFERENCES pipeline_runs(run_id),
 checked_at timestamptz NOT NULL, check_name text NOT NULL, status text NOT NULL, details jsonb NOT NULL
);
CREATE TABLE IF NOT EXISTS anomalies (
 id bigserial PRIMARY KEY, run_id uuid NOT NULL REFERENCES pipeline_runs(run_id), event_date date NOT NULL,
 source text NOT NULL, metric text NOT NULL, observed_value numeric NOT NULL,
 baseline_value numeric NOT NULL, severity text NOT NULL, description text NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ads_date ON ad_performance(event_date);
CREATE INDEX IF NOT EXISTS idx_crm_attribution ON crm_leads(created_date,source,campaign_id);

-- For a private backend connection only. If exposing through Supabase Data API, enable RLS
-- and define least-privilege policies before granting authenticated/anon access.

