import os

import altair as alt
import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="London Tube vs Weather", layout="wide")


@st.cache_data(ttl=300)
def query(sql: str) -> pd.DataFrame:
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB"),
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [c[0] for c in cur.description]
            return pd.DataFrame(cur.fetchall(), columns=cols)
    finally:
        conn.close()


st.title("Does weather affect London Tube disruption?")
st.caption("Hourly TfL line status joined to Open-Meteo weather. Built with Airflow and dbt.")

coverage = query("""
    select count(*) as line_hours,
           count(distinct snapshot_hour) as hours_observed,
           min(snapshot_hour) as first_snapshot,
           max(snapshot_hour) as last_snapshot
    from analytics.fct_line_status_hourly
""").iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("Line-hours observed", int(coverage["line_hours"]))
c2.metric("Hourly snapshots", int(coverage["hours_observed"]))
c3.metric("Latest snapshot (UTC)", str(coverage["last_snapshot"])[:16])

if coverage["hours_observed"] < 48:
    st.info("Early data: fewer than 48 hourly snapshots so far. "
            "Disruption rates will become more reliable as the pipeline keeps running.")

st.subheader("Disruption rate by weather condition")
by_weather = query("select * from analytics.mart_disruption_by_weather")
by_weather["disruption_rate_pct"] = by_weather["disruption_rate_pct"].astype(float)
if by_weather.empty:
    st.warning("No joined weather data yet.")
else:
    if len(by_weather) >= 2:
        st.bar_chart(by_weather.set_index("weather_category")["disruption_rate_pct"])
    else:
        st.info("Only one weather condition observed so far, so there is nothing to compare yet.")
    st.dataframe(by_weather, hide_index=True)

st.subheader("Disruption rate by line")
by_line = query("""
    select l.line_name,
           count(*) as hours_observed,
           round(100.0 * count(*) filter (where f.is_disrupted) / count(*), 2)
               as disruption_rate_pct
    from analytics.fct_line_status_hourly f
    join analytics.dim_line l using (line_id)
    group by l.line_name
    order by disruption_rate_pct desc
""")
by_line["disruption_rate_pct"] = by_line["disruption_rate_pct"].astype(float)
chart = (
    alt.Chart(by_line)
    .mark_bar()
    .encode(
        x=alt.X("line_name:N", sort="-y", title=None),
        y=alt.Y(
            "disruption_rate_pct:Q",
            scale=alt.Scale(domain=[0, 100]),
            title="Disruption rate (%)",
        ),
    )
)
st.altair_chart(chart, use_container_width=True)

st.subheader("Rain vs dry")
rain = query("""
    select case when is_raining then 'Raining' else 'Dry' end as condition,
           count(*) as line_hours,
           round(100.0 * count(*) filter (where is_disrupted) / count(*), 2)
               as disruption_rate_pct
    from analytics.fct_line_status_hourly
    where is_raining is not null
    group by 1
""")
rain["disruption_rate_pct"] = rain["disruption_rate_pct"].astype(float)
st.dataframe(rain, hide_index=True)
