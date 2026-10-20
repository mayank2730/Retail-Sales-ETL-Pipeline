
import sqlite3
from pathlib import Path

import pandas as pd

# Find the main project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Database and report locations
DATABASE_FILE = PROJECT_DIR / "data" / "retail_sales.db"
REPORTS_DIR = PROJECT_DIR / "data" / "reports"

# Create the reports folder if it does not exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_reports():
    """Generate business analysis reports from SQLite."""

    # Connect to the existing database
    with sqlite3.connect(DATABASE_FILE) as connection:

        # Report 1: Sales and profit by category
        category_report = pd.read_sql_query(
            """
            SELECT
                Category,
                ROUND(SUM(Sales), 2) AS total_sales,
                ROUND(SUM(Profit), 2) AS total_profit
            FROM retail_sales
            GROUP BY Category
            ORDER BY total_profit DESC
            """,
            connection,
        )

        # Report 2: Sales and profit by region
        region_report = pd.read_sql_query(
            """
            SELECT
                Region,
                ROUND(SUM(Sales), 2) AS total_sales,
                ROUND(SUM(Profit), 2) AS total_profit
            FROM retail_sales
            GROUP BY Region
            ORDER BY total_sales DESC
            """,
            connection,
        )

        # Report 3: Loss-making product subcategories
        loss_report = pd.read_sql_query(
            """
            SELECT
                "Sub-Category",
                ROUND(SUM(Profit), 2) AS total_profit
            FROM retail_sales
            GROUP BY "Sub-Category"
            HAVING SUM(Profit) < 0
            ORDER BY total_profit ASC
            """,
            connection,
        )

    # Save each report as a CSV file
    category_report.to_csv(
        REPORTS_DIR / "category_report.csv", index=False
    )
    region_report.to_csv(
        REPORTS_DIR / "region_report.csv", index=False
    )
    loss_report.to_csv(
        REPORTS_DIR / "loss_making_subcategories.csv", index=False
    )

    print("Reports generated successfully!")
    print(f"Reports saved to: {REPORTS_DIR}")
    print(f"Category report rows: {len(category_report)}")
    print(f"Region report rows: {len(region_report)}")
    print(f"Loss-making subcategories: {len(loss_report)}")


if __name__ == "__main__":
    generate_reports()

