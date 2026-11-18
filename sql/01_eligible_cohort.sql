-- Eligible first-purchase cohort and 30-day first-time Nectr conversion.
-- Feature window: orders before 2026-05-31 (cutoff).
-- Outcome window: 2026-05-31 to 2026-06-30 (30 days).
-- Runs in DuckDB from the repository root: duckdb < sql/01_eligible_cohort.sql

WITH orders AS (
    SELECT *, CAST(order_date AS DATE) AS order_dt
    FROM read_csv_auto('data/fact_orders.csv')
),
users AS (
    SELECT user_id FROM read_csv_auto('data/dim_users.csv')
),
prior_buyers AS (            -- bought Nectr before the cutoff: excluded
    SELECT DISTINCT user_id
    FROM orders
    WHERE order_dt < DATE '2026-05-31' AND nectr_purchase = 1
),
eligible AS (                -- never bought Nectr before the cutoff
    SELECT u.user_id
    FROM users u
    LEFT JOIN prior_buyers p USING (user_id)
    WHERE p.user_id IS NULL
),
first_buyers AS (            -- eligible users who bought Nectr in the outcome window
    SELECT DISTINCT o.user_id
    FROM orders o
    JOIN eligible e USING (user_id)
    WHERE o.order_dt >= DATE '2026-05-31'
      AND o.order_dt <  DATE '2026-06-30'
      AND o.nectr_purchase = 1
)
SELECT
    (SELECT COUNT(*) FROM users)        AS total_users,
    (SELECT COUNT(*) FROM orders)       AS cleaned_orders,
    (SELECT COUNT(*) FROM prior_buyers) AS prior_nectr_buyers,
    (SELECT COUNT(*) FROM eligible)     AS eligible_users,
    (SELECT COUNT(*) FROM first_buyers) AS future_first_buyers,
    ROUND(100.0 * (SELECT COUNT(*) FROM first_buyers)
                / (SELECT COUNT(*) FROM eligible), 2) AS conversion_pct;
