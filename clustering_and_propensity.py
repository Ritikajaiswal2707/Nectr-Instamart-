"""
Instamart Nectr — Clustering & Propensity Model
Uses only pre-cutoff history to build features (no leakage), and the
held-out future-30-day window to define the propensity label.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, precision_score, recall_score, roc_auc_score, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

pd.set_option("display.width", 120)

users = pd.read_csv("/home/claude/instamart/data/dim_users.csv")
history = pd.read_csv("/home/claude/instamart/data/orders_history.csv")
future_buyers = set(pd.read_csv("/home/claude/instamart/data/future_premium_buyers.csv")["user_id"])

# Clean: drop duplicate orders, drop negative order values, fill missing category
history = history[~history["order_id"].str.endswith("_DUP")].copy()
history = history[history["order_value"] > 0].copy()
history["dominant_category"] = history["dominant_category"].fillna("staples")

# ---------------------------------------------------------------------------
# BUILD USER-LEVEL FEATURES from history only
# ---------------------------------------------------------------------------
agg = history.groupby("user_id").agg(
    order_count=("order_id", "count"),
    avg_order_value=("order_value", "mean"),
    total_premium_items=("premium_item_count", "sum"),
    total_items=("item_count", "sum"),
    evening_order_share=("time_of_day", lambda s: (s == "evening").mean()),
).reset_index()

agg["premium_item_share"] = agg["total_premium_items"] / agg["total_items"].replace(0, 1)

user_features = users.merge(agg, on="user_id", how="left").fillna({
    "order_count": 0, "avg_order_value": 0, "total_premium_items": 0,
    "total_items": 0, "evening_order_share": 0, "premium_item_share": 0
})

active_users = user_features[user_features["order_count"] > 0].copy()
print(f"Total users: {len(user_features)} | Active (with history orders): {len(active_users)}")

# ---------------------------------------------------------------------------
# K-MEANS CLUSTERING
# ---------------------------------------------------------------------------
cluster_features = active_users[["order_count", "avg_order_value", "premium_item_share", "evening_order_share"]]
scaler = StandardScaler()
cluster_scaled = scaler.fit_transform(cluster_features)

print("\n" + "=" * 70)
print("SILHOUETTE SCORE BY K")
print("=" * 70)
for k in [2, 3, 4, 5, 6]:
    km_test = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels_test = km_test.fit_predict(cluster_scaled)
    score = silhouette_score(cluster_scaled, labels_test)
    print(f"k={k}: silhouette = {score:.3f}")

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
active_users["cluster"] = kmeans.fit_predict(cluster_scaled)
final_silhouette = silhouette_score(cluster_scaled, active_users["cluster"])
print(f"\nUsing k=4. Silhouette at k=4: {final_silhouette:.3f}")

print("\n" + "=" * 70)
print("CLUSTER PROFILES")
print("=" * 70)
cluster_summary = active_users.groupby("cluster").agg(
    n_users=("user_id", "count"),
    avg_order_count=("order_count", "mean"),
    avg_order_value=("avg_order_value", "mean"),
    avg_premium_share=("premium_item_share", "mean"),
    pct_tier1=("city_tier", lambda s: (s == "tier_1").mean()),
).round(2)
print(cluster_summary.to_string())

def label_cluster(row):
    if row["avg_premium_share"] > 0.25:
        return "Premium Explorer / Health-Conscious"
    elif row["avg_order_count"] > cluster_summary["avg_order_count"].median() and row["avg_premium_share"] < 0.1:
        return "Convenience Seeker"
    elif row["avg_order_value"] < cluster_summary["avg_order_value"].median():
        return "Value Shopper"
    else:
        return "Occasional Premium Explorer"

cluster_summary["persona_label"] = cluster_summary.apply(label_cluster, axis=1)
print("\nPersona labels assigned:")
print(cluster_summary[["n_users", "persona_label"]].to_string())

# ---------------------------------------------------------------------------
# PROPENSITY MODEL
# ---------------------------------------------------------------------------
active_users["will_buy_premium_future"] = active_users["user_id"].isin(future_buyers).astype(int)

model_features = active_users[[
    "order_count", "avg_order_value", "premium_item_share", "evening_order_share"
]].copy()
model_features["is_tier1"] = (active_users["city_tier"] == "tier_1").astype(int)
y = active_users["will_buy_premium_future"]

X_train, X_test, y_train, y_test = train_test_split(
    model_features, y, test_size=0.25, random_state=42, stratify=y
)

print("\n" + "=" * 70)
print("PROPENSITY MODEL")
print("=" * 70)
print(f"Base rate (test set): {y_test.mean():.1%} will buy premium in next 30 days")

logreg = LogisticRegression(max_iter=1000, class_weight="balanced")
logreg.fit(X_train, y_train)
logreg_probs = logreg.predict_proba(X_test)[:, 1]
logreg_preds = (logreg_probs >= 0.5).astype(int)
print(f"\nLogistic Regression — Precision: {precision_score(y_test, logreg_preds):.3f}, "
      f"Recall: {recall_score(y_test, logreg_preds):.3f}, ROC-AUC: {roc_auc_score(y_test, logreg_probs):.3f}")

rf = RandomForestClassifier(n_estimators=200, max_depth=6, class_weight="balanced", random_state=42)
rf.fit(X_train, y_train)
rf_probs = rf.predict_proba(X_test)[:, 1]
rf_preds = (rf_probs >= 0.5).astype(int)
print(f"Random Forest       — Precision: {precision_score(y_test, rf_preds):.3f}, "
      f"Recall: {recall_score(y_test, rf_preds):.3f}, ROC-AUC: {roc_auc_score(y_test, rf_probs):.3f}")

importance_df = pd.DataFrame({
    "feature": model_features.columns,
    "importance": rf.feature_importances_
}).sort_values("importance", ascending=False)
print("\nRandom Forest feature importances:")
print(importance_df.to_string(index=False))

# ---------------------------------------------------------------------------
# THE KEY NUMBER: premium adoption rate in top-propensity segment vs overall
# ---------------------------------------------------------------------------
active_users["propensity_score"] = rf.predict_proba(model_features)[:, 1]
top_decile_threshold = active_users["propensity_score"].quantile(0.90)
top_decile = active_users[active_users["propensity_score"] >= top_decile_threshold]

overall_rate = active_users["will_buy_premium_future"].mean()
top_decile_rate = top_decile["will_buy_premium_future"].mean()
uplift_x = top_decile_rate / overall_rate if overall_rate > 0 else float("nan")

print("\n" + "=" * 70)
print("TARGETING RESULT — the headline number")
print("=" * 70)
print(f"Overall premium adoption rate (all active users): {overall_rate:.1%}")
print(f"Premium adoption rate in TOP 10% propensity segment: {top_decile_rate:.1%}")
print(f"That's a {uplift_x:.1f}x concentration of premium buyers in the top-decile segment")
print(f"Top decile segment size: {len(top_decile)} users ({len(top_decile)/len(active_users):.1%} of active users)")

active_users.merge(
    cluster_summary[["persona_label"]], left_on="cluster", right_index=True
).to_csv("/home/claude/instamart/data/user_segments_with_propensity.csv", index=False)
print("\nSaved: user_segments_with_propensity.csv")
