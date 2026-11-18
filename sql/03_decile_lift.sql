-- Conversion by propensity-score decile on the held-out test set.
-- Decile 1 = highest scores. Lift = decile conversion / overall conversion.

WITH scored AS (
    SELECT
        user_id,
        actual_first_nectr_purchase AS converted,
        NTILE(10) OVER (ORDER BY score_rank) AS decile
    FROM read_csv_auto('data/heldout_first_nectr_scores.csv')
),
base AS (
    SELECT AVG(converted) AS base_rate FROM scored
)
SELECT
    decile,
    COUNT(*)                                   AS users,
    SUM(converted)                             AS buyers,
    ROUND(100.0 * AVG(converted), 2)           AS conversion_pct,
    ROUND(AVG(converted) / MAX(base_rate), 2)  AS lift_vs_base
FROM scored, base
GROUP BY decile
ORDER BY decile;
