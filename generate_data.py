
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# Reproducible synthetic data for a PM portfolio project.
# This is simulated data, NOT real Instamart or Nectr customer data.

SEED = 7
N_USERS = 6000
START_DATE = datetime(2026, 1, 1)
DATE_RANGE_DAYS = 180
FUTURE_WINDOW_DAYS = 30
CUTOFF = START_DATE + timedelta(days=DATE_RANGE_DAYS - FUTURE_WINDOW_DAYS)
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(SEED)

CITY_TIERS = ["tier_1", "tier_2", "tier_3"]
CITY_WEIGHTS = [0.50, 0.35, 0.15]
STANDARD_CATEGORIES = ["staples", "snacks", "dairy"]
PREMIUM_CATEGORIES = [
    "organic_produce", "imported_gourmet", "premium_meat_seafood"
]
ALL_CATEGORIES = STANDARD_CATEGORIES + PREMIUM_CATEGORIES

# Generate users.
user_ids = [f"U{200000 + i}" for i in range(N_USERS)]
city_tiers = rng.choice(CITY_TIERS, N_USERS, p=CITY_WEIGHTS)
signup_offsets = rng.integers(0, DATE_RANGE_DAYS, N_USERS)
signup_dates = [
    START_DATE + timedelta(days=int(offset))
    for offset in signup_offsets
]
base_affinity = rng.beta(2, 5, N_USERS)
tier_boost = np.where(
    city_tiers == "tier_1", 0.15,
    np.where(city_tiers == "tier_2", 0.03, -0.05)
)
affinity = np.clip(base_affinity + tier_boost, 0, 1)

users = pd.DataFrame({
    "user_id": user_ids,
    "city_tier": city_tiers,
    "signup_date": [d.date().isoformat() for d in signup_dates],
    "_affinity": affinity,
})

# Generate orders only after signup. The observation end is exclusive.
observation_end = START_DATE + timedelta(days=DATE_RANGE_DAYS)
order_rows = []
order_number = 0

