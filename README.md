# Nectr-Instamart — Premium Grocery Targeting

An AI Product Management case study: who should see Instamart's premium grocery line (Nectr) first, and should it live inside the existing app, get its own tab, or become a separate surface entirely?

## The Problem
Instamart built its identity on 10-minute delivery — but it's testing Nectr while Zepto's Harvest Store and FirstClub already prove premium grocery demand exists. Going premium risks slowing the core speed promise; not going premium risks ceding a high-margin segment to competitors. The open question: **which users are actually likely to buy premium, and what's the lowest-risk way to reach them first?**

## Approach: Segmentation → Clustering → Propensity Model → RICE → PRD → Dashboard

| Step | File | What it does |
|---|---|---|
| 1. Data | `generate_data.py` | Synthetic dataset: 6,000 users, ~25,000 orders. First version had a calibration bug — 78% of orders came out "premium" due to a compounding-probability error in the generation logic. Recalibrated to a realistic 17.2%, documented in the script. |
| 2. Clustering + Propensity | `clustering_and_propensity.py`, `findings.md` | K-means segments users into personas; Logistic Regression/Random Forest predicts who buys premium in the next 30 days (no data leakage — features from history only, label from a held-out future window) |
| 3. RICE Scoring | `rice_scoring.py` | Scores 3 product options (personalized rail / dedicated tab / standalone app) using real segment sizes pulled from the model, not guesses |
| 4. PRD | `prd.md` | User stories, acceptance criteria, A/B test design, stakeholder tensions, 30-60-90 day plan — including a deliberate override of the raw RICE ranking (explained below) |
| 5. Dashboard | `build_dashboard.py`, `dashboard.png` | 4-panel view: persona distribution, adoption concentration, AOV/premium-share profile, RICE comparison |
| 6. Executive Summary | `executive_summary.md` | One-page summary written for a non-technical reader |

## Headline Result
The top 10% of users by propensity score convert to premium purchases at **30.5%**, versus an **11.0%** base rate across all active users — a **2.8x concentration**. This is the evidence base for targeting a rollout instead of launching broadly.

## The RICE Override — the most interesting finding
Raw RICE scoring actually favored a broad, dedicated premium tab shown to all users (score: 716) over a personalized rail shown only to the top-decile segment (score: 612). **The recommendation goes with the rail anyway.** Reach alone rewards showing premium to everyone — including the 58% of users who are "Value Shoppers" with almost no premium interest (~2% of their purchases). The rail's confidence is grounded in an actual measured number (the 2.8x concentration); the tab's confidence is a guess about behavior at a scale never tested. Full reasoning is in `prd.md`, Section 3.

## Personas
| Persona | Share of users | Avg Order Value | Premium Item Share |
|---|---|---|---|
| Value Shopper | 58% | ~₹414 | ~2% |
| Occasional Premium Explorer | 27% | ₹572 | 14% |
| Premium Explorer / Health-Conscious | 15% | ₹1,143 | 46% |

**One honest limitation:** clustering technically produced 4 segments, but two came out nearly identical on every feature — realistically this is 3 meaningful personas, not 4, given only 5 behavioral signals were available in synthetic data.

## Data
All data in `data/` is **synthetic — created to simulate realistic operational scenarios, not proprietary Instamart data.**

## Tech Stack
Python, pandas, scikit-learn (K-Means, Logistic Regression, Random Forest), matplotlib
