\# Instamart × Nectr — Executive Summary



\## The Question



How should Instamart introduce Nectr, its premium grocery proposition: through the existing app, a dedicated tab, or a standalone experience? And can historical shopping behaviour help prioritize first-time buyers?



\## What We Found



We built a synthetic dataset of 6,000 users and 24,834 cleaned orders to explore first-time Nectr purchase prediction.



The analysis excluded users with prior Nectr purchases and used historical shopping behaviour to predict first-time purchases in a subsequent 30-day window.



\- \*\*Eligible first-purchase cohort:\*\* 5,793 users

\- \*\*Future first-time Nectr buyers:\*\* 172

\- \*\*Simulated 30-day purchase rate:\*\* 2.97%

\- \*\*Held-out test set:\*\* 1,449 users

\- \*\*Highest-scored decile conversion:\*\* 6.90%, compared with a 2.97% test-set baseline

\- \*\*Top-decile concentration:\*\* 2.32× the baseline rate in one synthetic test split



Logistic Regression performed slightly better than Random Forest on overall held-out metrics (ROC-AUC 0.617 versus 0.613; average precision 0.0476 versus 0.0456). Both models achieved the same top-decile conversion of 6.90% in the current test split. These results suggest a preliminary ranking signal, not causal lift or production-ready targeting performance.



\*\*Important:\*\* All data, users, orders, and outcomes are synthetic. These results do not represent actual Instamart or Nectr business performance.



\## The Decision



\*\*Test a personalized “Premium for You” rail before committing to a dedicated tab or standalone app.\*\*



A rail is a smaller, more reversible product hypothesis that can be tested within the existing shopping experience. The recommendation is based on the value of learning before making a larger investment—not on proof that the rail will perform better.



The initial RICE comparison favours a dedicated tab under its illustrative assumptions (716 versus 612 for the rail). We would still test the rail first because it offers a smaller, more reversible intervention. The relative effort, feasibility, and risks should be validated with stakeholders before implementation.



This is a sequencing decision, not a claim that the rail is the highest-scoring option or that the model has demonstrated causal impact. The next step is to validate feasibility and test the rail against the existing experience using a properly powered randomized experiment.



\## What Happens Next



1\. \*\*Validate feasibility:\*\* Confirm eligibility rules, instrumentation, and the availability of reliable first-time purchase data.

2\. \*\*Prepare the experiment:\*\* Randomize eligible users into treatment (rail) and control (existing experience). Calculate sample size and experiment duration using a real baseline conversion rate, traffic availability, and a commercially meaningful minimum detectable effect.

3\. \*\*Measure impact:\*\* Use the treatment-control difference in first-time Nectr purchase rate over a predefined 30-day outcome window as the primary metric. Monitor overall order conversion, cancellations, average order value, and app performance as guardrails.

4\. \*\*Make the rollout decision:\*\* Expand only if results provide credible evidence of incremental improvement without unacceptable guardrail deterioration.



\## What We're Being Upfront About



\- All data, customer behaviour, and outcomes in this project are synthetic—not actual Instamart or Nectr results.

\- The 2.32× concentration is an observed ranking result in one held-out synthetic split. It is not causal lift and does not establish that the rail will increase purchases.

\- Model discrimination is modest, and the small difference between Logistic Regression and Random Forest should not be overstated.

\- The clusters describe synthetic shopping patterns, not validated customer personas.

\- RICE scores are illustrative planning assumptions, not measured business outcomes.



\## The One-Line Takeaway



\*\*Use synthetic analysis to form a targeting hypothesis, then use a properly powered randomized experiment with real product data to establish whether targeted Nectr discovery drives incremental first-time purchases.\*\*

