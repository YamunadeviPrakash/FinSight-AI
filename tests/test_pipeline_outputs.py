
import unittest
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"


class TestFinSightPipeline(unittest.TestCase):

    def test_cleaned_transactions_exist(self):
        path = DATA_DIR / "cleaned_transactions.csv"
        self.assertTrue(path.exists(), "Cleaned transactions file is missing")

        df = pd.read_csv(path)
        required = {
            "Date", "Amount", "Transaction_Type",
            "Expense_Amount", "Income_Amount"
        }
        self.assertTrue(required.issubset(df.columns))
        self.assertGreater(len(df), 0)

    def test_anomaly_results_exist(self):
        path = DATA_DIR / "anomaly_results.csv"
        self.assertTrue(path.exists(), "Anomaly results file is missing")

        df = pd.read_csv(path)
        required = {"Anomaly_Flag", "Anomaly_Score", "Review_Reason"}
        self.assertTrue(required.issubset(df.columns))
        self.assertGreater(len(df), 0)

    def test_forecast_results_are_valid(self):
        path = DATA_DIR / "spending_forecast.csv"
        self.assertTrue(path.exists(), "Forecast file is missing")

        df = pd.read_csv(path)
        required = {"Month", "Forecast_Expense", "Forecast_Method"}
        self.assertTrue(required.issubset(df.columns))
        self.assertEqual(len(df), 3)
        self.assertTrue(
            pd.to_numeric(df["Forecast_Expense"], errors="coerce")
            .notna().all()
        )
        self.assertTrue(
            (df["Forecast_Expense"] >= 0).all()
        )


if __name__ == "__main__":
    unittest.main()
