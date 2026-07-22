# Instamart Nectr — Executive Summary

## The Question
Should Instamart's premium grocery line (Nectr) integrate into the existing app, get its own tab, or become a standalone surface — and who should see it first?

## What We Found
Not all Instamart users are equally likely to buy premium groceries. Using purchase history (order frequency, average order value, and past premium purchases), we built a model that identifies the 10% of users most likely to buy premium in the next 30 days. That segment converts to premium purchases at **2.8x the rate of the average user** (30.5% vs. 11.0%).

Three user personas emerged from the data:
- **Value Shoppers (58%)** — frequent, low-spend, almost never buy premium
- **Occasional Premium Explorers (27%)** — moderate spenders who dabble in premium
- **Premium Explorers/Health-Conscious (15%)** — high AOV, consistently choose organic/imported — the closest match to a FirstClub-style buyer

## The Decision
Launch a personalized "Premium for You" rail — visible only to the top 10% propensity segment — rather than a broad tab or a separate app.

**This overrides the raw RICE prioritization score**, which technically favored a dedicated tab shown to all users (716 vs. 612). We recommend against following that number as-is: a tab shown broadly mostly reaches Value Shoppers, who show almost no premium interest (~2% of their purchases), and testing it broadly before validating anything carries real brand-dilution risk with no real data yet to justify it. The targeted rail costs less (1.5 months vs. 4), carries higher confidence because it's grounded in an actual measured number rather than an assumption, and produces real evidence to justify a broader rollout later — if it's warranted.

## What Happens Next
1. **Month 1:** A/B test the rail against a control group within the top-decile segment (287 users each side); track premium conversion as the success metric, and core order completion + session time as guardrails against cannibalization and slowdown.
2. **Month 2:** If it works, begin a distinct visual/brand treatment to address Design's concern that premium blends too much into Instamart's fast-and-cheap visual identity.
3. **Month 3:** Use real conversion data — not assumptions — to decide whether to expand toward a broader surface.

## What We're Being Upfront About
- The clustering technically produced 4 segments, but two came out nearly identical — realistically, this is 3 meaningful personas, not 4. Richer real-world data would likely separate them further.
- The propensity model's predictive strength is modest (ROC-AUC ~0.59) given only 5 behavioral signals were available in this synthetic dataset — a production model with real search and session data would likely perform meaningfully better.
- This entire analysis runs on a synthetic dataset built to simulate realistic behavior, not actual Instamart data.

## The One-Line Takeaway
Don't guess who wants premium groceries — the data already shows a specific 10% of users convert at nearly 3x the average rate. Reach them first, prove it works, then decide whether to go broader.
