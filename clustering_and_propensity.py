
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
pd.set_option("display.width", 140)

users = pd.read_csv(DATA_DIR / "dim_users.csv")
history = pd.read_csv(DATA_DIR / "orders_history.csv")
eligible_ids = set(
    pd.read_csv(DATA_DIR / "eligible_first_nectr_cohort.csv")["user_id"]
)
future_buyers = set(
    pd.read_csv(DATA_DIR / "future_first_nectr_buyers.csv")["user_id"]
)

# Clean historical orders and use pre-cutoff features only.
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
    evening_order_share=("time_of_day", lambda s: (s == "evening").mean()),
).reset_index()

agg["premium_item_share"] = (
    agg["total_premium_items"] / agg["total_items"].replace(0, 1)
)

features = users.merge(agg, on="user_id", how="left")
fill_cols = [
    "order_count", "avg_order_value", "total_premium_items",
    "total_items", "evening_order_share", "premium_item_share"
]
features[fill_cols] = features[fill_cols].fillna(0)

# Acquisition eligibility is based on the pre-cutoff cohort.
cohort = features[features["user_id"].isin(eligible_ids)].copy()
cohort["first_nectr_purchase_30d"] = (
    cohort["user_id"].isin(future_buyers).astype(int)
)
cohort["is_tier1"] = (cohort["city_tier"] == "tier_1").astype(int)

MODEL_COLS = [
    "order_count", "avg_order_value", "premium_item_share",
    "evening_order_share", "is_tier1"
]
X = cohort[MODEL_COLS]
y = cohort["first_nectr_purchase_30d"]

print("=" * 72)
print("FIRST-TIME NECTR ACQUISITION — SYNTHETIC DATA")
print("=" * 72)
print(f"Eligible users: {len(cohort):,}")
print(f"Future first-time buyers: {int(y.sum()):,}")
print(f"30-day baseline conversion: {y.mean():.2%}")

if y.nunique() != 2 or y.sum() < 10:
    raise ValueError("Not enough positive and negative labels to evaluate the model.")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=SEED, stratify=y
)

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000, class_weight="balanced", random_state=SEED
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=300, max_depth=5, min_samples_leaf=10,
        class_weight="balanced", random_state=SEED
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
        "average_precision": average_precision_score(y_test, probabilities),
    })
    fitted_models[name] = model

results_df = pd.DataFrame(results)
print("\nHELD-OUT MODEL COMPARISON")
print(results_df.round(3).to_string(index=False))

# Use the Random Forest for a transparent held-out ranking comparison.
# These predictions are generated only for test users.
rf = fitted_models["Random Forest"]
test_scores = cohort.loc[X_test.index, ["user_id"]].copy()
test_scores["actual_first_nectr_purchase"] = y_test
test_scores["propensity_score"] = rf.predict_proba(X_test)[:, 1]

test_scores["score_rank"] = test_scores["propensity_score"].rank(
    method="first", ascending=False
)
top_n = max(1, int(np.ceil(len(test_scores) * 0.10)))
top_decile = test_scores.nsmallest(top_n, "score_rank")

baseline_rate = test_scores["actual_first_nectr_purchase"].mean()
top_rate = top_decile["actual_first_nectr_purchase"].mean()
lift = top_rate / baseline_rate if baseline_rate > 0 else np.nan

print("\nHELD-OUT TOP-DECILE TARGETING")
print(f"Test users: {len(test_scores):,}")
print(f"Test-set baseline conversion: {baseline_rate:.2%}")
print(f"Top-decile conversion: {top_rate:.2%}")
print(f"Top-decile concentration vs test baseline: {lift:.2f}x")
print(f"Top-decile users: {len(top_decile):,}")

# Save test scores and model metrics. Do not score training users for
# the headline evaluation.
test_scores.to_csv(
    DATA_DIR / "heldout_first_nectr_scores.csv", index=False
)
results_df.to_csv(DATA_DIR / "first_nectr_model_metrics.csv", index=False)

# Optional descriptive clustering on historical behaviour.
active = features[features["order_count"] > 0].copy()
cluster_cols = [
    "order_count", "avg_order_value",
    "premium_item_share", "evening_order_share"
]
if len(active) >= 6:
    scaler = StandardScaler()
    scaled = scaler.fit_transform(active[cluster_cols])
    kmeans = KMeans(n_clusters=4, random_state=SEED, n_init=10)
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

print("\nSaved:")
print("- data/heldout_first_nectr_scores.csv")
print("- data/first_nectr_model_metrics.csv")
print("- data/cluster_summary.csv (if clustering ran)")
print("\nReminder: all results are from synthetic data, not real customer evidence.")
