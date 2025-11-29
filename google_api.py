import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

def authenticate_google_analytics():
    """
    Authenticates with the Google Analytics API v4.
    Checks Streamlit Secrets first (for Cloud), then falls back to local JSON (for Laptop).
    """
    SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
    
    try:
        # PLAN A: Check for Streamlit Cloud Secrets (Production Environment)
        # This prevents the "Key Revoked" issue on GitHub
        if "gcp_service_account" in st.secrets:
            key_dict = st.secrets["gcp_service_account"]
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, SCOPES)
            print("✅ Authenticated using Streamlit Secrets (Cloud)")
            
        # PLAN B: Check for Local File (Development Environment)
        else:
            KEY_FILE_LOCATION = 'client_secrets.json'
            credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, SCOPES)
            print("✅ Authenticated using Local JSON File")
        
        # Build the service object
        analytics = build('analyticsreporting', 'v4', credentials=credentials)
        return analytics
        
    except Exception as e:
        # This print will show up in your terminal or Streamlit logs
        print(f"❌ API Authentication Failed: {e}")
        return None

def fetch_analytics_data(analytics):
    """
    Queries the API and returns a Pandas DataFrame.
    """
    try:
        # Define what we want (Metrics & Dimensions)
        # NOTE: You must replace 'YOUR_VIEW_ID_HERE' with your actual View ID if you want this to work.
        # If you don't have a View ID, this part will fail safely and your app will use Mock Data.
        VIEW_ID = 'YOUR_VIEW_ID_HERE' 
        
        response = analytics.reports().batchGet(
            body={
                'reportRequests': [
                {
                    'viewId': VIEW_ID,
                    'dateRanges': [{'startDate': '30daysAgo', 'endDate': 'today'}],
                    'metrics': [
                        {'expression': 'ga:sessions'},
                        {'expression': 'ga:transactions'}, # Conversions
                        {'expression': 'ga:bounceRate'},
                        {'expression': 'ga:percentNewSessions'} # Proxy for CTR
                    ],
                    'dimensions': [
                        {'name': 'ga:date'},
                        {'name': 'ga:source'},
                        {'name': 'ga:campaign'}
                    ]
                }]
            }
        ).execute()
        
        # Parse the JSON response
        data_list = []
        for report in response.get('reports', []):
            for row in report.get('data', {}).get('rows', []):
                dims = row.get('dimensions', [])
                metrics = row.get('metrics', [])[0].get('values', [])
                
                data_list.append({
                    'Date': pd.to_datetime(dims[0]),
                    'Source': dims[1],
                    'Campaign': dims[2],
                    'Sessions': int(metrics[0]),
                    'Conversions': int(metrics[1]),
                    'Bounce_Rate': float(metrics[2]),
                    'CTR': float(metrics[3]) 
                })
                
        return pd.DataFrame(data_list)
        
    except Exception as e:
        print(f"⚠️ Error Fetching Data: {e}")
        return pd.DataFrame() # Return empty if fetch fails