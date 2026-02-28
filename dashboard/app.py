import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(layout="wide")
st.title("🛡 C3MS - Anti-Corruption Monitoring Dashboard")

# -----------------------------
# FETCH DATA
# -----------------------------
@st.cache_data(ttl=10)
def fetch_data():
    try:
        response = requests.get("http://localhost:8000/complaints")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            return pd.DataFrame()
    except:
        return pd.DataFrame()

df = fetch_data()

if df.empty:
    st.warning("No complaints found.")
    st.stop()

# -----------------------------
# PREPROCESSING
# -----------------------------
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# -----------------------------
# KPI SECTION
# -----------------------------
col1, col2, col3 = st.columns(3)

total_cases = len(df)
high_cases = len(df[df["risk_level"] == "High"])
avg_score = round(df["severity_score"].mean(), 2)

col1.metric("Total Complaints", total_cases)
col2.metric("High Risk Cases", high_cases)
col3.metric("Average Severity Score", avg_score)

st.divider()

# -----------------------------
# LIVE FEED + DETAILS
# -----------------------------
left, right = st.columns([2,1])

with left:
    st.subheader("📋 Recent Complaints")

    latest = df.sort_values(by="timestamp", ascending=False).head(10)

    for _, row in latest.iterrows():
        st.markdown(f"""
        **ID:** {row['id']}  
        **Official:** {row['official_name']}  
        **Position:** {row['position']}  
        **Place:** {row['place']}  
        **Category:** {row['category']}  
        **Risk:** {row['risk_level']}  
        **Status:** {row['status']}  
        **Timestamp:** {row['timestamp']}
        ---
        """)

with right:
    st.subheader("⚠ Escalation Summary")

    escalated = df[df["escalation_required"] == True]

    st.metric("Escalated Cases", len(escalated))

    if not escalated.empty:
        latest_escalated = escalated.sort_values(by="timestamp", ascending=False).head(5)
        for _, row in latest_escalated.iterrows():
            st.write(f"🚨 {row['official_name']} - {row['place']}")

st.divider()

# -----------------------------
# ANALYTICS
# -----------------------------
st.subheader("📊 Analytics Overview")

colA, colB = st.columns(2)

with colA:
    fig1 = px.bar(
        df,
        x="category",
        title="Complaint Categories",
    )
    st.plotly_chart(fig1, use_container_width=True)

with colB:
    fig2 = px.pie(
        df,
        names="position",
        title="Position-wise Complaints",
    )
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# TREND ANALYSIS
# -----------------------------
st.subheader("📈 Daily Complaint Trend")

trend = df.groupby(df["timestamp"].dt.date).size().reset_index(name="count")

fig3 = px.line(
    trend,
    x="timestamp",
    y="count",
    title="Complaints Per Day"
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# -----------------------------
# RISK SUMMARY
# -----------------------------
st.subheader("🔥 Corruption Risk Summary")

highest_risk = df.loc[df["severity_score"].idxmax()]

st.write(f"🏆 Highest Severity Official: {highest_risk['official_name']}")
st.write(f"📍 Location: {highest_risk['place']}")
st.write(f"⚠ Severity Score: {highest_risk['severity_score']}")
st.write(f"📂 Most Frequent Category: {df['category'].mode()[0]}")

# -----------------------------
# AUTO REFRESH
# -----------------------------
time.sleep(10)
st.rerun()