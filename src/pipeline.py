
import logging
import sqlite3
from pathlib import Path

import pandas as pd

# Find the project folder automatically
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Define input, database, and log locations
DATA_FILE = PROJECT_DIR / "data" / "retail_sales.csv"
DATABASE_FILE = PROJECT_DIR / "data" / "retail_sales.db"
LOG_FILE = PROJECT_DIR / "logs" / "pipeline.log"

# Create the logging folder if it does not exist
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configure pipeline logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)


def extract_data():
    """Read the raw retail CSV file."""
    logging.info("Starting data extraction")

    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE, encoding="cp1252")

    if df.empty:
        raise ValueError("The source dataset is empty")

    logging.info("Extracted %s rows", len(df))
    return df


def transform_data(df):
    """Clean and standardize the dataset."""
    logging.info("Starting data transformation")

    df = df.copy()

    # Check that all expected columns exist
    required_columns = [
        "Row ID", "Order ID", "Order Date", "Ship Date",
        "Ship Mode", "Customer ID", "Customer Name",
        "Segment", "Country", "City", "State", "Postal Code",
        "Region", "Product ID", "Category", "Sub-Category",
        "Product Name", "Sales", "Quantity", "Discount", "Profit",
    ]

    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Required columns are missing: {sorted(missing_columns)}"
        )

    # Keep only the expected columns in a consistent order
    df = df[required_columns]

    # Convert date columns into actual datetime values
    df["Order Date"] = pd.to_datetime(
        df["Order Date"], format="mixed", errors="coerce"
    )
    df["Ship Date"] = pd.to_datetime(
        df["Ship Date"], format="mixed", errors="coerce"
    )

    # Store postal codes as text rather than quantities
    df["Postal Code"] = df["Postal Code"].astype("string")

    # Remove leading and trailing whitespace from text columns
    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        df[column] = df[column].str.strip()

    # Reject invalid dates
    if df["Order Date"].isna().any():
        raise ValueError("Invalid or missing order dates detected")

    if df["Ship Date"].isna().any():
        raise ValueError("Invalid or missing ship dates detected")

    # Validate row identifiers
    if df["Row ID"].isna().any() or df["Row ID"].duplicated().any():
        raise ValueError("Row ID values must be present and unique")

    # Validate quantities, sales, discounts, and shipping dates
    if (df["Quantity"] <= 0).any():
        raise ValueError("Non-positive quantities detected")

    if (df["Sales"] < 0).any():
        raise ValueError("Negative sales values detected")

    if not df["Discount"].between(0, 1).all():
        raise ValueError("Discounts outside the range 0 to 1 detected")

    if (df["Ship Date"] < df["Order Date"]).any():
        raise ValueError("Ship dates before order dates detected")

    if df.duplicated().any():
        raise ValueError("Exact duplicate rows detected")

    
    # Record a summary of the data quality checks
    logging.info(
        "Data quality summary | Rows validated: %s | "
        "Columns: %s | Missing values: %s | "
        "Duplicate rows: %s",
        len(df),
        len(df.columns),
        int(df.isna().sum().sum()),
        int(df.duplicated().sum()),
    )

    logging.info("Transformation and validation completed")
    return df




def load_data(df):
    """Load validated records into SQLite."""
    logging.info("Starting database load")

    connection = sqlite3.connect(DATABASE_FILE)

    try:
        with connection:
            df.to_sql(
                "retail_sales",
                connection,
                if_exists="replace",
                index=False,
            )

            # Confirm the number of records stored in the database
            stored_rows = pd.read_sql_query(
                "SELECT COUNT(*) AS row_count FROM retail_sales",
                connection,
            ).iloc[0]["row_count"]

        if stored_rows != len(df):
            raise ValueError(
                f"Row count mismatch: expected {len(df)}, "
                f"stored {stored_rows}"
            )

        logging.info("Loaded %s rows into SQLite", stored_rows)
        return stored_rows

    finally:
        # Always close the connection, even if an error occurs
        connection.close()


def run_pipeline():
    """Run the complete ETL process."""
    logging.info("ETL pipeline started")

    raw_data = extract_data()
    clean_data = transform_data(raw_data)
    loaded_rows = load_data(clean_data)

    print("ETL pipeline completed successfully!")
    print(f"Raw rows extracted: {len(raw_data)}")
    print(f"Rows validated: {len(clean_data)}")
    print(f"Rows loaded into SQLite: {loaded_rows}")
    print(f"Database location: {DATABASE_FILE}")

    logging.info("ETL pipeline completed successfully")


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception:
        logging.exception("ETL pipeline failed")
        raise
