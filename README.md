# Nectr × Instamart: First-Time Purchase Acquisition

**Project type:** Product Management + Applied ML  
**Status:** Product discovery, synthetic-data analysis, and experiment design

## Overview

How might a quick-commerce platform increase first-time purchases of a premium offering such as Nectr?

This project explores how historical purchasing behaviour could help identify users who are more likely to make their first Nectr purchase, and how those insights could inform product discovery, targeting, and experimentation.

The project combines synthetic data generation, exploratory analysis, propensity modelling, customer segmentation, product prioritisation, and an A/B testing proposal.

**Important:** All data and results in this project are synthetic. They do not represent actual Instamart customer behaviour or measured business performance.

## Problem Statement

Premium offerings can be difficult to discover within a broad quick-commerce catalogue. A product team needs to understand which users might be receptive to a first purchase and how to introduce relevant discovery experiences without unnecessarily disrupting the existing shopping experience.

The key product question is:

> Can a targeted discovery experience increase the first-time Nectr purchase rate among eligible users?

The analysis is exploratory. The proposed product intervention must be evaluated through a controlled experiment before claiming incremental impact.

## Analytical Approach

1. **Generate synthetic data:** Create users, orders, categories, and purchase histories.
2. **Define the eligible cohort:** Identify users without a historical Nectr purchase.
3. **Construct features:** Use historical behaviour to predict first-time purchases in a subsequent 30-day window.
4. **Evaluate models:** Compare Logistic Regression and Random Forest on a held-out test set.
5. **Explore segments:** Examine differences in order frequency, average order value, and premium-item share.
6. **Prioritise product options:** Use illustrative RICE assumptions to compare a personalised rail, a dedicated premium tab, and a standalone premium surface.
7. **Design an experiment:** Propose a controlled test with first-time Nectr purchase rate as the primary outcome.

## Key Findings

| Metric | Synthetic result |
|---|---:|
| Users generated | 6,000 |
| Cleaned orders | 24,834 |
| Eligible users | 5,793 |
| Future first-time Nectr buyers | 172 |
| Eligible-cohort 30-day conversion | 2.97% |
| Held-out test users | 1,449 |
| Held-out top-decile users | 145 |
| Top-decile conversion | 6.90% |
| Top-decile concentration vs. held-out baseline | 2.32× |

The synthetic eligible cohort has a 2.97% first-purchase rate over the defined future window. In the held-out test set, the highest-scored decile has a 6.90% conversion rate, approximately 2.32 times the test-set baseline.

This is **descriptive concentration, not causal lift**. It does not establish that targeting these users or launching a particular interface would increase purchases.

## Model Evaluation

Two baseline models were compared using a held-out test set.

| Metric | Logistic Regression | Random Forest |
|---|---:|---:|
| Precision at 0.5 threshold | 0.043 | 0.042 |
| Recall at 0.5 threshold | 0.535 | 0.465 |
| ROC-AUC | 0.617 | 0.613 |
| Average precision | 0.048 | 0.046 |

Logistic Regression performs slightly better on these synthetic results. Both models show modest predictive performance, so the findings should be treated as exploratory rather than production-ready targeting logic.

The ranking result motivates further investigation; it does not demonstrate that the model will generalise to real customers.

## Customer Segmentation

Clustering was used to explore differences in historical purchasing behaviour, including order frequency, average order value, and premium-item share.

The resulting groups are descriptive clusters, not validated customer personas. Similarity between some clusters also means that stronger claims about distinct customer types would be premature.

## Product Prioritisation

Three product options were considered:

- **Personalised premium rail:** Introduce a targeted discovery surface within the existing feed.
- **Dedicated premium tab:** Provide a distinct destination for premium offerings.
- **Standalone premium surface or app:** Build a more separate experience.

The RICE analysis uses illustrative assumptions for reach, impact, confidence, and effort. These values are not measured business inputs.

Under the current assumptions, the dedicated tab scores higher on raw RICE, while the personalised rail is recommended as a smaller, more reversible first experiment, subject to engineering feasibility.

This recommendation is a product hypothesis—not a proven winner. The assumptions should be validated with stakeholders and real product data.

## Proposed A/B Experiment

**Objective:** Test whether a personalised premium discovery rail increases first-time Nectr purchases among eligible users.

**Hypothesis:** Eligible users exposed to the targeted rail will have a higher first-time Nectr purchase rate than comparable users receiving the existing experience.

**Design:**

- **Population:** Eligible users with no historical Nectr purchase.
- **Control:** Existing discovery experience.
- **Treatment:** Existing experience with the proposed personalised rail.
- **Primary metric:** Difference in first-time Nectr purchase rate between treatment and control over the defined 30-day window.
- **Secondary metrics:** Discovery engagement, product-page visits, add-to-cart rate, and time to first purchase.
- **Guardrails:** Overall purchase conversion, cancellations, average order value, and other relevant business or customer-experience measures.

Before launch, the team should calculate sample size using a real baseline conversion rate, the minimum detectable effect, statistical power, and the planned experiment duration.

A positive result should be established through the experiment, not inferred from model scores or synthetic data.

## Repository Contents

- `generate_data.py` — Generates the synthetic dataset and analysis cohorts.
- `clustering_and_propensity.py` — Builds historical features, evaluates propensity models, and produces cluster summaries.
- `build_dashboard.py` — Generates the visual dashboard.
- `rice_scoring.py` — Calculates illustrative RICE scores and reports model results.
- `executive_summary.md` — Executive overview.
- `findings.md` — Analytical findings and limitations.
- `prd.md` — Product requirements and experiment proposal.
- `dashboard.png` — Visual summary of the analysis.
- `data/` — Generated datasets, model metrics, held-out scores, cluster summaries, and RICE outputs.

## Reproducibility

Run the following commands from the repository root in an environment with Python and the required packages installed:

```powershell
pip install pandas numpy scikit-learn matplotlib
python generate_data.py
python clustering_and_propensity.py
python build_dashboard.py
python rice_scoring.py
```

The scripts use repository-relative paths and regenerate the analysis outputs from the synthetic data.

## Limitations

- The dataset is synthetic and does not contain actual Instamart customer evidence.
- Predictive performance on synthetic data may not generalise to real customers.
- Top-decile concentration is not evidence of incremental treatment impact.
- Cluster descriptions are exploratory and are not validated personas.
- RICE inputs are assumptions rather than measured reach, confidence, impact, or effort.
- Real-world implementation requires production data, privacy and governance review, instrumentation, and controlled experimentation.

## Conclusion

This project demonstrates a product analytics workflow: translate a discovery problem into a measurable acquisition question, construct an eligible cohort, evaluate baseline propensity models, explore behavioural segments, compare product options, and design an experiment.

The central recommendation is to test targeted discovery as a reversible product hypothesis and measure incremental first-time purchases before committing to a larger product surface.

**The results are synthetic and should be presented as a demonstration of analytical and product decision-making—not as evidence of actual Instamart performance.**