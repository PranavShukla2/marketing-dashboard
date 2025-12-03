import streamlit as st
import pandas as pd
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

def authenticate_google_analytics():
    # GA4 Scope
    SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

    try:
        # PLAN A: Check for Local File FIRST (Best for your laptop)
        if os.path.exists('client_secrets.json'):
            creds = service_account.Credentials.from_service_account_file(
                "client_secrets.json", scopes=SCOPES
            )
            print("✅ Authenticated locally using JSON file")

        # PLAN B: Check for Streamlit Cloud Secrets (Production)
        else:
            try:
                if "gcp_service_account" in st.secrets:
                    creds = service_account.Credentials.from_service_account_info(
                        st.secrets["gcp_service_account"], scopes=SCOPES
                    )
                    print("✅ Authenticated using Streamlit Cloud secrets")
                else:
                    raise ValueError("No secrets found")
            except Exception:
                # If both fail, we can't connect
                print("⚠️ No local key or cloud secret found.")
                return None

        # Build the GA4 Service (analyticsdata v1beta)
        analytics = build("analyticsdata", "v1beta", credentials=creds)
        return analytics

    except Exception as e:
        print("❌ Authentication ERROR:", e)
        return None

def fetch_analytics_data(analytics):
    # YOUR DIGITAL PLUS PROPERTY ID
    PROPERTY_ID = "487589561"

    try:
        response = analytics.properties().runReport(
            property=f"properties/{PROPERTY_ID}",
            body={
                "dateRanges": [{"startDate": "30daysAgo", "endDate": "today"}],
                "dimensions": [
                    {"name": "date"},
                    {"name": "sessionSource"},
                    {"name": "sessionCampaignName"},
                ],
                "metrics": [
                    {"name": "sessions"},
                    {"name": "conversions"},
                    {"name": "bounceRate"},
                    {"name": "engagementRate"}, # Proxy for CTR
                ],
            },
        ).execute()

        rows = response.get("rows", [])
        data = []

        for row in rows:
            dims = row["dimensionValues"]
            mets = row["metricValues"]
            
            data.append({
                "Date": pd.to_datetime(dims[0]["value"]),
                "Source": dims[1]["value"],
                "Campaign": dims[2]["value"],
                "Sessions": int(mets[0]["value"]),
                "Conversions": float(mets[1]["value"]),
                "Bounce_Rate": float(mets[2]["value"]) * 100,
                "CTR": float(mets[3]["value"]) * 100
            })

        if not data:
            print("⚠️ API connected but returned no data.")

        return pd.DataFrame(data)

    except Exception as e:
        print("❌ Fetch ERROR:", e)
        return pd.DataFrame()