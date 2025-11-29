import pandas as pd
import numpy as np
import random
import sqlite3
from datetime import datetime, timedelta


num_days = 45  
sources = ['Organic Search', 'Social Media', 'Email', 'Paid Ads', 'Referral']

print("🔄 Generating random marketing data...")

data = []
start_date = datetime.today() - timedelta(days=num_days)

for i in range(num_days):
    current_date = start_date + timedelta(days=i)
    
    # Creating 5-10 entries per day
    for _ in range(random.randint(5, 10)):
        source = random.choice(sources)
        
        
        if source == 'Paid Ads':
            campaign = random.choice(['Winter_Sale', 'New_Year_Promo', 'Retargeting_Q1'])
        elif source == 'Email':
            campaign = 'Newsletter_Weekly'
        else:
            campaign = 'None'
            
        sessions = random.randint(100, 5000)
        conversions = int(sessions * random.uniform(0.01, 0.05)) 
        bounce_rate = round(random.uniform(30, 70), 2) 
        ctr = round(random.uniform(1, 5), 2) if source == 'Paid Ads' else 0 
        
        data.append([
            current_date.strftime('%Y-%m-%d'),
            campaign,
            source,
            sessions,
            conversions,
            bounce_rate,
            ctr
        ])

# Creating DataFrame
columns = ['date', 'campaign', 'source', 'sessions', 'conversions', 'bounce_rate', 'ctr']
df = pd.DataFrame(data, columns=columns)


try:
    
    conn = sqlite3.connect('data/marketing.db')
    
    
    df.to_sql('campaign_metrics', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"✅ Success! Database created at: data/marketing.db")
    print(f"✅ Table 'campaign_metrics' filled with {len(df)} rows.")
    
except Exception as e:
    print(f"❌ Error creating database: {e}")