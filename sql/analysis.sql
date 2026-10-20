
-- 1. Check the total number of records
SELECT COUNT(*) AS total_records
FROM retail_sales;

-- 2. Calculate overall sales, profit, and quantity
SELECT
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    SUM(Quantity) AS total_quantity
FROM retail_sales;

-- 3. Analyze sales and profit by category
SELECT
    Category,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit
FROM retail_sales
GROUP BY Category
ORDER BY total_profit DESC;

-- 4. Analyze performance by region
SELECT
    Region,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit
FROM retail_sales
GROUP BY Region
ORDER BY total_sales DESC;

-- 5. Find loss-making product subcategories
SELECT
    "Sub-Category",
    ROUND(SUM(Profit), 2) AS total_profit
FROM retail_sales
GROUP BY "Sub-Category"
HAVING SUM(Profit) < 0
ORDER BY total_profit ASC;
