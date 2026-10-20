
import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "raw" / "Daily Household Transactions.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "cleaned_transactions.csv"

# Load the original dataset
df = pd.read_csv(INPUT_FILE)

# Convert dates into datetime format
df["Date"] = pd.to_datetime(
    df["Date"],
    dayfirst=True,
    errors="coerce",
    format="mixed"
)

# Remove rows when essential fields are invalid
df = df.dropna(subset=["Date", "Amount", "Income/Expense"]).copy()

# Standardize text columns
text_columns = [
    "Mode", "Category", "Subcategory",
    "Note", "Income/Expense", "Currency"
]

for col in text_columns:
    df[col] = df[col].fillna("Unknown").astype(str).str.strip()

# Standardize transaction labels
df["Income/Expense"] = df["Income/Expense"].str.title()

# Flag exact duplicate rows for review
df["Possible_Duplicate"] = df.duplicated(
    subset=[
        "Date", "Mode", "Category", "Subcategory",
        "Note", "Amount", "Income/Expense", "Currency"
    ],
    keep=False
)

# Classify transaction types
df["Transaction_Type"] = df["Income/Expense"].map({
    "Expense": "Expense",
    "Income": "Income",
    "Transfer-Out": "Transfer"
}).fillna("Other")

# Create separate amount columns for financial analysis
df["Expense_Amount"] = df["Amount"].where(
    df["Transaction_Type"] == "Expense", 0
)

df["Income_Amount"] = df["Amount"].where(
    df["Transaction_Type"] == "Income", 0
)

df["Transfer_Amount"] = df["Amount"].where(
    df["Transaction_Type"] == "Transfer", 0
)

# Add useful time columns
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Year_Month"] = df["Date"].dt.to_period("M").astype(str)

# Save cleaned dataset
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

print("DATA CLEANING COMPLETED")
print("Original dataset rows: 2461")
print("Cleaned dataset rows:", len(df))
print("Possible duplicate rows:", df["Possible_Duplicate"].sum())
print("Missing values remaining:", int(df.isna().sum().sum()))
print("Output saved to:", OUTPUT_FILE)

print("\nTransaction type counts:")
print(df["Transaction_Type"].value_counts())

print("\nTotal amounts by transaction type:")
print(
    df.groupby("Transaction_Type")["Amount"]
    .agg(["count", "sum", "mean"])
    .round(2)
)
