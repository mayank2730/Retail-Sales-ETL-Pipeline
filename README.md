# Retail Sales ETL Pipeline

A Python-based ETL (Extract, Transform, Load) pipeline that processes retail sales data, validates data quality, stores cleaned records in a SQLite database, and generates analytical CSV reports.

## 🚀 Live Dashboard

[**Open Retail Sales ETL Dashboard**](https://retail-sales-etl-pipeline-hx9fssevyzmmzccjsuhaxz.streamlit.app/)




## Project Overview

This project demonstrates a complete data engineering workflow using a retail sales dataset containing 9,994 records and 21 columns.

The pipeline extracts data from a CSV file, cleans and validates the records, loads the processed data into SQLite, and generates reports to support business analysis.

## Key Features

- **Data Extraction:** Reads retail sales data from a CSV file using pandas.
- **Data Transformation:** Standardizes column names and data types, converts dates, and trims unnecessary whitespace.
- **Data Quality Validation:** Checks required columns, dates, unique row identifiers, quantities, sales values, discounts, shipping dates, and duplicate records.
- **Database Loading:** Stores validated records in a SQLite database.
- **SQL Analysis:** Analyzes sales and profit by category and region and identifies loss-making product subcategories.
- **Automated Reporting:** Generates CSV reports for category performance, regional performance, and loss-making subcategories.
- **Automated Testing:** Includes four unit tests covering extraction, transformation, invalid quantities, and database loading.
- **Logging:** Records pipeline progress and data quality summaries.

## Technologies Used

- Python
- pandas
- SQLite
- SQL
- unittest
- Git and GitHub

## Project Structure

```text
Retail-Sales-ETL-Pipeline/
│
├── data/
│   ├── retail_sales.csv
│   ├── retail_sales.db
│   └── reports/
│       ├── category_report.csv
│       ├── region_report.csv
│       └── loss_making_subcategories.csv
│
├── src/
│   ├── pipeline.py
│   ├── inspect_data.py
│   └── generate_reports.py
│
├── sql/
│   └── analysis.sql
│
├── tests/
│   └── test_pipeline.py
│
├── logs/
│   └── pipeline.log
│
├── run_project.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ETL Workflow

1. **Extract:** Load retail sales records from the source CSV.
2. **Transform:** Clean fields, convert data types, and validate business rules.
3. **Load:** Store the validated records in SQLite.
4. **Analyze:** Execute SQL queries to understand sales and profitability.
5. **Report:** Export category, region, and loss-making subcategory summaries to CSV.
6. **Test:** Run automated tests to verify important pipeline functions.

## Data Quality Checks

The pipeline validates:

- Required columns are present.
- Order and ship dates are valid.
- Row IDs are unique and present.
- Quantities are positive.
- Sales values are non-negative.
- Discounts fall between 0 and 1.
- Ship dates do not precede order dates.
- Exact duplicate records are rejected.

The current dataset contains **9,994 records and 21 columns**. Initial inspection found no missing values, duplicate rows, or invalid values in the checked fields.

## Business Insights

The SQL analysis identifies:

- Sales and profit by product category.
- Sales and profit by geographical region.
- Product subcategories generating negative profit.

The generated reports help identify stronger-performing categories and regions, as well as subcategories that may require further business investigation.

## Installation and Setup

### 1. Clone the repository

```bash
git clone <https://github.com/mayank2730/Retail-Sales-ETL-Pipeline>
cd Retail-Sales-ETL-Pipeline
```



### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the complete workflow

```bash
python run_project.py
```

The workflow runs the ETL pipeline and generates the analytical CSV reports.

### 5. Run automated tests

```bash
python -m unittest discover -s tests -v
```

## Expected Results

- 9,994 records extracted, validated, and loaded.
- SQLite database created or refreshed.
- Three analytical CSV reports generated.
- Four automated tests passing.

These results reflect the current local project run and test results.

## Future Improvements

- Add scheduled pipeline execution.
- Introduce configurable data quality thresholds.
