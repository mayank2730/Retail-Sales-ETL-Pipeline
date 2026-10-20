
import pandas as pd
from pathlib import Path

# Find the project folder automatically
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Define the dataset location
DATA_FILE = PROJECT_DIR / "data" / "retail_sales.csv"


def inspect_dataset():
    # Load the raw CSV file
    df = pd.read_csv(DATA_FILE, encoding="cp1252")

    print("\n--- DATASET SHAPE ---")
    print(df.shape)

    print("\n--- FIRST 5 ROWS ---")
    print(df.head())

    print("\n--- COLUMN NAMES ---")
    print(df.columns.tolist())

    print("\n--- DATA TYPES ---")
    print(df.dtypes)

    print("\n--- MISSING VALUES ---")
    print(df.isnull().sum())

    print("\n--- DUPLICATE ROWS ---")
    print(df.duplicated().sum())

    # Check whether Row ID values are unique
    print("\n--- DUPLICATE ROW IDs ---")
    print(df["Row ID"].duplicated().sum())

    # Convert dates temporarily for validation
    order_dates = pd.to_datetime(
        df["Order Date"], format="mixed", errors="coerce"
    )
    ship_dates = pd.to_datetime(
        df["Ship Date"], format="mixed", errors="coerce"
    )

    print("\n--- INVALID ORDER DATES ---")
    print(order_dates.isna().sum())

    print("\n--- INVALID SHIP DATES ---")
    print(ship_dates.isna().sum())

    print("\n--- SHIP DATE BEFORE ORDER DATE ---")
    print((ship_dates < order_dates).sum())

    # Check numeric business rules
    print("\n--- NON-POSITIVE QUANTITIES ---")
    print((df["Quantity"] <= 0).sum())

    print("\n--- NEGATIVE SALES ---")
    print((df["Sales"] < 0).sum())

    print("\n--- DISCOUNTS OUTSIDE 0 TO 1 ---")
    print(((df["Discount"] < 0) | (df["Discount"] > 1)).sum())


if __name__ == "__main__":
    inspect_dataset()
