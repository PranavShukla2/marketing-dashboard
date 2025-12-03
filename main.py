import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(page_title="DigitalPlus 24x7 Hub", layout="wide", initial_sidebar_state="expanded")

# --- THEME MANAGEMENT ---
# Initialize theme state if not present
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

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
else:
    bg_color = "#ffffff"
    text_color = "#000000"
    card_bg = "#f0f2f6"
    metric_value_color = "#000000"
    plotly_template = "plotly_white"
    sidebar_bg = "#f0f2f6"

# --- CUSTOM CSS (Dynamic) ---
st.markdown(f"""
<style>
    /* Main App Background */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Sidebar Background (Targeting Streamlit classes) */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
    }}
    
    /* Metric Cards */
    .metric-card {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: {text_color};
    }}
    
    /* Metric Text Colors */
    [data-testid="stMetricValue"] {{
        color: {metric_value_color} !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: #888888 !important;
    }}
    
    /* Live Pulsing Dot Animation */
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(0, 200, 83, 0.7); }}
        70% {{ box-shadow: 0 0 0 10px rgba(0, 200, 83, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(0, 200, 83, 0); }}
    }}
    
    .live-indicator {{
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: #00C853;
        border-radius: 50%;
        animation: pulse 2s infinite;
        margin-right: 8px;
        vertical-align: middle;
    }}
    
    .status-text {{
        font-family: monospace;
        color: #00C853;
        font-weight: bold;
        vertical-align: middle;
    }}
    
    /* Headers */
    .big-title {{
        font-size: 3.5rem !important;
        font-weight: 800;
        background: linear-gradient(90deg, #4285F4, #34A853, #FBBC05, #EA4335);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    /* Fix for Plotly Chart Backgrounds */
    .js-plotly-plot .plotly .main-svg {{
        background: transparent !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- HELPER: FORECASTING ---
def generate_forecast(df, days):
    if len(df) < 2: return df
    df_f = df[['Date', 'Sessions']].copy()
    df_f['Idx'] = (df_f['Date'] - df_f['Date'].min()).dt.days
    
    slope, intercept = np.polyfit(df_f['Idx'], df_f['Sessions'], 1)
    
    future_dates = [df_f['Date'].max() + timedelta(days=i) for i in range(1, days + 1)]
    future_vals = [int(slope * (df_f['Idx'].max() + i) + intercept) for i in range(1, days + 1)]
    
    df_f['Type'] = 'Historical'
    df_new = pd.DataFrame({'Date': future_dates, 'Sessions': future_vals, 'Type': 'Forecast'})
    return pd.concat([df_f, df_new], ignore_index=True)

# --- DATA LOADER ---
@st.cache_data
def load_data(use_live_google):
    try:
        conn = sqlite3.connect("data/marketing.db")
        df = pd.read_sql("SELECT * FROM campaign_metrics", conn)
        conn.close()
    except: return pd.DataFrame(), "❌ DB Error"

    df.columns = [c.title() for c in df.columns]
    df['Date'] = pd.to_datetime(df['Date'])
    status = "SIMULATION MODE"
    
    if use_live_google:
        try:
            import google_api
            ga = google_api.authenticate_google_analytics()
            if ga:
                df_ga = google_api.fetch_analytics_data(ga)
                if not df_ga.empty:
                    df = df[df['Platform'] != 'Google Analytics']
                    df_ga['Platform'] = 'Google Analytics'
                    df_ga['Cost'] = 0.0
                    if 'CTR' in df_ga.columns: df_ga.rename(columns={'CTR': 'Engagement_Rate'}, inplace=True)
                    else: df_ga['Engagement_Rate'] = 0.0
                    df = pd.concat([df, df_ga], ignore_index=True)
                    status = "LIVE DATA STREAM"
        except: status = "API CONNECTION FAILED"
            
    return df, status

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.title("⚙️ Settings")
    
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
    st.markdown("### Data Source")
    use_google_live = st.toggle("Google Live API", value=False)

# --- MAIN LOAD ---
df, status_msg = load_data(use_google_live)
if df.empty:
    st.error("Database empty. Please run 'generate_data.py' first.")
    st.stop()

# --- HERO SECTION ---
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<p class="big-title">DigitalPlus 24x7</p>', unsafe_allow_html=True)
    st.markdown("### Marketing Intelligence Hub")
    
    # Quick Links
    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    col_l1.link_button("🌐 Google", "https://analytics.google.com")
    col_l2.link_button("📘 Meta", "https://business.facebook.com")
    col_l3.link_button("💼 LinkedIn", "https://linkedin.com/campaignmanager")
    col_l4.link_button("📧 Mailchimp", "https://mailchimp.com")

with c2:
    # STATUS CARD (Dynamic Background)
    st.markdown(f"""
    <div style="background-color: {card_bg}; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #444; color: {text_color};">
        <span class="live-indicator"></span>
        <span class="status-text">{status_msg}</span>
        <br><br>
        <small style="opacity: 0.7;">Last Updated: {datetime.now().strftime('%H:%M:%S')}</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- FILTERS ---
f1, f2 = st.columns([1, 2])
sel_platform = f1.selectbox("Filter by Platform", ["All Platforms"] + sorted(df['Platform'].unique().tolist()))
d1, d2 = f2.date_input("Filter by Date", [df['Date'].min(), df['Date'].max()])

df_filtered = df[(df['Date'] >= pd.to_datetime(d1)) & (df['Date'] <= pd.to_datetime(d2))]
if sel_platform != "All Platforms":
    df_filtered = df_filtered[df_filtered['Platform'] == sel_platform]

# --- KPI CARDS ---
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Traffic", f"{df_filtered['Sessions'].sum():,}")
k2.metric("Total Conversions", f"{df_filtered['Conversions'].sum():,}")
k3.metric("Est. Ad Spend", f"${df_filtered['Cost'].sum():,.0f}")
k4.metric("Avg. Engagement", f"{df_filtered['Engagement_Rate'].mean():.1f}%")

st.markdown("---")

# --- VISUALIZATION TABS ---
tab1, tab2, tab3 = st.tabs(["📈 Trends & Forecast", "💰 ROI & Cost", "📊 Channel Split"])

with tab1:
    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        st.markdown("#### 🔮 AI Settings")
        forecast_days = st.radio("Prediction Horizon", [14, 30, 90], horizontal=True, format_func=lambda x: f"+{x} Days")
        show_forecast = st.checkbox("Show Forecast Line", value=True)
    
    with col_f2:
        daily = df_filtered.groupby('Date')['Sessions'].sum().reset_index()
        if show_forecast:
            chart_data = generate_forecast(daily, days=forecast_days)
            fig = px.line(chart_data, x='Date', y='Sessions', color='Type', line_dash='Type', 
                          title=f"Traffic Projection (+{forecast_days} Days)", template=plotly_template)
            fig.update_traces(line=dict(width=3))
        else:
            fig = px.line(daily, x='Date', y='Sessions', title="Historical Traffic", template=plotly_template)
        # Ensure plot background is transparent to match theme
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    if df_filtered['Cost'].sum() > 0:
        fig = px.scatter(df_filtered, x='Cost', y='Conversions', color='Platform', size='Sessions', 
                         title="Ad Spend Efficiency", template=plotly_template)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No cost data available for the selected view.")

with tab3:
    c_pie, c_bar = st.columns(2)
    with c_pie:
        fig = px.pie(df_filtered, values='Sessions', names='Platform', hole=0.6, title="Traffic Distribution", template=plotly_template)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with c_bar:
        fig = px.bar(df_filtered.groupby('Platform')['Engagement_Rate'].mean().reset_index(), 
                     x='Platform', y='Engagement_Rate', color='Platform', title="Engagement Quality by App", template=plotly_template)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- REPORT HUB ---
st.subheader("📑 Data Export Hub")
platforms_available = sorted(df['Platform'].unique().tolist())
tabs = st.tabs(platforms_available)

for i, platform in enumerate(platforms_available):
    with tabs[i]:
        df_export = df[df['Platform'] == platform]
        st.dataframe(df_export, use_container_width=True, height=300)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Download {platform} Report (CSV)",
            data=csv,
            file_name=f"{platform}_Report.csv",
            mime='text/csv'
        )