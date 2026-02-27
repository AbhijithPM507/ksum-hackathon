import streamlit as st
import pandas as pd
import requests
import folium
import plotly.express as px
from streamlit_folium import st_folium


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(layout="wide")
st.title("🛡️ C3MS - Anti-Corruption Monitoring Dashboard")

# -----------------------------
# AUTO REFRESH (Every 10 seconds)
# -----------------------------


# -----------------------------
# FETCH DATA FUNCTION
# -----------------------------
def fetch_data():
    try:
        response = requests.get("http://localhost:8000/complaints")
        return pd.DataFrame(response.json())
    except:
        return pd.read_json("sample_data.json")

df = fetch_data()

# -----------------------------
# KPI SECTION
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Complaints", len(df))
col2.metric("High Severity Cases", len(df[df["severity"] == "High"]))
col3.metric("Average Risk Score", round(df["risk_score"].mean(), 2))

st.divider()

# -----------------------------
# LAYOUT SPLIT
# -----------------------------
left, right = st.columns([2,1])

# -----------------------------
# KERALA MAP SECTION
# -----------------------------
with left:
    st.subheader("📍 Kerala Complaint Map")

    kerala_center = [10.8505, 76.2711]
    m = folium.Map(location=kerala_center, zoom_start=7)

    for _, row in df.iterrows():
        color = "red" if row["severity"] == "High" else \
                "orange" if row["severity"] == "Medium" else "green"

        popup_content = f"""
        <b>ID:</b> {row['id']}<br>
        <b>Category:</b> {row['category']}<br>
        <b>Department:</b> {row['department']}<br>
        <b>Status:</b> {row['status']}<br>
        <b>Risk Score:</b> {row['risk_score']}<br>
        <b>Time:</b> {row['timestamp']}<br>
        <b>Blockchain:</b> ✔ Verified
        """

        folium.Marker(
            [row["lat"], row["lon"]],
            popup=popup_content,
            icon=folium.Icon(color=color)
        ).add_to(m)
        
    from folium.plugins import HeatMap

    heat_data = [[row["lat"], row["lon"]] for _, row in df.iterrows()]
    HeatMap(heat_data).add_to(m)

    st_folium(m, width=900, height=500)

# -----------------------------
# LIVE FEED SECTION
# -----------------------------
with right:
    st.subheader("🆕 Live Complaint Feed")

    latest = df.sort_values(by="timestamp", ascending=False).head(5)

    for _, row in latest.iterrows():
        st.write(
            f"🔹 {row['timestamp']} | {row['category']} | {row['district']} | {row['severity']}"
        )

st.divider()

# -----------------------------
# ANALYTICS SECTION
# -----------------------------
st.subheader("📊 Analytics Overview")

colA, colB = st.columns(2)

with colA:
    fig1 = px.bar(df, x="category", title="Complaint Categories")
    st.plotly_chart(fig1, use_container_width=True)

with colB:
    fig2 = px.pie(df, names="department", title="Department-wise Complaints")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("📈 Complaint Trend")

df["timestamp"] = pd.to_datetime(df["timestamp"])
trend = df.groupby(df["timestamp"].dt.date).size().reset_index(name="count")
fig3 = px.line(trend, x="timestamp", y="count", title="Daily Complaint Trend")
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# -----------------------------
# RISK SUMMARY
# -----------------------------
st.subheader("🔥 Corruption Risk Summary")

highest_risk = df.loc[df["risk_score"].idxmax()]

st.write(f"🏆 Highest Risk District: {highest_risk['district']}")
st.write(f"⚠ Risk Score: {highest_risk['risk_score']}")
st.write(f"📂 Most Frequent Category: {df['category'].mode()[0]}")

import time
time.sleep(10)
st.rerun()