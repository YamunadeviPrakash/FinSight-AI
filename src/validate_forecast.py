
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "processed" / "cleaned_transactions.csv"

# Load and prepare transactions
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

# Build features from historical data
data = pd.DataFrame(index=monthly.index)
data["Actual"] = monthly
data["Month"] = data.index.month
data["Year"] = data.index.year
data["Lag_1"] = monthly.shift(1)
data["Lag_2"] = monthly.shift(2)
data["Lag_3"] = monthly.shift(3)
data["Rolling_3"] = monthly.shift(1).rolling(3).mean()

features = ["Month", "Year", "Lag_1", "Lag_2", "Lag_3", "Rolling_3"]
data = data.dropna(subset=features)

# Evaluate the final 18 months as three consecutive 6-month windows.
# Each prediction uses only the history available before that month.
first_test_position = max(12, len(data) - 18)
results = []

for i in range(first_test_position, len(data)):
    train = data.iloc[:i]
    test = data.iloc[[i]]

    date = test.index[0]
    actual = float(test["Actual"].iloc[0])

    # Previous-month baseline
    previous_prediction = float(monthly.loc[date - pd.offsets.MonthBegin(1)])

    # Same month in the previous year
    prior_year_date = date - pd.DateOffset(years=1)
    seasonal_prediction = float(monthly.loc[prior_year_date])

    # Random Forest
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=5,
        random_state=42,
    )
    model.fit(train[features], train["Actual"])
    rf_prediction = max(0.0, float(model.predict(test[features])[0]))

    results.append({
        "Month": date,
        "Actual": actual,
        "Previous_Month": previous_prediction,
        "Seasonal_Naive": seasonal_prediction,
        "Random_Forest": rf_prediction,
    })

results = pd.DataFrame(results)

# Score each of the three consecutive six-month windows
results["Window"] = (
    results["Month"].dt.year.astype(str)
    + "-"
    + (((results["Month"].dt.month - 1) // 6) * 6 + 1)
    .astype(str).str.zfill(2)
)

models = {
    "Seasonal naive": "Seasonal_Naive",
    "Random Forest": "Random_Forest",
    "Previous month": "Previous_Month",
}

print("\nMULTI-WINDOW WALK-FORWARD VALIDATION")
print("=" * 55)
print(f"Months evaluated: {len(results)}")
print("\nMAE by six-month window:")

for window, group in results.groupby("Window"):
    print(f"\nWindow starting {window}:")
    for name, column in models.items():
        mae = mean_absolute_error(group["Actual"], group[column])
        print(f"  {name}: ₹{mae:,.2f}")

print("\nOVERALL MAE")
print("=" * 30)
overall_scores = []

for name, column in models.items():
    mae = mean_absolute_error(results["Actual"], results[column])
    overall_scores.append((name, mae))
    print(f"{name}: ₹{mae:,.2f}")

print("\nNote: These results are based on a small historical dataset.")
print("The best model may differ for other users or future periods.")
