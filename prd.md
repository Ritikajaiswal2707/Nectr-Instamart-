# Instamart Nectr — Product Requirements Document

## 1. Objective
Determine which product surface (personalized rail, dedicated tab, or standalone app) should carry Instamart's premium grocery (Nectr) rollout, and target it using a validated propensity model rather than a blanket launch.

## 2. Background
Instamart is testing Nectr while Zepto's Harvest Store and FirstClub demonstrate real premium demand. Clustering and propensity modeling on 5,731 active users found:
- Premium adoption concentrates **2.8x** in the top-decile propensity segment (30.5% vs. 11.0% base rate)
- Three meaningful personas exist: Value Shopper (58%), Occasional Premium Explorer (27%), Premium Explorer/Health-Conscious (15%)

## 3. RICE Scoring Results — and why we don't just follow them blindly

| Option | Reach | Impact | Confidence | Effort | RICE Score |
|---|---|---|---|---|---|
| B: Dedicated tab (all users) | 5,731 | 1 | 50% | 4.0mo | **716** |
| A: Personalized rail (top-decile) | 574 | 2 | 80% | 1.5mo | 612 |
| C: Standalone app | 859 | 3 | 30% | 9.0mo | 86 |

**The raw score favors Option B — but we recommend Option A first anyway.** This is a deliberate override, not an oversight, for three reasons:

1. **RICE's reach term rewards breadth even when most of that reach is low-relevance.** 58% of Instamart's active users are Value Shoppers with ~2% premium purchase share — showing them a premium tab mostly adds visual clutter to a fast-delivery experience, which is the exact brand-dilution risk Design flagged.
2. **Confidence is not symmetric with reach.** Option A's 80% confidence is grounded in an actual measured number (2.8x concentration); Option B's 50% is a guess about how a broad audience will respond to something never tested at this scale. RICE treats both as comparable percentages, but they carry very different risk.
3. **Effort compounds risk, not just cost.** Option B takes 4 months to ship before any real signal comes back. Option A takes 1.5 months and produces real conversion data that de-risks a *future* Option B decision.

**Recommendation: launch Option A first. If it validates (premium conversion up, guardrails hold), expand toward Option B with real evidence instead of a RICE score built on assumptions.**

## 4. User Stories

- *As a user in the top-decile propensity segment, I want to see premium/curated options relevant to my past purchases, so that I don't have to actively search for quality I already care about.*
  - **Acceptance criteria:** rail appears only for users scoring above the propensity threshold (top 10%); does not appear in a user's first 3 sessions (insufficient data to score them yet); rail is dismissible without penalizing future recommendation eligibility.

- *As a Value Shopper (58% of the user base), I want my core fast-delivery experience completely unaffected by the premium rollout, so that speed isn't compromised for a feature I won't use.*
  - **Acceptance criteria:** browse-to-cart latency unchanged; premium rail never appears above the fold for users below the propensity threshold; no premium-related push notifications sent to this segment during the pilot.

- *As an Instamart Product Manager, I want to see daily conversion and guardrail metrics for the pilot segment, so that I can catch a negative signal early rather than at the end of the pilot window.*
  - **Acceptance criteria:** dashboard refreshes daily; guardrail metrics (session time, core order completion rate) are visible on the same view as the success metric, not a separate report.

## 5. A/B Test Design

- **Hypothesis:** Showing a personalized "Premium for You" rail to users in the top-decile propensity segment increases premium item add-to-cart rate versus no rail.
- **Success metric:** premium item add-to-cart rate among the treatment group (top-decile segment).
- **Guardrail metrics:** overall app session time (premium rail shouldn't slow core browsing); core (non-premium) order completion rate (rail shouldn't cannibalize standard orders).
- **Sample size:** treatment group = the 574-user top-decile segment; split 50/50 treatment/control within this segment (287 each) rather than testing against the full 5,731-user base, since the effect is expected specifically in this segment.
- **Duration:** minimum 3 weeks, to capture at least 2-3 order cycles per user given this segment's order frequency.
- **Risk:** cannibalization — a user who would've bought a standard item switches to a premium item instead of making a genuinely incremental purchase. Tracked via the core order completion guardrail metric.

## 6. Stakeholder Communication

- **Engineering** wants the lowest-effort integration — Option A reuses existing home-feed infrastructure, no new surface to build or maintain.
- **Design/Brand** worries a rail blends premium into the same fast-and-cheap visual language that defines core Instamart, diluting the premium feel.
- **Finance** wants proof of incremental revenue, not cannibalized standard orders — this is exactly what the guardrail metric in the A/B test is built to catch.
- **Product recommendation:** start with Option A (satisfies Engineering, gets real data fast, keeps Finance's cannibalization concern testable), but commit to a distinct visual treatment (badge/color system) in the same rollout to partially address Design's concern without the cost of a fully separate surface.

## 7. Business Decision

- **Decision:** Launch a personalized "Premium for You" rail, targeted only at the top-decile propensity segment (574 users) — not a dedicated tab or standalone app.
- **Why:** Highest confidence (grounded in measured 2.8x concentration), lowest effort (1.5 months), and produces real data to de-risk a future broader rollout — even though the raw RICE score technically favors the broader tab option.
- **Risks:** Cannibalization of standard orders; brand dilution if premium doesn't feel meaningfully differentiated within the same visual system; small sample size (574 users) limits statistical power for subtle effects.
- **Next experiment:** If the rail succeeds, test a distinct visual treatment before expanding toward Option B (dedicated tab) with actual conversion evidence in hand.

## 8. 30-60-90 Day Execution Plan

- **Week 1-2:** Instrument the event schema (`viewed_premium_item`, `added_to_cart`, `payment_success`) in staging; finalize the propensity scoring pipeline for daily re-scoring of active users.
- **Month 1:** Launch the A/B test to the top-decile segment (287 treatment / 287 control); monitor guardrail metrics daily.
- **Month 2:** Evaluate results at the 3-week mark; if successful, begin design work on the distinct visual treatment (badge/color system) while continuing to monitor the live rail.
- **Month 3:** Decide on expansion — either broaden the propensity threshold (e.g., top 20% instead of top 10%) or begin scoping Option B with real conversion data from Month 1-2 informing the business case.

## 9. One Honest Limitation
K-means clustering produced two nearly-identical "Value Shopper" segments (clusters 0 and 3) rather than 4 truly distinct personas — a real limit of only having 5 behavioral features in synthetic data. Practical read: treat this as 3 meaningful personas. Additionally, the propensity model's ROC-AUC (~0.59) is modest — a production system would benefit from richer signals (search queries, session dwell time) not available in this synthetic dataset.

## 10. Why This Is an AI PM Project, Not Just a PM Project
The clustering and propensity model don't just describe the situation — they directly determine who sees the feature at all, which is the actual product decision here. The RICE override in Section 3 is itself an AI PM skill: knowing when a model's output (measured 2.8x concentration, 80% confidence) should outweigh a framework's raw score built partly on assumptions.

## Status
- [x] RICE scoring completed with real numbers
- [x] PRD written, including honest override of raw RICE ranking
- [x] A/B test design specified
- [ ] Dashboard (next)
- [ ] Executive summary (next)
