
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

SEED = 42
DATA_DIR = Path(__file__).resolve().parent / "data"
pd.set_option("display.width", 160)

# --------------------------------------------------
# 1. Load and validate source data
# --------------------------------------------------

users = pd.read_csv(DATA_DIR / "dim_users.csv")
history = pd.read_csv(DATA_DIR / "orders_history.csv")

eligible_df = pd.read_csv(DATA_DIR / "eligible_first_nectr_cohort.csv")
future_df = pd.read_csv(DATA_DIR / "future_first_nectr_buyers.csv")

for name, df in [
    ("Users", users),
    ("Eligible cohort", eligible_df),
    ("Future buyers", future_df),
]:
    if "user_id" not in df.columns:
        raise ValueError(f"{name} file is missing user_id.")
    if df["user_id"].isna().any():
        raise ValueError(f"{name} file contains missing user IDs.")
    if df["user_id"].duplicated().any():
        raise ValueError(f"{name} file contains duplicate user IDs.")

if users["user_id"].duplicated().any():
    raise ValueError("dim_users.csv contains duplicate user IDs.")

eligible_ids = set(eligible_df["user_id"])
future_buyers = set(future_df["user_id"])
user_ids = set(users["user_id"])

if not eligible_ids.issubset(user_ids):
    raise ValueError("Eligible cohort contains users missing from dim_users.csv.")

if not future_buyers.issubset(eligible_ids):
    raise ValueError("Future buyers include users outside the eligible cohort.")

print("Source data validation passed.")
print(f"Eligible users: {len(eligible_ids):,}")
print(f"Future first-time buyers: {len(future_buyers):,}")

# --------------------------------------------------
# 2. Build historical behavioural features
# --------------------------------------------------

# This assumes orders_history.csv contains only pre-cutoff orders.
# The cutoff itself must be verified against the data-generation process.

history = history[
    ~history["order_id"].astype(str).str.endswith("_DUP")
    & (history["order_value"] > 0)
].copy()

history["dominant_category"] = history["dominant_category"].fillna("staples")

agg = history.groupby("user_id").agg(
    order_count=("order_id", "count"),
    avg_order_value=("order_value", "mean"),
    total_premium_items=("premium_item_count", "sum"),
    total_items=("item_count", "sum"),
    evening_order_share=(
        "time_of_day",
        lambda s: (s == "evening").mean(),
    ),
).reset_index()

agg["premium_item_share"] = (
    agg["total_premium_items"]
    / agg["total_items"].replace(0, 1)
)

features = users.merge(
    agg,
    on="user_id",
    how="left",
    validate="one_to_one",
)

fill_cols = [
    "order_count",
    "avg_order_value",
    "total_premium_items",
    "total_items",
    "evening_order_share",
    "premium_item_share",
]

# Missing history is treated as zero for this exploratory baseline.
# This assumption should be revisited before production use.
features[fill_cols] = features[fill_cols].fillna(0)

# --------------------------------------------------
# 3. Define the first-time acquisition cohort and label
# --------------------------------------------------

cohort = features[features["user_id"].isin(eligible_ids)].copy()

cohort["first_nectr_purchase_30d"] = (
    cohort["user_id"].isin(future_buyers).astype(int)
)

cohort["is_tier1"] = (
    cohort["city_tier"] == "tier_1"
).astype(int)

MODEL_COLS = [
    "order_count",
    "avg_order_value",
    "premium_item_share",
    "evening_order_share",
    "is_tier1",
]

X = cohort[MODEL_COLS]
y = cohort["first_nectr_purchase_30d"]

print("\n" + "=" * 72)
print("FIRST-TIME NECTR ACQUISITION — SYNTHETIC DATA")
print("=" * 72)
print(f"Eligible users: {len(cohort):,}")
print(f"Future first-time buyers: {int(y.sum()):,}")
print(f"30-day baseline conversion: {y.mean():.2%}")

if y.nunique() != 2 or y.sum() < 10:
    raise ValueError(
        "Not enough positive and negative labels to evaluate the model."
    )

# --------------------------------------------------
# 4. Split data and evaluate candidate models
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=SEED,
    stratify=y,
)

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=SEED,
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        max_depth=5,
        min_samples_leaf=10,
        class_weight="balanced",
        random_state=SEED,
    ),
}

results = []
fitted_models = {}

