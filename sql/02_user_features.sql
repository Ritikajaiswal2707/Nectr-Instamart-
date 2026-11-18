-- Behavioural features per eligible user, built from pre-cutoff orders only
-- (no leakage from the outcome window). Mirrors clustering_and_propensity.py.

WITH history AS (
    SELECT *
    FROM read_csv_auto('data/orders_history.csv')
    WHERE order_value > 0
),
eligible AS (
    SELECT user_id FROM read_csv_auto('data/eligible_first_nectr_cohort.csv')
),
agg AS (
    SELECT
        user_id,
        COUNT(*)                                              AS order_count,
        AVG(order_value)                                      AS avg_order_value,
        SUM(premium_item_count)                               AS total_premium_items,
        SUM(item_count)                                       AS total_items,
        AVG(CASE WHEN time_of_day = 'evening' THEN 1 ELSE 0 END) AS evening_order_share
    FROM history
    GROUP BY user_id
)
SELECT
    e.user_id,
    COALESCE(a.order_count, 0)                                AS order_count,
    COALESCE(a.avg_order_value, 0)                            AS avg_order_value,
    COALESCE(a.total_items, 0)                                AS total_items,
    COALESCE(a.total_premium_items * 1.0
             / NULLIF(a.total_items, 0), 0)                   AS premium_item_share,
    COALESCE(a.evening_order_share, 0)                        AS evening_order_share,
    CASE WHEN u.city_tier = 'tier_1' THEN 1 ELSE 0 END        AS is_tier_1
FROM eligible e
LEFT JOIN agg a USING (user_id)
LEFT JOIN read_csv_auto('data/dim_users.csv') u USING (user_id)
ORDER BY e.user_id;
