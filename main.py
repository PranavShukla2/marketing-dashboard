import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(page_title="DigitalPlus 24x7 Hub", layout="wide", initial_sidebar_state="expanded")

# --- THEME MANAGEMENT ---
# Initialize theme state if not present (Default to Light)
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    if st.session_state.theme == 'dark':
        st.session_state.theme = 'light'
    else:
        st.session_state.theme = 'dark'

# Set colors based on current theme
if st.session_state.theme == 'dark':
    bg_color = "#0e1117"
    text_color = "#ffffff"
    card_bg = "#262730"
    metric_value_color = "#ffffff"
    plotly_template = "plotly_dark"
    sidebar_bg = "#262730"
    sidebar_text = "#ffffff"
    border_color = "#444"
else:
    bg_color = "#f8f9fa"
    text_color = "#212529"
    card_bg = "#ffffff"
    metric_value_color = "#000000"
    plotly_template = "plotly_white"
    sidebar_bg = "#ffffff"
    sidebar_text = "#333333"
    border_color = "#dee2e6"

# --- CUSTOM CSS (Dynamic) ---
st.markdown(f"""
<style>
    /* Main App Background */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Sidebar Background & Text */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        border-right: 1px solid {border_color};
    }}
    
    section[data-testid="stSidebar"] .stMarkdown h1, 
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] p {{
        color: {sidebar_text} !important;
    }}
    
    /* Header Gradient */
    .brand-text {{
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E88E5, #9B51E0, #FF4081);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        line-height: 1.2;
    }}
    
    .subtitle-text {{
        font-size: 1.2rem;
        color: {text_color};
        opacity: 0.7;
        margin-bottom: 25px;
        font-weight: 500;
    }}

    /* Card Styling */
    .metric-card {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 12px;
        border: 1px solid {border_color};
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.2s;
        color: {text_color};
    }}
    
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        border-color: #1E88E5;
    }}

    /* Metric Values */
    .metric-value {{
        font-size: 2.2rem;
        font-weight: 700;
        color: {metric_value_color};
        margin: 10px 0;
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        color: {text_color};
        opacity: 0.6;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }}
    
    /* Status Pill */
    .status-pill {{
        background: {card_bg};
        border: 1px solid {border_color};
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: {text_color};
    }}
    
    /* Fix for Plotly Chart Backgrounds */
    .js-plotly-plot .plotly .main-svg {{
        background: transparent !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def generate_forecast(df, days):
    if len(df) < 2: return df
    
    df_f = df[['Date', 'Sessions']].copy()
    
    # CRITICAL FIX: Force Sessions to be numeric to prevent numpy casting error
    df_f['Sessions'] = pd.to_numeric(df_f['Sessions'], errors='coerce').fillna(0)
    
    df_f['Idx'] = (df_f['Date'] - df_f['Date'].min()).dt.days
    
    try:
        slope, intercept = np.polyfit(df_f['Idx'], df_f['Sessions'], 1)
        future_dates = [df_f['Date'].max() + timedelta(days=i) for i in range(1, days + 1)]
        future_vals = [int(slope * (df_f['Idx'].max() + i) + intercept) for i in range(1, days + 1)]
        
        df_f['Type'] = 'Historical'
        df_new = pd.DataFrame({'Date': future_dates, 'Sessions': future_vals, 'Type': 'Forecast'})
        return pd.concat([df_f, df_new], ignore_index=True)
    except Exception as e:
        st.warning(f"Forecasting error: {e}")
        return df

@st.cache_data
def load_data(use_live_google, use_live_meta):
    # Base Schema
    columns = ['Date', 'Platform', 'Campaign', 'Sessions', 'Conversions', 'Cost', 'Engagement_Rate']
    df = pd.DataFrame(columns=columns)
    
    status_msg = "OFFLINE"

    # --- GOOGLE LOGIC ---
    if use_live_google:
        try:
            import google_api
            ga = google_api.authenticate_google_analytics()
            if ga:
                df_ga = google_api.fetch_analytics_data(ga)
                if not df_ga.empty:
                    df_ga['Platform'] = 'Google Analytics'
                    df_ga['Cost'] = 0.0
                    if 'CTR' in df_ga.columns: df_ga.rename(columns={'CTR': 'Engagement_Rate'}, inplace=True)
                    else: df_ga['Engagement_Rate'] = 0.0
                    df = pd.concat([df, df_ga], ignore_index=True)
                    status_msg = "LIVE: GOOGLE"
        except: pass
    else:
        # Load Mock Google
        try:
            conn = sqlite3.connect("data/marketing.db")
            query = "SELECT * FROM campaign_metrics WHERE Platform = 'Google Analytics'"
            df_mock_ga = pd.read_sql(query, conn)
            conn.close()
            df_mock_ga.columns = [c.title() for c in df_mock_ga.columns]
            df_mock_ga['Date'] = pd.to_datetime(df_mock_ga['Date'])
            df = pd.concat([df, df_mock_ga], ignore_index=True)
            if status_msg == "OFFLINE": status_msg = "SIMULATION: GOOGLE"
        except: pass

    # --- META LOGIC (STRICT ZERO DATA) ---
    if use_live_meta:
        # We try to load real data. If no API/Script, we do NOTHING.
        # This results in 0 rows for Meta, which is what we want (No fake numbers).
        if "LIVE" in status_msg: status_msg += " + META (No Data)"
        else: status_msg = "LIVE: META (No Data)"
        
        # Future hook: if you add facebook_api.py later, call it here.
    else:
        # Load Mock Meta
        try:
            conn = sqlite3.connect("data/marketing.db")
            query = "SELECT * FROM campaign_metrics WHERE Platform IN ('Facebook Ads', 'Instagram')"
            df_mock_meta = pd.read_sql(query, conn)
            conn.close()
            df_mock_meta.columns = [c.title() for c in df_mock_meta.columns]
            df_mock_meta['Date'] = pd.to_datetime(df_mock_meta['Date'])
            df = pd.concat([df, df_mock_meta], ignore_index=True)
            if "SIMULATION" in status_msg: status_msg += " + META"
            elif status_msg == "OFFLINE": status_msg = "SIMULATION: META"
            else: status_msg += " + SIM: META"
        except: pass

    # --- TYPE ENFORCEMENT FIX ---
    # Ensure numerical columns are actually numbers to prevent Plotly errors
    numeric_cols = ['Sessions', 'Conversions', 'Cost', 'Engagement_Rate']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df, status_msg

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1055/1055666.png", width=50)
    st.markdown("### DigitalPlus 24x7")
    
    # THEME TOGGLE BUTTON
    if st.session_state.theme == 'dark':
        if st.button("☀️ Switch to Light Mode"):
            toggle_theme()
            st.rerun()
    else:
        if st.button("🌙 Switch to Dark Mode"):
            toggle_theme()
            st.rerun()
            
    st.markdown("---")
    
    st.markdown("#### Data Connections")
    use_google_live = st.toggle("Google Analytics (Live)", value=True)
    use_meta_live = st.toggle("Meta Ads (Live)", value=True)
    
    df, status_msg = load_data(use_google_live, use_meta_live)
    
    if not df.empty:
        st.markdown("---")
        st.markdown("#### Filters")
        sel_platform = st.selectbox("Platform", ["All Platforms"] + sorted(df['Platform'].unique().tolist()))
        d1, d2 = st.date_input("Date Range", [df['Date'].min(), df['Date'].max()])
        
        df_filtered = df[(df['Date'] >= pd.to_datetime(d1)) & (df['Date'] <= pd.to_datetime(d2))]
        if sel_platform != "All Platforms":
            df_filtered = df_filtered[df_filtered['Platform'] == sel_platform]
    else:
        # If both are LIVE but empty, show empty dataframe structure to avoid crash
        df_filtered = pd.DataFrame(columns=['Sessions', 'Conversions', 'Cost', 'Engagement_Rate', 'Date', 'Platform'])
        # Create a dummy row with 0s if needed for visuals, or just handle empty
        
# --- HEADER ---
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown('<div class="brand-text">DigitalPlus 24x7</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">Omni-Channel Marketing Analytics Hub</div>', unsafe_allow_html=True)

with c2:
    dot_color = "#00C853" if "LIVE" in status_msg else "#F57C00"
    st.markdown(f"""
    <div style="text-align: right; padding-top: 15px;">
        <div class="status-pill" style="border-color: {dot_color}; color: {dot_color}; background-color: {bg_color}">
            <span style="background-color: {dot_color}; width: 8px; height: 8px; border-radius: 50%; display: inline-block;"></span>
            SYSTEM STATUS: {status_msg}
        </div>
        <div style="color: {text_color}; opacity: 0.6; font-size: 0.8rem; margin-top: 5px;">Last Sync: {datetime.now().strftime('%H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)

# --- QUICK ACTION HUB ---
col1, col2, col3, col4 = st.columns(4)
with col1: st.link_button("🌐 Google Analytics", "https://analytics.google.com", use_container_width=True)
with col2: st.link_button("📘 Meta Ads Manager", "https://adsmanager.facebook.com", use_container_width=True)
with col3: st.link_button("📸 Instagram Insights", "https://business.facebook.com/latest/insights", use_container_width=True)
# Removed Mailchimp button as requested

st.markdown("###")

# --- KPI CARDS ---
if not df_filtered.empty:
    k_traffic = f"{df_filtered['Sessions'].sum():,}"
    k_conv = f"{df_filtered['Conversions'].sum():,}"
    k_spend = f"${df_filtered['Cost'].sum():,.0f}"
    k_eng = f"{df_filtered['Engagement_Rate'].mean():.1f}%"
else:
    k_traffic = "0"
    k_conv = "0"
    k_spend = "$0"
    k_eng = "0.0%"

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Traffic</div><div class="metric-value">{k_traffic}</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Conversions</div><div class="metric-value">{k_conv}</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Ad Spend</div><div class="metric-value">{k_spend}</div></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Engagement</div><div class="metric-value">{k_eng}</div></div>""", unsafe_allow_html=True)

st.markdown("---")

if not df_filtered.empty:
    # --- TABS ---
    tabs = st.tabs(["📊 Trends", "🤖 Forecast", "💰 ROI", "📂 Data"])

    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(df_filtered, values='Sessions', names='Platform', hole=0.6, title="Traffic Share", template=plotly_template)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=text_color)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.bar(df_filtered.groupby('Platform')['Engagement_Rate'].mean().reset_index(), 
                         x='Platform', y='Engagement_Rate', color='Platform', title="Engagement by Platform", template=plotly_template)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=text_color)
            st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        daily = df_filtered.groupby('Date')['Sessions'].sum().reset_index()
        # Add a check to ensure 'daily' is not empty and has valid data
        if len(daily) > 2 and daily['Sessions'].sum() > 0:
            chart_data = generate_forecast(daily, days=30)
            fig = px.line(chart_data, x='Date', y='Sessions', color='Type', line_dash='Type', title="AI Projection (30 Days)", template=plotly_template)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=text_color)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need more data points for forecasting.")

    with tabs[2]:
        if df_filtered['Cost'].sum() > 0:
            fig = px.scatter(df_filtered, x='Cost', y='Conversions', color='Platform', size='Sessions', title="Ad Spend Efficiency", template=plotly_template)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=text_color)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cost data available (Google Analytics doesn't track spend by default).")

    with tabs[3]:
        st.dataframe(df_filtered, use_container_width=True)
else:
    st.info("Waiting for live data... Toggle switches in sidebar to 'Simulation' if you want to see test data.")