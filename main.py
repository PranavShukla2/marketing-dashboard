import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import numpy as np
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(page_title="DigitalPlus 24x7 Hub", layout="wide", initial_sidebar_state="expanded")

# --- THEME VARIABLES (Dark/Light Mode) ---
# We check this early so we can apply the CSS immediately
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)

if dark_mode:
    bg_color, card_bg, text_color, border_color = "#0e1117", "#262730", "#fafafa", "#444"
    metric_val_color = "#ffffff"
    plotly_template = "plotly_dark"
else:
    bg_color, card_bg, text_color, border_color = "#f8f9fa", "#ffffff", "#212529", "#dee2e6"
    metric_val_color = "#000000"
    plotly_template = "plotly_white"

# --- CUSTOM CSS ---
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .brand-text {{
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00C853, #1E88E5, #9B51E0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        filter: drop-shadow(0px 0px 5px rgba(30, 136, 229, 0.3));
    }}
    .metric-card {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 12px;
        border: 1px solid {border_color};
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        transition: transform 0.2s;
        color: {text_color};
    }}
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(30, 136, 229, 0.1);
        border-color: #1E88E5;
    }}
    .metric-value {{ font-size: 2rem; font-weight: 700; color: {metric_val_color}; }}
    .metric-label {{ font-size: 0.9rem; color: #888; text-transform: uppercase; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def generate_forecast(df, days):
    """Linear regression forecasting for time-series data."""
    if df.empty or len(df) < 2: return df
    df_f = df.copy()
    df_f['Idx'] = (df_f['Date'] - df_f['Date'].min()).dt.days
    try:
        slope, intercept = np.polyfit(df_f['Idx'], df_f['Sessions'], 1)
        future_dates = [df_f['Date'].max() + timedelta(days=i) for i in range(1, days + 1)]
        # Ensure we don't predict negative traffic
        future_vals = [max(0, int(slope * (df_f['Idx'].max() + i) + intercept)) for i in range(1, days + 1)]
        
        df_f['Type'] = 'Historical'
        df_new = pd.DataFrame({'Date': future_dates, 'Sessions': future_vals, 'Type': 'Forecast'})
        return pd.concat([df_f, df_new], ignore_index=True)
    except:
        return df

def load_google_properties():
    status_msg = ""
    try:
        import google_api
        if not os.path.exists("client_secrets.json") and "gcp_service_account" not in st.secrets:
            return {}, None, "❌ Keys missing."
        creds = google_api.authenticate_google_analytics()
        if not creds: return {}, None, "❌ Auth Failed."
        properties = google_api.get_ga4_properties(creds)
        if not properties: return {}, creds, "⚠️ 0 properties found."
        return properties, creds, None
    except Exception as e: return {}, None, f"❌ Error: {str(e)}"

def load_google_deep_dive(creds, property_id):
    try:
        import google_api
        df_s = google_api.fetch_traffic_sources(creds, property_id)
        df_c = google_api.fetch_campaign_details(creds, property_id)
        df_t = google_api.fetch_time_series_data(creds, property_id)
        return df_s, df_c, df_t
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1055/1055666.png", width=50)
    st.markdown("### DigitalPlus 24x7")
    
    st.markdown("#### 🌍 Property Selector")
    properties, creds, error = load_google_properties()
    
    selected_prop_id = None
    if properties:
        selected_prop_name = st.selectbox("Select Website", list(properties.keys()))
        selected_prop_id = properties[selected_prop_name]
    else:
        if error: st.error(error)
        else: st.warning("Connecting...")

    st.markdown("---")
    use_google_live = st.toggle("Google Analytics (Live)", value=True)
    use_meta_live = st.toggle("Meta Ads (Live)", value=True)

# --- HEADER ---
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown('<div class="brand-text">DigitalPlus 24x7</div>', unsafe_allow_html=True)
    if selected_prop_id: st.caption(f"Analyzing Property ID: **{selected_prop_id}**")
    else: st.caption("Omni-Channel Marketing Analytics Hub")

with c2:
    status_text = "LIVE: GOOGLE" if (use_google_live and selected_prop_id) else "SIMULATION MODE"
    dot_color = "#00C853" if "LIVE" in status_text else "#F57C00"
    st.markdown(f"""
    <div style="text-align: right; padding-top: 15px;">
        <span style="color: {dot_color}; font-weight: bold;">● {status_text}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("###")

# --- DATA FETCHING ---
df_sources = pd.DataFrame()
df_campaigns = pd.DataFrame()
df_time = pd.DataFrame()

if use_google_live and creds and selected_prop_id:
    df_sources, df_campaigns, df_time = load_google_deep_dive(creds, selected_prop_id)

# --- KPI CALCULATIONS ---
total_traffic = df_sources['Sessions'].sum() if not df_sources.empty else 0
total_conversions = df_campaigns['Conversions'].sum() if not df_campaigns.empty else 0
avg_eng = (df_campaigns['Engagement Rate'].mean() * 100) if not df_campaigns.empty else 0.0

# --- KPI CARDS ---
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Traffic</div><div class="metric-value">{total_traffic:,}</div></div>""", unsafe_allow_html=True)
with k2: st.markdown(f"""<div class="metric-card"><div class="metric-label">Conversions</div><div class="metric-value">{total_conversions:,}</div></div>""", unsafe_allow_html=True)
with k3: st.markdown(f"""<div class="metric-card"><div class="metric-label">Properties</div><div class="metric-value">{len(properties)}</div></div>""", unsafe_allow_html=True)
with k4: st.markdown(f"""<div class="metric-card"><div class="metric-label">Avg. Engagement</div><div class="metric-value">{avg_eng:.1f}%</div></div>""", unsafe_allow_html=True)

st.markdown("---")

# --- TABS ---
# Added the Forecasting tab back!
tabs = st.tabs(["📊 AI Forecast", "🏆 Top 3 Sources", "🎯 Post-Level Tracking", "📈 Overview"])

with tabs[0]:
    st.subheader("🤖 Traffic Prediction Model")
    st.markdown("Using linear regression to forecast traffic trends for the next 30 days based on historical property data.")
    
    if not df_time.empty and len(df_time) > 2:
        forecast_data = generate_forecast(df_time, days=30)
        fig = px.line(forecast_data, x='Date', y='Sessions', color='Type', line_dash='Type', 
                      title="AI Projection (30 Days)", template=plotly_template, 
                      color_discrete_map={"Historical": "#1E88E5", "Forecast": "#00C853"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient daily data in Google Analytics to generate a reliable AI forecast. Need at least 3 days of historical traffic.")

with tabs[1]:
    if not df_sources.empty:
        top_src = df_sources.groupby("Source")['Sessions'].sum().reset_index().sort_values(by="Sessions", ascending=False).head(3)
        c1, c2, c3 = st.columns(3)
        colors = ["#FF4B4B", "#1E88E5", "#00C853"]
        for i, (index, row) in enumerate(top_src.iterrows()):
            if i < 3:
                with [c1, c2, c3][i]:
                    st.markdown(f"""<div class="metric-card" style="border-top: 5px solid {colors[i]};"><div style="font-size: 1.5rem;">#{i+1}</div><div style="font-weight:bold;">{row['Source']}</div><div>{row['Sessions']} Sessions</div></div>""", unsafe_allow_html=True)
        st.dataframe(df_sources, use_container_width=True)
    else:
        st.info("No Traffic Source data available.")

with tabs[2]:
    if not df_campaigns.empty:
        st.markdown("**Detailed Ad Content / Post Performance:**")
        st.dataframe(df_campaigns, use_container_width=True)
    else:
        st.info("No Campaign/Post data available. Ensure UTM tags are used.")

with tabs[3]:
    if not df_sources.empty:
        fig = px.pie(df_sources, values='Sessions', names='Source', title="Traffic Share", template=plotly_template)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for charts.")