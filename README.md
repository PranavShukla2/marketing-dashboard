📊 Marketing Analytics Dashboard

An integrated analytics platform designed to centralize marketing KPIs into a single, interactive interface. This dashboard allows marketing teams to monitor traffic trends, conversion rates, and campaign performance in real-time.

🚀 Key Features

Hybrid Data Architecture: Automatically fetches live data from Google Analytics API v4 and caches it into a local SQLite database. If the API is unavailable, the system seamlessly falls back to the database to ensure zero downtime.

Interactive Visualizations: Dynamic charts powered by Plotly to analyze traffic sources and campaign bounce rates.

Smart Filtering: Sidebar controls to filter data by specific Date Ranges, Traffic Sources, and Marketing Campaigns.

Data Export: One-click functionality to download processed data as CSV reports.

🛠️ Tech Stack

Frontend: Streamlit (Python)

Backend Logic: Python, Google API Client

Database: SQLite (Serverless local storage)

Visualization: Plotly Express

Deployment: Streamlit Community Cloud

⚙️ Installation & Setup

If you want to run this project locally on your machine, follow these steps:

1. Clone the Repository

git clone https://github.com/YOUR_USERNAME/marketing-dashboard.git


2. Install Dependencies

pip install -r requirements.txt


3. Configure API Credentials

To connect to the live Google Analytics API, you need a Service Account key.

Place your client_secrets.json file in the root directory.

(Optional) If you don't have API keys, the app will automatically run in "Simulated Mode" using the SQLite database.

4. Run the Dashboard

streamlit run main.py


🔐 Deployment (Streamlit Cloud)

This project is deployed using Streamlit Community Cloud.
To handle API security in the cloud without exposing keys on GitHub:

The client_secrets.json file is excluded from the repository (via .gitignore).

Production keys are stored securely in Streamlit Secrets configuration.

📂 Project Structure

marketing-dashboard/
├── data/
│   └── marketing.db        # SQLite database (Simulated/Cached data)
├── main.py                 # The main dashboard application (Frontend)
├── google_api.py           # Backend logic for API authentication & fetching
├── generate_data.py        # Script to generate mock data for testing
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation


📈 Future Improvements

Integration with Facebook Ads API.

User authentication system for multiple team members.

Advanced forecasting using Machine Learning.

Developed by Pranav Shukla as part of the Marketing Analytics Internship Project.