for name, model in models.items():
    model.fit(X_train, y_train)

    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    results.append({
        "model": name,
        "precision_at_0_5": precision_score(
            y_test, predictions, zero_division=0
        ),
        "recall_at_0_5": recall_score(
            y_test, predictions, zero_division=0
        ),
        "roc_auc": roc_auc_score(y_test, probabilities),
        "average_precision": average_precision_score(
            y_test, probabilities
        ),
    })

    fitted_models[name] = model

results_df = pd.DataFrame(results)

print("\nHELD-OUT MODEL COMPARISON")
print(results_df.round(4).to_string(index=False))

# --------------------------------------------------
# 5. Compare top-decile ranking for both models
# --------------------------------------------------

# Both models are evaluated on exactly the same held-out users.
test_scores = cohort.loc[
    X_test.index, ["user_id"]
].copy()

test_scores["actual_first_nectr_purchase"] = y_test.to_numpy()

baseline_rate = test_scores[
    "actual_first_nectr_purchase"
].mean()

top_n = max(1, int(np.ceil(len(test_scores) * 0.10)))

print("\nHELD-OUT TOP-DECILE TARGETING COMPARISON")
print(f"Test users: {len(test_scores):,}")
print(f"Test-set baseline conversion: {baseline_rate:.2%}")
print(f"Top-decile users per model: {top_n:,}")

ranking_results = []

for name, model in fitted_models.items():
    probabilities = model.predict_proba(X_test)[:, 1]

    ranked = test_scores[
        ["user_id", "actual_first_nectr_purchase"]
    ].copy()

    ranked["propensity_score"] = probabilities

    ranked = ranked.sort_values(
        "propensity_score",
        ascending=False,
        kind="stable",
    )

    top_decile = ranked.head(top_n)

    top_rate = top_decile[
        "actual_first_nectr_purchase"
    ].mean()

    concentration = (
        top_rate / baseline_rate
        if baseline_rate > 0
        else np.nan
    )

    ranking_results.append({
        "model": name,
        "top_decile_conversion": top_rate,
        "baseline_conversion": baseline_rate,
        "concentration_vs_baseline": concentration,
        "top_decile_users": len(top_decile),
    })

    score_column = (
        "lr_propensity_score"
        if name == "Logistic Regression"
        else "rf_propensity_score"
    )

    test_scores[score_column] = probabilities

ranking_df = pd.DataFrame(ranking_results)

print(ranking_df.round(4).to_string(index=False))

# Preserve Random Forest as the default score column for compatibility
# with existing downstream outputs. This does not mean it is the winner.
test_scores["propensity_score"] = test_scores["rf_propensity_score"]

test_scores["score_rank"] = test_scores[
    "propensity_score"
].rank(
    method="first",
    ascending=False,
)

# --------------------------------------------------
# 6. Save held-out evaluation outputs
# --------------------------------------------------

test_scores.to_csv(
    DATA_DIR / "heldout_first_nectr_scores.csv",
    index=False,
)

results_df.to_csv(
    DATA_DIR / "first_nectr_model_metrics.csv",
    index=False,
)

# --------------------------------------------------
# 7. Descriptive clustering on historical behaviour
# --------------------------------------------------

active = features[features["order_count"] > 0].copy()

cluster_cols = [
    "order_count",
    "avg_order_value",
    "premium_item_share",
    "evening_order_share",
]

if len(active) >= 6:
    scaler = StandardScaler()
    scaled = scaler.fit_transform(active[cluster_cols])

    kmeans = KMeans(
        n_clusters=4,
        random_state=SEED,
        n_init=10,
    )

    active["cluster"] = kmeans.fit_predict(scaled)

    summary = active.groupby("cluster").agg(
        users=("user_id", "count"),
        avg_orders=("order_count", "mean"),
        avg_order_value=("avg_order_value", "mean"),
        avg_premium_item_share=("premium_item_share", "mean"),
    ).round(3)

    summary.to_csv(DATA_DIR / "cluster_summary.csv")

    print("\nDESCRIPTIVE CLUSTER SUMMARY")
    print(summary.to_string())

# --------------------------------------------------
# 8. Final output
# --------------------------------------------------

print("\nSaved:")
print("- data/heldout_first_nectr_scores.csv")
print("- data/first_nectr_model_metrics.csv")
print("- data/cluster_summary.csv (if clustering ran)")
print(
    "\nReminder: all results are from synthetic data, "
    "not real customer evidence."
)
