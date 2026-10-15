# Nectr × Instamart: First-Time Purchase Acquisition Analysis

> **Data disclosure:** This project uses synthetic data generated for portfolio analysis. All customer behaviour, orders, conversion rates, model metrics, and business implications are simulated. They are not actual Instamart or Nectr results.

## 1. Product question

How might Instamart identify eligible customers who are more likely to make their first Nectr purchase, and how should the team test a targeted discovery experience?

The analysis explores historical shopping behaviour as a potential targeting signal. It does not establish that targeting causes incremental purchases.

## 2. Dataset and methodology

The synthetic dataset contains 6,000 users and 24,834 cleaned orders.

| Dataset measure | Result |
|---|---:|
| Synthetic users | 6,000 |
| Cleaned orders | 24,834 |
| Historical orders used for features | 13,412 |
| Future-window orders | 11,422 |
| Users with a prior Nectr purchase | 207 |
| Eligible first-purchase cohort | 5,793 |
| Future first-time Nectr buyers | 172 |
| Future-window conversion among eligible users | 2.97% |

The analysis separates historical behaviour from a subsequent 30-day outcome window. Users with a prior Nectr purchase are excluded from the first-purchase acquisition cohort.

Features are derived from historical orders, including order frequency, average order value, premium-item share, total items, evening-order share, and tier-1 location status.

## 3. Predictive model comparison

Logistic Regression and Random Forest were evaluated on a held-out test set.

| Metric | Logistic Regression | Random Forest |
|---|---:|---:|
| ROC-AUC | 0.617 | 0.613 |
| Average precision | 0.0476 | 0.0456 |
| Precision at 0.5 threshold | 4.34% | 4.21% |
| Recall at 0.5 threshold | 53.5% | 46.5% |

Logistic Regression performs slightly better across the reported metrics and is the simpler model to interpret. However, both models show modest discrimination, and precision at the default 0.5 threshold is low.

**Decision:**  Retain Logistic Regression as the preferred exploratory baseline because it performs slightly better on ROC-AUC and average precision and is easier to interpret. However, both models achieve the same top-decile conversion in this test split. Neither model is production-ready, and the results do not establish reliable targeting performance on real customers.
## 4. Top-decile targeting hypothesis

The held-out test set contains 1,449 eligible users.

| Measure | Result |
|---|---:|
| Test-set baseline conversion | 2.97% |
| Conversion among highest-scored decile | 6.90% |
| Top-decile concentration versus baseline | 2.32× |
| Users in the top decile | 145 |

The highest-scored decile has a higher observed first-time purchase rate than the overall held-out test cohort.

This is a **ranking signal in one synthetic test split**, not evidence of incremental impact. It does not establish that a personalized rail, recommendation, or promotion will cause additional Nectr purchases. The result may also vary across random splits and synthetic-data assumptions.

## 5. Descriptive customer segments

A four-cluster K-Means analysis of historical shopping behaviour produced the following descriptive groups:

| Cluster | Users | Average orders | Average order value | Premium-item share |
|---|---:|---:|---:|---:|
| 0 | 1,243 | 5.30 | ₹542 | 11.4% |
| 1 | 604 | 2.67 | ₹1,223 | 50.0% |
| 2 | 1,053 | 2.02 | ₹412 | 3.0% |
| 3 | 1,491 | 2.07 | ₹411 | 2.3% |

These clusters describe shopping patterns in the synthetic dataset. They should not be interpreted as validated customer personas or proof of Nectr affinity. Clusters 2 and 3 appear similar on the displayed measures.

## 6. Product implications

1. **Test targeted discovery before building a dedicated destination.** A personalized rail is a reasonable first experiment because it is a smaller, more reversible product intervention than a dedicated premium destination. Although the dedicated tab has a higher illustrative RICE score, the rail is the proposed first test—not a proven winner. The choice should be validated against engineering feasibility and real product data.2. **Use first-time Nectr purchase as the primary outcome.** Add-to-cart and click-through rates can diagnose the funnel, but do not establish purchase conversion.
3. **Evaluate incrementality with a control group.** Compare eligible users randomly assigned to treatment and control.
4. **Monitor guardrails.** Track overall order conversion, cancellations, average order value, and user experience to detect potential harm to core shopping.
5. **Avoid over-personalization claims.** The model is exploratory and the underlying data is synthetic.

## 7. Proposed experiment

Randomly assign eligible users who have never purchased Nectr to a treatment group receiving a targeted Nectr discovery rail and a control group receiving the existing experience.

- **Primary metric:** Difference in first-time Nectr purchase rate between treatment and control over a predefined 30-day window.
- **Secondary metrics:** Nectr product-page visits, add-to-cart rate, and checkout completion.
- **Guardrails:** Overall Instamart order conversion, cancellations, average order value, and customer complaints.
- **Analysis:** Report treatment and control rates, absolute percentage-point lift, relative lift, confidence intervals, and sample size.
- **Decision rule:** Scale only if the experiment shows a credible incremental improvement without unacceptable guardrail deterioration.

The required sample size and experiment duration must be determined using the real baseline conversion, minimum detectable effect, and traffic availability. The synthetic dataset is not sufficient to establish these values.

## 8. Limitations

- All data is synthetic; the findings are not evidence of actual customer behaviour.
- The results come from one train/test split and may vary with other splits or assumptions.
- Model performance is modest, particularly at the default classification threshold.
- The top-decile comparison is observational within the held-out synthetic cohort, not a randomized experiment.
- The analysis does not establish the effectiveness of any specific interface, promotion, or recommendation strategy.

## Conclusion

The analysis demonstrates an end-to-end approach to defining a first-purchase cohort, constructing historical behavioural features, comparing simple predictive models, and developing a testable product hypothesis.

The next meaningful validation step is a controlled experiment using real, appropriately governed product data—not deployment of the model based on these synthetic results.