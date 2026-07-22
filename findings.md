# Instamart Nectr — Clustering & Propensity Findings

## Dataset
6,000 synthetic users, 5,731 with order history. Premium adoption defined on a held-out future 30-day window (no leakage — features built only from prior history).

## Clustering (K-means, k=4)

| Cluster | Users | Avg Orders | Avg Order Value | Premium Item Share | Persona |
|---|---|---|---|---|---|
| 0 | 1,848 | 2.74 | ₹416 | 3% | Value Shopper |
| 1 | 836 | 3.18 | ₹1,143 | 46% | **Premium Explorer / Health-Conscious** |
| 2 | 1,566 | 5.98 | ₹572 | 14% | Occasional Premium Explorer |
| 3 | 1,481 | 2.50 | ₹412 | 2% | Value Shopper |

**Silhouette score at k=4: 0.315** (k=2 actually scores higher at 0.359, but collapses to just "premium vs. not," which is too coarse to act on — 4 personas is the better trade-off between statistical cleanliness and product usefulness).

## One honest limitation — clusters 0 and 3 aren't really distinct

Both got labeled "Value Shopper" by the labeling logic — their order count, order value, and premium share are nearly identical (2.74 vs 2.50 orders; ₹416 vs ₹412 AOV). This is the exact limitation flagged in the original spec ("K-means becomes difficult to interpret meaningfully beyond a certain point") — it just showed up at k=4 itself, not beyond it. With richer real behavioral data (session recordings, search queries), these two would likely separate on a dimension this synthetic dataset can't simulate. **Practical read: treat this as effectively 3 meaningful personas, not 4** — Value Shopper, Occasional Premium Explorer, Premium Explorer/Health-Conscious.

## Propensity Model

| Model | Precision | Recall | ROC-AUC |
|---|---|---|---|
| Logistic Regression | 0.141 | 0.563 | 0.594 |
| Random Forest | 0.162 | 0.405 | 0.588 |

Both models are modest (ROC-AUC ~0.59) — honestly reflects that only 5 behavioral features are available in this synthetic dataset. A real deployment would add search queries, category dwell time, and push-notification response, which would likely lift this meaningfully.

**Top feature by importance:** `avg_order_value` (0.36), followed by `premium_item_share` (0.22) — consistent with intuition: past spend and past premium behavior are the strongest predictors of future premium behavior.

## The headline number (resume bullet material)

- **Overall premium adoption rate:** 11.0% of active users
- **Premium adoption rate in the top 10% propensity segment:** 30.5%
- **Concentration: 2.8x** — the model concentrates premium buyers into a segment nearly 3x denser than the base rate, using less than a third of the recall a production system would ideally want, which itself is an honest caveat on how confidently to act on this number yet

## What this means for the product decision

Targeting the top-decile segment (574 users, 10% of the active base) for the "Premium for You" rail means Instamart could reach roughly 3x the premium-buyer density of a random/blanket rollout — directly supporting the earlier recommendation to launch the personalized rail to a targeted segment first, rather than showing it to everyone.

## Status
- [x] Synthetic dataset generated and corrected (premium-order rate fixed from unrealistic 78% to realistic 17%)
- [x] K-means clustering run, k=4 selected with honest limitation noted
- [x] Propensity model built (Logistic Regression + Random Forest)
- [x] Headline number established: 2.8x concentration in top-decile segment
- [ ] Next: RICE scoring with real numbers, PRD, dashboard
