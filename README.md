📊 DigitalPlus 24x7 Marketing Hub

An integrated Omni-Channel Marketing Analytics Command Center designed to centralize performance metrics from Google Analytics and Meta Ads (Facebook/Instagram) into a single, interactive interface.

🌟 Key Features

Hybrid Data Architecture:

Live Mode: Connects to Google Analytics API (GA4) for real-time traffic analysis.

Simulation Mode: Includes a robust data simulator for Facebook & Instagram Ads to demonstrate UI capabilities before API provisioning.

Zero-Data Handling: Smartly displays "0" or "No Data" when live feeds are empty, preventing misleading reporting.

🤖 AI Forecasting:

Built-in Linear Regression Engine that predicts traffic trends for the next 14, 30, or 90 days based on historical velocity.

📊 Advanced Visualization:

Traffic Share: Pie charts showing the split between Search (Google) and Social (Meta).

ROI Matrix: Scatter plots analyzing Cost Efficiency (Ad Spend vs. Conversions).

Engagement Tracking: Bar charts comparing user engagement rates across platforms.

📑 Data Export Hub:

One-click download of raw performance data (CSV) for external audits.

🛠️ Tech Stack

Frontend: Streamlit (Python)

Backend Logic: Python, Google API Client (GA4 Data API)

Database: SQLite (Serverless local storage for simulation & caching)

Visualization: Plotly Express (Interactive charts)

Deployment: Streamlit Community Cloud

⚙️ Installation & Setup

If you want to run this project locally:

Clone the Repository

git clone [https://github.com/YOUR_USERNAME/marketing-dashboard.git](https://github.com/YOUR_USERNAME/marketing-dashboard.git)
cd marketing-dashboard


Install Dependencies

pip install -r requirements.txt


Generate Database
Run this script once to populate the simulation database:

python generate_data.py


Run the Dashboard

streamlit run main.py


🔐 Configuration (Secrets)

To enable the Live Google Analytics feed, you must provide a Service Account JSON key:

Place client_secrets.json in the root folder (for local run).

Add contents to Streamlit Secrets (for cloud deployment).

📂 Project Structure

marketing-dashboard/
├── data/
│   └── marketing.db        # SQLite database (Simulated/Cached data)
├── main.py                 # The main dashboard application
├── google_api.py           # Backend logic for Google GA4 API
├── generate_data.py        # Script to generate simulation data (FB/Insta)
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation


Developed by Pranav Shukla as part of the Marketing Analytics Internship Project.