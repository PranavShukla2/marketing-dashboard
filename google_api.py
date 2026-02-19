import streamlit as st
import pandas as pd
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Dimension, Metric
)

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

def authenticate_google_analytics():
    creds = None
    try:
        if "gcp_service_account" in st.secrets:
            key_dict = dict(st.secrets["gcp_service_account"])
            key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
            creds = service_account.Credentials.from_service_account_info(
                key_dict, scopes=SCOPES
            )
            return creds
    except Exception:
        pass

    if not creds:
        try:
            if os.path.exists("client_secrets.json"):
                creds = service_account.Credentials.from_service_account_file(
                    "client_secrets.json", scopes=SCOPES
                )
                return creds
        except Exception as e:
            print(f"Local Auth Error: {e}")

    return None

def get_ga4_properties(creds):
    try:
        service = build('analyticsadmin', 'v1beta', credentials=creds)
        accounts_response = service.accounts().list().execute()
        
        properties = {}
        if 'accounts' in accounts_response:
            for account in accounts_response['accounts']:
                account_name = account['name']
                props_response = service.properties().list(filter=f"parent:{account_name}").execute()
                if 'properties' in props_response:
                    for prop in props_response['properties']:
                        prop_id = prop['name'].split('/')[-1]
                        display_name = f"{account['displayName']} -> {prop['displayName']}"
                        properties[display_name] = prop_id
        return properties
    except Exception as e:
        print(f"Property List Error: {e}")
        return {}

def fetch_traffic_sources(creds, property_id, date_range_days=30):
    try:
        client = BetaAnalyticsDataClient(credentials=creds)
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="sessionSource"), Dimension(name="sessionMedium")],
            metrics=[Metric(name="sessions")],
            date_ranges=[DateRange(start_date=f"{date_range_days}daysAgo", end_date="today")],
            limit=10 
        )
        response = client.run_report(request)
        data = [{"Source": row.dimension_values[0].value, "Medium": row.dimension_values[1].value, "Sessions": int(row.metric_values[0].value)} for row in response.rows]
        return pd.DataFrame(data)
    except Exception: return pd.DataFrame()

def fetch_campaign_details(creds, property_id, date_range_days=30):
    try:
        client = BetaAnalyticsDataClient(credentials=creds)
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="sessionSource"), Dimension(name="sessionCampaignName"), Dimension(name="sessionManualAdContent")],
            metrics=[Metric(name="sessions"), Metric(name="conversions"), Metric(name="engagementRate")],
            date_ranges=[DateRange(start_date=f"{date_range_days}daysAgo", end_date="today")]
        )
        response = client.run_report(request)
        data = [{"Source": r.dimension_values[0].value, "Campaign": r.dimension_values[1].value, "Ad Content / Post": r.dimension_values[2].value, "Sessions": int(r.metric_values[0].value), "Conversions": int(r.metric_values[1].value), "Engagement Rate": float(r.metric_values[2].value)} for r in response.rows]
        return pd.DataFrame(data)
    except Exception: return pd.DataFrame()

def fetch_time_series_data(creds, property_id, date_range_days=90):
    """Fetches daily traffic data for AI Forecasting."""
    try:
        client = BetaAnalyticsDataClient(credentials=creds)
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="date")],
            metrics=[Metric(name="sessions")],
            date_ranges=[DateRange(start_date=f"{date_range_days}daysAgo", end_date="today")]
        )
        response = client.run_report(request)
        data = []
        for row in response.rows:
            date_str = row.dimension_values[0].value # Format: YYYYMMDD
            data.append({
                "Date": pd.to_datetime(date_str, format='%Y%m%d'),
                "Sessions": int(row.metric_values[0].value)
            })
        df = pd.DataFrame(data).sort_values(by="Date")
        return df
    except Exception as e:
        print(f"Time Series Error: {e}")
        return pd.DataFrame()