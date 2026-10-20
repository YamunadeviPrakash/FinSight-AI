
import pandas as pd
from pathlib import Path

# Locate the CSV file
file_path = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "Daily Household Transactions.csv"
)

# Load the dataset
df = pd.read_csv(file_path)

print("\n--- FIRST 5 ROWS ---")
print(df.head())

print("\n--- DATASET SHAPE ---")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- DATA TYPES ---")
print(df.dtypes)

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- DUPLICATE ROWS ---")
print(df.duplicated().sum())

print("\n--- DATASET SUMMARY ---")
print(df.describe(include="all").T)
