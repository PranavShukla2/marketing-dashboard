import sqlite3

def create_database():
    
    conn = sqlite3.connect('data/marketing.db')
    cursor = conn.cursor()

    # Define the Schema (The structure of your data) 
    create_table_query = """
    CREATE TABLE IF NOT EXISTS campaign_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        campaign_name TEXT,
        source TEXT,
        sessions INTEGER,
        conversions INTEGER,
        bounce_rate REAL,
        ctr REAL
    );
    """
    
    cursor.execute(create_table_query)
    print("✅ Database 'marketing.db' and table 'campaign_metrics' created successfully.")

   
    try:
        import pandas as pd
        df = pd.read_csv('data/mock_data.csv')
        
        # Rename columns to match SQL standard (lowercase, no spaces usually)
        df.rename(columns={
            'Date': 'date',
            'Campaign': 'campaign_name',
            'Source': 'source',
            'Sessions': 'sessions',
            'Conversions': 'conversions',
            'Bounce_Rate': 'bounce_rate',
            'CTR': 'ctr'
        }, inplace=True)
        
        # Write to SQL
        df.to_sql('campaign_metrics', conn, if_exists='replace', index=False)
        print(f"✅ Loaded {len(df)} rows from CSV into SQLite.")
        
    except Exception as e:
        print(f"⚠️ Could not load initial data: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()






