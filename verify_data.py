
from datetime import timedelta
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent / "data"

FILES = [
    "dim_users.csv",
    "orders_history.csv",
    "fact_orders.csv",
    "eligible_first_nectr_cohort.csv",
    "future_first_nectr_buyers.csv",
    "prior_nectr_buyers.csv",
]

# Keep these aligned with generate_data.py.
START_DATE = pd.Timestamp("2026-01-01")
DATE_RANGE_DAYS = 180
FUTURE_WINDOW_DAYS = 30
CUTOFF = START_DATE + pd.Timedelta(
    days=DATE_RANGE_DAYS - FUTURE_WINDOW_DAYS
)
OBSERVATION_END = START_DATE + pd.Timedelta(days=DATE_RANGE_DAYS)


def fail(message):
    print(f"FAIL: {message}")
    raise SystemExit(1)


print("Starting data verification...")
print("Data folder:", BASE)
print(f"Historical cutoff: {CUTOFF.date()} (exclusive)")
print(f"Observation end: {OBSERVATION_END.date()} (exclusive)")

missing = [name for name in FILES if not (BASE / name).is_file()]
if missing:
    fail("Missing files: " + ", ".join(missing))

data = {name: pd.read_csv(BASE / name) for name in FILES}

for name, df in data.items():
    print(f"{name}: {len(df):,} rows")

users = data["dim_users.csv"]
history = data["orders_history.csv"]
facts = data["fact_orders.csv"]
eligible = data["eligible_first_nectr_cohort.csv"]
future_buyers = data["future_first_nectr_buyers.csv"]
prior_buyers = data["prior_nectr_buyers.csv"]

print("\nChecking required columns...")

for name, df in data.items():
    if "user_id" not in df.columns:
        fail(f"user_id column missing in {name}")

for name in ["orders_history.csv", "fact_orders.csv"]:
    required = {"order_id", "user_id", "order_date", "nectr_purchase"}
    missing_columns = required - set(data[name].columns)
    if missing_columns:
        fail(f"{name} missing columns: {sorted(missing_columns)}")

if "signup_date" not in users.columns:
    fail("signup_date column missing in dim_users.csv")

print("PASS: Required columns exist.")

print("\nChecking IDs and duplicates...")

if users["user_id"].isna().any() or users["user_id"].duplicated().any():
    fail("dim_users.csv contains missing or duplicate user IDs")

for name in FILES:
    df = data[name]
    if df["user_id"].isna().any():
        fail(f"Missing user IDs in {name}")

for name in ["orders_history.csv", "fact_orders.csv"]:
    df = data[name]
    if df["order_id"].isna().any() or df["order_id"].duplicated().any():
        fail(f"Missing or duplicate order IDs in {name}")

print("PASS: User and order identifiers are valid.")

print("\nChecking dates and user references...")

user_ids = set(users["user_id"])

signup_dates = pd.to_datetime(users["signup_date"], errors="coerce")
if signup_dates.isna().any():
    fail("Invalid signup dates in dim_users.csv")

for name in ["orders_history.csv", "fact_orders.csv"]:
    df = data[name]
    dates = pd.to_datetime(df["order_date"], errors="coerce")

    if dates.isna().any():
        fail(f"Invalid order dates in {name}")

    if not set(df["user_id"]).issubset(user_ids):
        fail(f"{name} contains users absent from dim_users.csv")

    if name == "orders_history.csv":
        if not (dates < CUTOFF).all():
            fail("Historical orders include dates on or after the cutoff.")
    else:
        if not ((dates >= START_DATE) & (dates < OBSERVATION_END)).all():
            fail("Fact orders fall outside the full observation window.")

    mapped_signup = df["user_id"].map(
        users.set_index("user_id")["signup_date"]
    )
    mapped_signup = pd.to_datetime(mapped_signup, errors="coerce")

    if not (dates >= mapped_signup).all():
        fail(f"Orders before signup date found in {name}")

print("PASS: Date windows and order-user references are valid.")

print("\nChecking cohort membership...")

for name, df in [
    ("eligible_first_nectr_cohort.csv", eligible),
    ("future_first_nectr_buyers.csv", future_buyers),
    ("prior_nectr_buyers.csv", prior_buyers),
]:
    if df["user_id"].duplicated().any():
        fail(f"Duplicate user IDs in {name}")

eligible_ids = set(eligible["user_id"])
prior_ids = set(prior_buyers["user_id"])
future_ids = set(future_buyers["user_id"])

if not eligible_ids.issubset(user_ids):
    fail("Eligible cohort contains unknown users")

if not prior_ids.issubset(user_ids):
    fail("Prior buyer cohort contains unknown users")

if not future_ids.issubset(user_ids):
    fail("Future buyer cohort contains unknown users")

if eligible_ids != user_ids - prior_ids:
    fail("Eligible cohort does not equal all users minus prior Nectr buyers")

if eligible_ids & prior_ids:
    fail("Eligible cohort overlaps with prior Nectr buyers")

# Reconstruct first-time buyers from the future-window orders.
history_dates = pd.to_datetime(history["order_date"], errors="coerce")
fact_dates = pd.to_datetime(facts["order_date"], errors="coerce")

historical_prior_ids = set(
    history.loc[history["nectr_purchase"] == 1, "user_id"]
)
if historical_prior_ids != prior_ids:
    fail("Prior buyer cohort does not match historical Nectr purchases")

future_orders = facts[
    (fact_dates >= CUTOFF) & (fact_dates < OBSERVATION_END)
]

expected_future_buyers = set(
    future_orders.loc[
        (future_orders["nectr_purchase"] == 1)
        & future_orders["user_id"].isin(eligible_ids),
        "user_id",
    ]
)

if expected_future_buyers != future_ids:
    fail("Future buyer cohort does not match future-window Nectr purchases")

if not future_ids.issubset(eligible_ids):
    fail("Future first-time buyers include ineligible users")

print("PASS: Eligible, prior, and future buyer cohorts match the source data.")

print("\nALL DATA VERIFICATION CHECKS PASSED.")
print("Note: These checks validate synthetic data consistency, not real-world validity.")
