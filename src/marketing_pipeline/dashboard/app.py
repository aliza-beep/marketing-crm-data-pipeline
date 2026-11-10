from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / "src") not in sys.path: sys.path.insert(0, str(ROOT / "src"))

from marketing_pipeline.config import settings
from marketing_pipeline.database import Database
from marketing_pipeline.export import FACT_QUERY

st.set_page_config(page_title="ScalingCraft Marketing Pipeline", layout="wide")
st.title("Marketing + CRM Pipeline Monitor")
st.warning("PORTFOLIO DEMO — all displayed marketing and CRM records are simulated.")

db = Database(settings)
try:
    db.initialize(); rows = db.query(FACT_QUERY)
except Exception as exc:  # noqa: BLE001 - dashboard must show a friendly DB/config error
    st.error(f"Database unavailable: {type(exc).__name__}. Run the ETL first."); st.stop()
if not rows:
    st.info("No data yet. Run: python -m marketing_pipeline.pipeline --days 30"); st.stop()

df = pd.DataFrame(rows); df["event_date"] = pd.to_datetime(df["event_date"])
source = st.sidebar.multiselect("Source", sorted(df.source.unique()), default=sorted(df.source.unique()))
filtered = df[df.source.isin(source)]

spend, revenue = filtered.spend.sum(), filtered.revenue.sum()
leads, customers = int(filtered.leads.sum()), int(filtered.customers.sum())
values = [("Spend", f"${spend:,.0f}"), ("Leads", f"{leads:,}"),
          ("CPL", f"${spend/leads:,.2f}" if leads else "—"),
          ("CPA", f"${spend/customers:,.2f}" if customers else "—"),
          ("ROAS", f"{revenue/spend:.2f}x" if spend else "—"),
          ("Lead quality", f"{filtered.qualified_leads.sum()/leads:.1%}" if leads else "—")]
for row_start in (0, 3):
    cols = st.columns(3)
    for col, (label, value) in zip(cols, values[row_start:row_start + 3]):
        col.metric(label, value)

daily = filtered.groupby("event_date", as_index=False)[["spend", "revenue"]].sum()
st.plotly_chart(px.line(daily, x="event_date", y=["spend", "revenue"], markers=True,
                        title="Daily spend and attributed revenue"), width="stretch")
left, right = st.columns(2)
with left:
    by_source = filtered.groupby("source", as_index=False)[["spend", "revenue"]].sum()
    st.plotly_chart(px.bar(by_source, x="source", y=["spend", "revenue"], barmode="group",
                           title="Source performance"), width="stretch")
with right:
    quality = filtered.groupby("source", as_index=False)[["leads", "qualified_leads"]].sum()
    quality["quality_rate"] = quality.qualified_leads / quality.leads.replace(0, pd.NA)
    st.plotly_chart(px.bar(quality, x="source", y="quality_rate", title="Lead quality rate"),
                    width="stretch")

st.subheader("Reconciliation and pipeline health")
recon_path = Path("data/exports/reconciliation.csv")
if recon_path.exists(): st.dataframe(pd.read_csv(recon_path), width="stretch")
else: st.caption("Run the export command to generate the Power BI reconciliation table.")
st.dataframe(pd.DataFrame(db.query("SELECT * FROM pipeline_runs ORDER BY started_at DESC LIMIT 10")),
             width="stretch")
with st.expander("Data dictionary / definitions"):
    st.markdown("**CPL** = spend / CRM leads. **CPA** = spend / won customers. **ROAS** = attributed CRM revenue / spend. **Lead quality** = leads scoring 60+ / all leads. Attribution uses same-day source + campaign in this demo.")