for i, user in users.iterrows():
    available_days = (observation_end - signup_dates[i]).days
    if available_days <= 0:
        continue

    # More frequent orders for users with higher simulated premium affinity.
    order_count = int(np.clip(rng.poisson(2 + 6 * user["_affinity"]), 0, 15))

    for _ in range(order_count):
        order_number += 1
        order_date = signup_dates[i] + timedelta(
            days=int(rng.integers(0, available_days))
        )

        n_items = int(rng.integers(2, 12))
        premium_order = rng.random() < (0.03 + 0.35 * user["_affinity"])
        premium_items = (
            int(rng.integers(max(1, n_items // 2), n_items + 1))
            if premium_order else 0
        )
        standard_items = n_items - premium_items

        order_value = max(
            50.0,
            standard_items * rng.normal(60, 15)
            + premium_items * rng.normal(280, 60)
        )
        dominant_category = (
            rng.choice(PREMIUM_CATEGORIES)
            if premium_items > standard_items
            else rng.choice(STANDARD_CATEGORIES)
        )

        # Nectr is a simulated brand within premium orders.
        # Brand propensity is synthetic and is not based on real customer evidence.
        nectr_probability = np.clip(
            0.015 + 0.16 * user["_affinity"], 0, 0.25
        )
        nectr_bought = bool(
            premium_items > 0 and rng.random() < nectr_probability
        )

        order_rows.append({
            "order_id": f"O{700000 + order_number}",
            "user_id": user["user_id"],
            "order_date": order_date.date().isoformat(),
            "order_value": round(float(order_value), 2),
            "item_count": n_items,
            "premium_item_count": premium_items,
            "dominant_category": dominant_category,
            "time_of_day": rng.choice(
                ["morning", "afternoon", "evening", "night"],
                p=[0.20, 0.25, 0.35, 0.20]
            ),
            "channel": rng.choice(["app", "web"], p=[0.92, 0.08]),
            "nectr_purchase": int(nectr_bought),
        })

orders = pd.DataFrame(order_rows)
orders["order_date_dt"] = pd.to_datetime(orders["order_date"])
orders["signup_date_dt"] = orders["user_id"].map(
    users.set_index("user_id")["signup_date"]
)
orders["signup_date_dt"] = pd.to_datetime(orders["signup_date_dt"])

# Inject data quality issues into the raw dataset; the modeling pipeline
# will explicitly clean them before constructing features and labels.
if not orders.empty:
    missing_mask = rng.random(len(orders)) < 0.025
    orders.loc[missing_mask, "dominant_category"] = np.nan

    duplicate_rows = orders.sample(
        frac=0.01, random_state=11
    ).copy()
    duplicate_rows["order_id"] = duplicate_rows["order_id"] + "_DUP"
    orders = pd.concat([orders, duplicate_rows], ignore_index=True)

    negative_mask = rng.random(len(orders)) < 0.004
    orders.loc[negative_mask, "order_value"] = (
        -orders.loc[negative_mask, "order_value"].abs()
    )

# Remove synthetic data-quality faults before defining canonical labels.
clean = orders[
    ~orders["order_id"].str.endswith("_DUP")
    & (orders["order_value"] > 0)
].copy()

clean["dominant_category"] = clean["dominant_category"].fillna("staples")
clean["order_date_dt"] = pd.to_datetime(clean["order_date"])
clean["signup_date_dt"] = pd.to_datetime(clean["signup_date_dt"])

history = clean[clean["order_date_dt"] < CUTOFF].copy()
future = clean[
    (clean["order_date_dt"] >= CUTOFF)
    & (clean["order_date_dt"] < observation_end)
].copy()

# Eligible acquisition cohort: users who have never purchased Nectr
# before the cutoff. Users with no historical orders remain eligible.
prior_buyers = set(
    history.loc[history["nectr_purchase"] == 1, "user_id"]
)
eligible_ids = set(users["user_id"]) - prior_buyers

future_first_buyers = set(
    future.loc[
        (future["nectr_purchase"] == 1)
        & future["user_id"].isin(eligible_ids),
        "user_id"
    ]
)

# User table does not expose the hidden affinity used for simulation.
users_out = users.drop(columns=["_affinity"]).copy()

categories = pd.DataFrame({
    "category_name": ALL_CATEGORIES,
    "price_tier": [
        "standard", "standard", "standard",
        "premium", "premium", "premium"
    ],
    "avg_margin_pct": [8, 12, 10, 22, 28, 26],
})

# Persist local, portable outputs.
users_out.to_csv(DATA_DIR / "dim_users.csv", index=False)
clean.drop(
    columns=["order_date_dt", "signup_date_dt"]
).to_csv(DATA_DIR / "fact_orders.csv", index=False)
categories.to_csv(DATA_DIR / "dim_categories.csv", index=False)
history.drop(
    columns=["order_date_dt", "signup_date_dt"]
).to_csv(DATA_DIR / "orders_history.csv", index=False)

pd.DataFrame({"user_id": sorted(prior_buyers)}).to_csv(
    DATA_DIR / "prior_nectr_buyers.csv", index=False
)
pd.DataFrame({"user_id": sorted(eligible_ids)}).to_csv(
    DATA_DIR / "eligible_first_nectr_cohort.csv", index=False
)
pd.DataFrame({"user_id": sorted(future_first_buyers)}).to_csv(
    DATA_DIR / "future_first_nectr_buyers.csv", index=False
)

# Keep a legacy filename for scripts not yet migrated; this label now means
# first Nectr purchase, not generic premium adoption.
pd.DataFrame({"user_id": sorted(future_first_buyers)}).to_csv(
    DATA_DIR / "future_premium_buyers.csv", index=False
)

print("Synthetic data generated successfully.")
print(f"Users: {len(users_out):,}")
print(f"Clean orders: {len(clean):,}")
print(f"Historical orders: {len(history):,}")
print(f"Future-window orders: {len(future):,}")
print(f"Prior Nectr buyers: {len(prior_buyers):,}")
print(f"Eligible first-purchase cohort: {len(eligible_ids):,}")
print(f"Future first Nectr buyers: {len(future_first_buyers):,}")
print(f"Future conversion among eligible: "
      f"{len(future_first_buyers) / max(len(eligible_ids), 1):.2%}")

# Sanity checks: these should always pass.
assert (clean["order_date_dt"] >= clean["signup_date_dt"]).all()
assert set(future_first_buyers).issubset(eligible_ids)
assert not (prior_buyers & eligible_ids)
assert clean["order_id"].is_unique
