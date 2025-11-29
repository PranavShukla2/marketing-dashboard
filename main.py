import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3


# since as of now i don't have actual values mock values are used therefore this try block
# ensures the app doesn't crash if google_api.py is missing 
try:
    import google_api
    BACKEND_EXISTS = True
except ImportError:
    BACKEND_EXISTS = False

# --- CONFIGURATION ---
st.set_page_config(page_title="Marketing Analytics Dashboard", layout="wide")

# --- SIDEBAR: DATA CONTROLS ---
st.sidebar.header("🔌 Data Connection")

# The "Shift" Button (Mode Switcher)
data_mode = st.sidebar.radio(
    "Select Data Source:",
    options=["Local Database (Simulated)", "Live Google API v4"],
    index=0  # Default to Local DB for safety
)

st.sidebar.markdown("---")

# --- DATA LOADING FUNCTION ---
@st.cache_data
def load_data(mode):
    df = pd.DataFrame()
    status_msg = ""
    status_type = "info" # info, success, warning, error

    # CASE 1: User selected "Live Google API"
    if mode == "Live Google API v4":
        if BACKEND_EXISTS:
            try:
                # Attempt Connection
                analytics = google_api.authenticate_google_analytics()
                if analytics:
                    # Attempt Fetch
                    df = google_api.fetch_analytics_data(analytics)
                    if not df.empty:
                        status_msg = "✅ Connected to Live Google Analytics API"
                        status_type = "success"
                    else:
                        raise ValueError("API returned empty data")
                else:
                    raise ConnectionError("Authentication failed")
            except Exception as e:
                # IF CRASH: Fail gracefully and tell the user
                status_msg = f"❌ API Error: {e}"
                status_type = "error"
        else:
             status_msg = "⚠️ Backend file 'google_api.py' not found."
             status_type = "warning"

    # CASE 2: User selected "Local Database" OR API Failed above
    # If df is still empty (because API crashed or wasn't selected), load from SQLite
    if df.empty:
        try:
            # Connect to SQLite Database
            conn = sqlite3.connect("data/marketing.db")
            
            # Read Data
            query = "SELECT * FROM campaign_metrics"
            df = pd.read_sql(query, conn)
            conn.close()
            
            # Rename columns to Title Case (SQL is usually lowercase)
            df.rename(columns={
                'date': 'Date', 'campaign': 'Campaign', 'source': 'Source',
                'sessions': 'Sessions', 'conversions': 'Conversions',
                'bounce_rate': 'Bounce_Rate', 'ctr': 'CTR'
            }, inplace=True)
            
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Update status message based on why we are here
            if mode == "Live Google API v4":
                status_msg += " | 🔄 Switched to Local Database Fallback"
            else:
                status_msg = "🗄️ Using Local Database (SQLite)"
                status_type = "info"
                
        except Exception as e:
            st.error(f"CRITICAL ERROR: Could not read from database 'marketing.db'. Please run 'generate_data.py' first. Error: {e}")
            st.stop()
            
    return df, status_msg, status_type

# --- LOAD DATA BASED ON SELECTION ---
df, msg, msg_type = load_data(data_mode)

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Options")

# Date Range Filter
min_date = df['Date'].min()
max_date = df['Date'].max()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Source Filter
source_options = st.sidebar.multiselect(
    "Select Traffic Source",
    options=df['Source'].unique(),
    default=df['Source'].unique()
)

# Campaign Filter
campaign_options = st.sidebar.multiselect(
    "Select Campaign",
    options=df['Campaign'].unique(),
    default=df['Campaign'].unique()
)

# --- FILTER LOGIC ---
df_selection = df.query(
    "Date >= @start_date and Date <= @end_date and Source == @source_options and Campaign == @campaign_options"
)

# --- MAIN DASHBOARD INTERFACE ---
st.title("📊 Marketing Analytics Dashboard")

# Connection Status Banner
if msg_type == "success":
    st.success(msg)
elif msg_type == "error":
    st.error(msg)
elif msg_type == "warning":
    st.warning(msg)
else:
    st.info(msg)

st.markdown("---")

# --- TOP KPI METRICS ---
if not df_selection.empty:
    total_sessions = df_selection["Sessions"].sum()
    total_conversions = df_selection["Conversions"].sum()
    avg_bounce_rate = df_selection["Bounce_Rate"].mean()
    avg_ctr = df_selection["CTR"].mean() if "CTR" in df_selection.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sessions", f"{total_sessions:,}")
    col2.metric("Total Conversions", f"{total_conversions:,}")
    col3.metric("Avg Bounce Rate", f"{avg_bounce_rate:.1f}%")
    col4.metric("Avg CTR (Ads)", f"{avg_ctr:.2f}%")
else:
    st.warning("No data available for the selected filters.")

st.markdown("---")

# --- VISUALIZATIONS ---
if not df_selection.empty:
    # Row 1: Traffic Trend
    st.subheader("Traffic Trend Over Time")
    
    daily_trend = df_selection.groupby('Date')['Sessions'].sum().reset_index()
    
    fig_trend = px.line(
        daily_trend,
        x='Date', y='Sessions',
        title="Daily Sessions Trend",
        template="plotly_white"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # Row 2: Sources and Campaigns
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Conversions by Traffic Source")
        source_breakdown = df_selection.groupby('Source')['Conversions'].sum().reset_index()
        
        fig_source = px.bar(
            source_breakdown,
            x='Source', y='Conversions',
            title="Total Conversions by Source",
            template="plotly_white", color='Source'
        )
        st.plotly_chart(fig_source, use_container_width=True)

    with col_right:
        st.subheader("Campaign Performance (Bounce Rate)")
        campaign_bounce = df_selection.groupby('Campaign')['Bounce_Rate'].mean().reset_index()
        
        fig_campaign = px.bar(
            campaign_bounce,
            x='Campaign', y='Bounce_Rate',
            title="Avg Bounce Rate by Campaign",
            template="plotly_white", color='Campaign'
        )
        st.plotly_chart(fig_campaign, use_container_width=True)

# --- DATA TABLE & EXPORT ---
st.markdown("---")
st.subheader("Detailed Data View")

with st.expander("View Raw Data"):
    st.dataframe(df_selection)

    csv_data = df_selection.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv_data,
        file_name='marketing_data_export.csv',
        mime='text/csv',
    )