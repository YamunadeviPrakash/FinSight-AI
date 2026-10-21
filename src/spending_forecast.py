
from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "processed" / "cleaned_transactions.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "spending_forecast.csv"


def load_monthly_expenses():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}\n"
            "Run: python src/clean_data.py"
        )

    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df = df.dropna(subset=["Date", "Amount"])

    expenses = df[
        df["Income/Expense"].astype(str).str.strip().str.lower()
        == "expense"
    ]

    monthly = (
        expenses.set_index("Date")["Amount"]
        .resample("MS")
        .sum()
        .asfreq("MS", fill_value=0)
    )

    if len(monthly) < 24:
        raise ValueError(
            "At least 24 months of data are required "
            "for seasonal-naive forecasting."
        )

    return monthly


def main():
    monthly = load_monthly_expenses()

    # Evaluate the last 12 months, one month at a time.
    test_start = len(monthly) - 12
    results = []

    for i in range(test_start, len(monthly)):
        date = monthly.index[i]
        actual = float(monthly.iloc[i])

        previous_prediction = float(monthly.iloc[i - 1])
        seasonal_prediction = float(monthly.loc[
            date - pd.DateOffset(years=1)
        ])

        results.append({
            "Month": date.strftime("%Y-%m"),
            "Actual": actual,
            "Seasonal_Naive": seasonal_prediction,
            "Previous_Month": previous_prediction,
        })

    evaluation = pd.DataFrame(results)

    seasonal_mae = mean_absolute_error(
        evaluation["Actual"], evaluation["Seasonal_Naive"]
    )
    previous_mae = mean_absolute_error(
        evaluation["Actual"], evaluation["Previous_Month"]
    )

    print("\nFINSIGHT AI — SEASONAL FORECAST")
    print("=" * 45)
    print(f"Historical months: {len(monthly)}")
    print(f"Evaluation months: {len(evaluation)}")
    print(f"Seasonal-naive MAE: ₹{seasonal_mae:,.2f}")
    print(f"Previous-month MAE: ₹{previous_mae:,.2f}")

    # Forecast the next three calendar months using the same month
    # from the most recent available historical year.
    future_rows = []

    for step in range(1, 4):
        next_date = monthly.index[-1] + pd.offsets.MonthBegin(step)
        prior_year_date = next_date - pd.DateOffset(years=1)

        if prior_year_date not in monthly.index:
            raise ValueError(
                f"No matching historical month for {next_date:%Y-%m}."
            )

        prediction = float(monthly.loc[prior_year_date])

        future_rows.append({
            "Month": next_date.strftime("%Y-%m"),
            "Forecast_Expense": round(max(0.0, prediction), 2),
            "Forecast_Method": "Seasonal naive",
        })

    forecast = pd.DataFrame(future_rows)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    forecast.to_csv(OUTPUT_PATH, index=False)

    print("\nNext three forecast periods:")
    print(forecast.to_string(index=False))
    print(f"\nSaved to: {OUTPUT_PATH}")
    print(
        "\nNote: Forecast dates reflect the historical dataset. "
        "They are not current-year predictions."
    )


if __name__ == "__main__":
    main()
