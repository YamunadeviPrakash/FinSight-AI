
# FinSight AI — Financial Intelligence Dashboard

An AI and data science portfolio project for exploring financial transactions, analyzing spending patterns, and identifying potentially unusual expenses.

## Features

- Interactive financial dashboard built with Streamlit
- Income, expense, and transfer analysis
- Spending trends and category breakdowns
- Searchable transaction history
- Unusual-spending detection using Isolation Forest
- Historical financial insights

## Technology Stack

- Python
- Pandas and NumPy
- Scikit-learn
- Streamlit
- Plotly

## Project Structure

```text
AI-Financial-Intelligence/
├── dashboard/
│   ├── app.py
│   └── app_backup.py
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── inspect_data.py
│   ├── check_dates.py
│   ├── clean_data.py
│   └── anomaly_detection.py
├── models/
├── reports/
├── requirements.txt
├── .gitignore
└── README.md
```

## Run Locally

1. Install Python.
2. Create and activate a virtual environment.
3. Install dependencies:

   `pip install -r requirements.txt`

4. Place the permitted transaction dataset in `data/raw/`.
5. Run the cleaning script:

   `python src/clean_data.py`

6. Run anomaly detection:

   `python src/anomaly_detection.py`

7. Start the dashboard:

   `python -m streamlit run dashboard/app.py`

## Data and Limitations

The current prototype uses historical sample transactions, not live bank data. Anomaly flags indicate transactions for review and do not establish fraud. Automatic transaction synchronization and multi-user bank integration are future enhancements.
