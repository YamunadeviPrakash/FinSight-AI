
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed" / "cleaned_transactions.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed" / "anomaly_results.csv"
)


def detect_unusual_spending(data, contamination=0.03):
    """
    Flag potentially unusual expense transactions using Isolation Forest.

    The model uses transaction amount and category-specific context.
    A flagged transaction should be reviewed, not assumed fraudulent.
    """
    df = data.copy()

    # Inspect category labels before deciding what to exclude
    print("\n--- Expense categories and totals ---")

    expense_rows = df[
        (df["Transaction_Type"] == "Expense")
        & (df["Amount"] > 0)
    ].copy()

    category_summary = (
        expense_rows.groupby("Category")
        .agg(
            Transactions=("Amount", "count"),
            Total_Amount=("Amount", "sum"),
            Median_Amount=("Amount", "median")
        )
        .sort_values("Total_Amount", ascending=False)
    )

    print(category_summary.to_string())

    # Exclude categories that usually represent transfers or investments
    excluded_categories = {
        "money transfer",
        "investment",
        "public provident fund",
            "recurring deposit",
    }

    expenses = expense_rows[
        ~expense_rows["Category"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(excluded_categories)
    ].copy()

    print("\nExcluded categories:", sorted(excluded_categories))
    print("Everyday expense transactions analyzed:", len(expenses))

    if len(expenses) < 10:
        raise ValueError(
            "Not enough expense records to train the anomaly model."
        )

    # Category context helps compare amounts across spending categories
    expenses["Category_Median"] = expenses.groupby(
        "Category"
    )["Amount"].transform("median")

    expenses["Amount_to_Category_Median"] = (
        expenses["Amount"]
        / expenses["Category_Median"].replace(0, 1)
    )

    # Use log amounts because financial transactions are highly skewed
    expenses["Log_Amount"] = __import__("numpy").log1p(
        expenses["Amount"]
    )
    expenses["Log_Relative_Amount"] = __import__("numpy").log1p(
        expenses["Amount_to_Category_Median"].clip(lower=0)
    )

    features = expenses[
        ["Log_Amount", "Log_Relative_Amount"]
    ].replace([float("inf"), -float("inf")], 0).fillna(0)

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42
    )

    predictions = model.fit_predict(features)

    expenses["Anomaly_Flag"] = predictions == -1
    expenses["Anomaly_Score"] = -model.decision_function(features)

    expenses["Review_Reason"] = expenses.apply(
    lambda row: (
        f"Amount is {row['Amount_to_Category_Median']:.1f} times "
        "the category median"
        if row["Amount_to_Category_Median"] >= 3
        else "Unusual pattern detected by Isolation Forest; review context"
    ) if row["Anomaly_Flag"] else "",
    axis=1
)

    return expenses.sort_values(
        ["Anomaly_Flag", "Anomaly_Score"],
        ascending=[False, False]
    )


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {INPUT_FILE}"
        )

    data = pd.read_csv(INPUT_FILE)
    results = detect_unusual_spending(data)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT_FILE, index=False)

    flagged = results[results["Anomaly_Flag"]]

    print("ANOMALY DETECTION COMPLETED")
    print("Expense transactions analyzed:", len(results))
    print("Potentially unusual transactions:", len(flagged))
    print("Results saved to:", OUTPUT_FILE)

    print("\nTop 10 transactions to review:")
    columns = [
        "Date", "Category", "Amount",
        "Anomaly_Score", "Review_Reason"
    ]
    print(flagged[columns].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
