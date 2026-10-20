
import pandas as pd
from pathlib import Path

file_path = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "Daily Household Transactions.csv"
)

df = pd.read_csv(file_path)

# Convert text dates into datetime values
df["Date"] = pd.to_datetime(
    df["Date"],
    dayfirst=True,
    errors="coerce",
    format="mixed"
)

print("\n--- DATE COVERAGE ---")
print("Earliest date:", df["Date"].min())
print("Latest date:", df["Date"].max())
print("Invalid dates:", df["Date"].isna().sum())

print("\n--- TRANSACTION TYPES ---")
print(df["Income/Expense"].value_counts(dropna=False))

print("\n--- TOP 10 CATEGORIES ---")
print(df["Category"].value_counts().head(10))

print("\n--- MONTHLY TRANSACTION COUNTS ---")
monthly_counts = (
    df.dropna(subset=["Date"])
    .set_index("Date")
    .resample("MS")
    .size()
)
print(monthly_counts.to_string())

print("\n--- LARGEST 10 TRANSACTIONS ---")
print(
    df.nlargest(10, "Amount")[
        ["Date", "Category", "Amount", "Income/Expense"]
    ].to_string(index=False)
)

print("\n--- DUPLICATE ROW EXAMPLES ---")
print(df[df.duplicated(keep=False)].head(20).to_string(index=False))
