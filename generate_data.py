import pandas as pd
import numpy as np
import random
import sqlite3
from datetime import datetime, timedelta

# Settings
num_days = 90
platforms = ['Google Analytics', 'Facebook Ads', 'Instagram', 'LinkedIn Ads', 'Email Marketing']

print("🔄 Generating Omni-Channel Marketing Data...")

data = []
start_date = datetime.today() - timedelta(days=num_days)

for i in range(num_days):
    current_date = start_date + timedelta(days=i)
    
    for platform in platforms:
        # 1. Google Analytics
        if platform == 'Google Analytics':
            campaigns = ['Organic_Search', 'Direct', 'Referral']
            cpc = 0
            sessions = random.randint(800, 3000)
            engagement = random.uniform(40, 70)
            
        # 2. Facebook Ads
        elif platform == 'Facebook Ads':
            campaigns = ['Retargeting_Sale', 'New_User_Promo']
            cpc = random.uniform(0.5, 1.5)
            sessions = int(random.randint(2000, 10000) * 0.02)
            engagement = random.uniform(10, 40)

        # 3. Instagram
        elif platform == 'Instagram':
            campaigns = ['Influencer_Reel', 'Story_Ads']
            cpc = random.uniform(0.8, 2.0)
            sessions = int(random.randint(1500, 8000) * 0.03)
            engagement = random.uniform(50, 90)

        # 4. LinkedIn Ads
        elif platform == 'LinkedIn Ads':
            campaigns = ['B2B_Lead_Gen', 'Hiring_Q4']
            cpc = random.uniform(3.0, 8.0)
            sessions = int(random.randint(200, 1500) * 0.015)
            engagement = random.uniform(20, 50)

        # 5. Email Marketing
        elif platform == 'Email Marketing':
            campaigns = ['Weekly_Newsletter', 'Product_Update']
            cpc = 0.0 
            sessions = random.randint(300, 1200) 
            engagement = random.uniform(30, 60)

        conversions = int(sessions * random.uniform(0.02, 0.08))
        cost = round(sessions * cpc, 2)
        
        data.append([
            current_date.strftime('%Y-%m-%d'),
            platform,
            random.choice(campaigns),
            sessions,
            conversions,
            cost,
            round(engagement, 2)
        ])

df = pd.DataFrame(data, columns=['date', 'platform', 'campaign', 'sessions', 'conversions', 'cost', 'engagement_rate'])

try:
    conn = sqlite3.connect('data/marketing.db')
    df.to_sql('campaign_metrics', conn, if_exists='replace', index=False)
    conn.close()
    print(f"✅ Database updated: {len(df)} rows generated.")
except Exception as e:
    print(f"❌ Error: {e}")
    