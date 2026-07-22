"""
Instamart Nectr — Synthetic Data Generator
Generates dim_users, fact_orders, dim_categories tables simulating
quick-commerce purchase behavior, with realistic premium-adoption signal
built in (not just noise) so clustering/propensity modeling has something
real to find.

Synthetic dataset created to simulate realistic operational scenarios —
not proprietary Instamart data.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

rng = np.random.default_rng(7)

N_USERS = 6000
N_ORDERS = 25000
START_DATE = datetime(2026, 1, 1)
DATE_RANGE_DAYS = 180

CITY_TIERS = ["tier_1", "tier_2", "tier_3"]
CITY_WEIGHTS = [0.5, 0.35, 0.15]

CATEGORIES = ["staples", "snacks", "dairy", "organic_produce", "imported_gourmet", "premium_meat_seafood"]
CATEGORY_PRICE_TIER = {
    "staples": "standard", "snacks": "standard", "dairy": "standard",
    "organic_produce": "premium", "imported_gourmet": "premium", "premium_meat_seafood": "premium",
}
CATEGORY_MARGIN = {
    "staples": 8, "snacks": 12, "dairy": 10,
    "organic_produce": 22, "imported_gourmet": 28, "premium_meat_seafood": 26,
}

# ---------------------------------------------------------------------------
# USERS — each user has a latent "premium affinity" that drives their behavior
# ---------------------------------------------------------------------------
user_ids = [f"U{200000+i}" for i in range(N_USERS)]
city_tier = rng.choice(CITY_TIERS, size=N_USERS, p=CITY_WEIGHTS)
signup_offsets = rng.integers(0, DATE_RANGE_DAYS, size=N_USERS)
signup_dates = [START_DATE + timedelta(days=int(o)) for o in signup_offsets]

# latent affinity: tier_1 skews higher, but plenty of variance within each tier
base_affinity = rng.beta(2, 5, size=N_USERS)  # right-skewed, most users low-to-mid affinity
tier_boost = np.where(city_tier == "tier_1", 0.15, np.where(city_tier == "tier_2", 0.03, -0.05))
premium_affinity = np.clip(base_affinity + tier_boost, 0, 1)

users = pd.DataFrame({
    "user_id": user_ids,
    "city_tier": city_tier,
    "signup_date": [d.date().isoformat() for d in signup_dates],
    "_premium_affinity": premium_affinity,  # latent var, kept for label generation only
})

# ---------------------------------------------------------------------------
# ORDERS — order frequency and category mix driven by each user's affinity
# ---------------------------------------------------------------------------
# assign number of orders per user (frequency), higher affinity -> more orders on average
user_order_lambda = 2 + users["_premium_affinity"].values * 6
orders_per_user = rng.poisson(user_order_lambda)
orders_per_user = np.clip(orders_per_user, 0, 15)

order_rows = []
oid = 0
for idx, row in users.iterrows():
    n_orders = orders_per_user[idx]
    affinity = row["_premium_affinity"]
    for _ in range(n_orders):
        oid += 1
        order_offset = rng.integers(0, DATE_RANGE_DAYS)
        order_date = START_DATE + timedelta(days=int(order_offset))

        # Model each ORDER as premium-leaning or not (order-level decision),
        # not per-item independent draws — avoids the compounding-probability
        # trap where high item counts make "at least one premium item" near-certain
        # even for low-affinity users.
        is_premium_order = rng.random() < (0.03 + 0.35 * affinity)
        n_items = rng.integers(2, 12)

        if is_premium_order:
            # a premium-leaning order still mixes in some staples, but premium dominates
            premium_items = rng.integers(max(1, n_items // 2), n_items + 1)
            premium_items = min(premium_items, n_items)
        else:
            premium_items = 0
        standard_items = n_items - premium_items

        # order value: standard items cheap, premium items expensive
        standard_value = standard_items * rng.normal(60, 15)
        premium_value = premium_items * rng.normal(280, 60)
        order_value = max(50, standard_value + premium_value)

        dominant_category = (
            rng.choice(["organic_produce", "imported_gourmet", "premium_meat_seafood"])
            if premium_items > standard_items
            else rng.choice(["staples", "snacks", "dairy"])
        )

        time_of_day = rng.choice(["morning", "afternoon", "evening", "night"], p=[0.2, 0.25, 0.35, 0.2])

        order_rows.append({
            "order_id": f"O{700000+oid}",
            "user_id": row["user_id"],
            "order_date": order_date.date().isoformat(),
            "order_value": round(order_value, 2),
            "item_count": n_items,
            "premium_item_count": premium_items,
            "dominant_category": dominant_category,
            "time_of_day": time_of_day,
            "channel": rng.choice(["app", "web"], p=[0.92, 0.08]),
        })

orders = pd.DataFrame(order_rows)

# ---------------------------------------------------------------------------
# CATEGORY DIM TABLE
# ---------------------------------------------------------------------------
dim_categories = pd.DataFrame({
    "category_name": CATEGORIES,
    "price_tier": [CATEGORY_PRICE_TIER[c] for c in CATEGORIES],
    "avg_margin_pct": [CATEGORY_MARGIN[c] for c in CATEGORIES],
})

# ---------------------------------------------------------------------------
# LABEL for propensity model: will this user place a premium order in a
# held-out future window? (last 30 days of the date range = "future")
# ---------------------------------------------------------------------------
orders["order_date_dt"] = pd.to_datetime(orders["order_date"])
cutoff = START_DATE + timedelta(days=DATE_RANGE_DAYS - 30)

history = orders[orders["order_date_dt"] < cutoff].copy()
future = orders[orders["order_date_dt"] >= cutoff].copy()

future_premium_users = set(future.loc[future["premium_item_count"] > 0, "user_id"])

# ---------------------------------------------------------------------------
# INJECT MESSINESS
# ---------------------------------------------------------------------------
# missing dominant_category on ~2.5% of orders (tagging pipeline gap)
mask_missing_cat = rng.random(len(orders)) < 0.025
orders.loc[mask_missing_cat, "dominant_category"] = np.nan

# ~1% duplicate orders
dupe_orders = orders.sample(frac=0.01, random_state=11).copy()
dupe_orders["order_id"] = dupe_orders["order_id"] + "_DUP"
orders = pd.concat([orders, dupe_orders], ignore_index=True)

# a few negative order_value glitches (refund logging bug)
mask_negative = rng.random(len(orders)) < 0.004
orders.loc[mask_negative, "order_value"] = -abs(orders.loc[mask_negative, "order_value"])

# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------
users_out = users.drop(columns=["_premium_affinity"])
users_out.to_csv("/home/claude/instamart/data/dim_users.csv", index=False)
orders.drop(columns=["order_date_dt"]).to_csv("/home/claude/instamart/data/fact_orders.csv", index=False)
dim_categories.to_csv("/home/claude/instamart/data/dim_categories.csv", index=False)

# save the future-premium label set + history separately for modeling script
pd.DataFrame({"user_id": list(future_premium_users)}).to_csv(
    "/home/claude/instamart/data/future_premium_buyers.csv", index=False
)
history.drop(columns=["order_date_dt"]).to_csv("/home/claude/instamart/data/orders_history.csv", index=False)

print("Users:", users_out.shape)
print("Orders (all):", orders.shape)
print("Orders (history, pre-cutoff):", history.shape)
print("Users who bought premium in future 30-day window:", len(future_premium_users))
print("Overall % of orders containing a premium item:",
      round((orders["premium_item_count"] > 0).mean() * 100, 1), "%")
