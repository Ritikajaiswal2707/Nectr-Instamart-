
"""
Nectr x Instamart — First-Time Purchase Acquisition Dashboard

All underlying data and results are synthetic.
Outputs dashboard.png in the repository root.
"""

from pathlib import Path
import math

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ---------------------------------------------------------------------
# PATHS AND INPUTS
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_PATH = BASE_DIR / "dashboard.png"

SCORES_PATH = DATA_DIR / "heldout_first_nectr_scores.csv"
METRICS_PATH = DATA_DIR / "first_nectr_model_metrics.csv"
CLUSTERS_PATH = DATA_DIR / "cluster_summary.csv"

for path in [SCORES_PATH, METRICS_PATH, CLUSTERS_PATH]:
    if not path.exists():
        raise FileNotFoundError(
            f"Required input file not found: {path}\n"
            "Run generate_data.py and clustering_and_propensity.py first."
        )

scores = pd.read_csv(SCORES_PATH)
metrics = pd.read_csv(METRICS_PATH)
clusters = pd.read_csv(CLUSTERS_PATH)

required_score_columns = {
    "user_id",
    "actual_first_nectr_purchase",
    "propensity_score",
    "score_rank",
}
if not required_score_columns.issubset(scores.columns):
    missing = required_score_columns - set(scores.columns)
    raise ValueError(f"Missing score columns: {sorted(missing)}")

required_metric_columns = {
    "model",
    "roc_auc",
    "average_precision",
}
if not required_metric_columns.issubset(metrics.columns):
    missing = required_metric_columns - set(metrics.columns)
    raise ValueError(f"Missing model metric columns: {sorted(missing)}")

required_cluster_columns = {
    "cluster",
    "users",
    "avg_order_value",
    "avg_premium_item_share",
}
if not required_cluster_columns.issubset(clusters.columns):
    missing = required_cluster_columns - set(clusters.columns)
    raise ValueError(f"Missing cluster columns: {sorted(missing)}")

if scores.empty:
    raise ValueError("Held-out scores file is empty.")

if not scores["actual_first_nectr_purchase"].isin([0, 1]).all():
    raise ValueError("Purchase outcome must contain only 0 and 1.")

# ---------------------------------------------------------------------
# VISUAL STYLE
# ---------------------------------------------------------------------

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

PRIMARY = "#2F6F63"
SECONDARY = "#C9A227"
MUTED = "#9BA6A0"
ACCENT = "#B5563C"

# ---------------------------------------------------------------------
# HELD-OUT COHORT METRICS
# ---------------------------------------------------------------------

baseline_rate = scores["actual_first_nectr_purchase"].mean()
top_decile_count = max(1, math.ceil(len(scores) * 0.10))
scores["top_decile"] = scores["score_rank"] <= top_decile_count
top_decile = scores.loc[scores["top_decile"]]
top_decile_rate = top_decile["actual_first_nectr_purchase"].mean()
lift = top_decile_rate / baseline_rate if baseline_rate > 0 else 0

# ---------------------------------------------------------------------
# DASHBOARD CANVAS
# ---------------------------------------------------------------------

fig, axes = plt.subplots(2, 2, figsize=(15, 10.5))

fig.suptitle(
    "Nectr x Instamart — First-Time Purchase Acquisition",
    fontsize=16,
    fontweight="bold",
    y=0.985,
)

fig.text(
    0.5,
    0.952,
    "SYNTHETIC DATA — exploratory analysis, not actual business results",
    ha="center",
    fontsize=10,
    color=ACCENT,
)

# ---------------------------------------------------------------------
# CHART 1: FIRST-TIME PURCHASE CONVERSION
# ---------------------------------------------------------------------

ax = axes[0, 0]

labels = [
    f"All held-out users\n(n={len(scores):,})",
    f"Top-scored decile\n(n={len(top_decile):,})",
]
values = [baseline_rate * 100, top_decile_rate * 100]

bars = ax.bar(labels, values, color=[MUTED, PRIMARY], width=0.55)
ax.set_title("First-Time Nectr Purchase Rate", fontweight="bold")
ax.set_ylabel("Users purchasing in future window (%)")
ax.yaxis.set_major_formatter(mticker.PercentFormatter())

max_value = max(values) if values else 1
ax.set_ylim(0, max_value * 1.35 if max_value > 0 else 1)

for bar, value in zip(bars, values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + max_value * 0.04,
        f"{value:.2f}%",
        ha="center",
        fontweight="bold",
    )

ax.text(
    0.98,
    0.95,
    f"{lift:.2f}x concentration",
    transform=ax.transAxes,
    ha="right",
    va="top",
    color=PRIMARY,
    fontweight="bold",
)

# ---------------------------------------------------------------------
# CHART 2: MODEL COMPARISON
# Separate panels keep average-precision values readable.
# ---------------------------------------------------------------------

model_grid = axes[0, 1].get_subplotspec().subgridspec(1, 2, wspace=0.38)
axes[0, 1].remove()

ax_auc = fig.add_subplot(model_grid[0, 0])
ax_ap = fig.add_subplot(model_grid[0, 1])

model_colors = {
    "Logistic Regression": PRIMARY,
    "Random Forest": SECONDARY,
}
ordered_models = metrics["model"].tolist()
positions = list(range(len(ordered_models)))

auc_values = [
    float(metrics.loc[metrics["model"] == model, "roc_auc"].iloc[0])
    for model in ordered_models
]
ap_values = [
    float(metrics.loc[metrics["model"] == model, "average_precision"].iloc[0])
    for model in ordered_models
]
colors = [model_colors.get(model, MUTED) for model in ordered_models]

auc_bars = ax_auc.bar(positions, auc_values, color=colors, width=0.62)
ax_auc.set_title("ROC-AUC", fontweight="bold", fontsize=10)
ax_auc.set_xticks(positions)
ax_auc.set_xticklabels(
    ["Logistic\nRegression", "Random\nForest"], fontsize=8
)
ax_auc.set_ylim(0, max(auc_values) * 1.22)
ax_auc.set_ylabel("Score")

for bar, value in zip(auc_bars, auc_values):
    ax_auc.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + max(auc_values) * 0.025,
        f"{value:.3f}",
        ha="center",
        fontsize=8,
    )

ap_bars = ax_ap.bar(positions, ap_values, color=colors, width=0.62)
ax_ap.set_title("Average precision", fontweight="bold", fontsize=10)
ax_ap.set_xticks(positions)
ax_ap.set_xticklabels(
    ["Logistic\nRegression", "Random\nForest"], fontsize=8
)
ax_ap.set_ylim(
    0, max(ap_values) * 1.55 if max(ap_values) > 0 else 0.1
)

for bar, value in zip(ap_bars, ap_values):
    ax_ap.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + max(ap_values) * 0.04,
        f"{value:.3f}",
        ha="center",
        fontsize=8,
    )

ax_auc.text(
    0.5,
    1.14,
    "Held-Out Model Comparison",
    transform=ax_auc.transAxes,
    ha="center",
    fontweight="bold",
    fontsize=11,
)

ax_ap.text(
    0.5,
    -0.28,
    "Modest predictive performance",
    transform=ax_ap.transAxes,
    ha="center",
    fontsize=8,
    color=ACCENT,
)

# ---------------------------------------------------------------------
# CHART 3: DESCRIPTIVE SHOPPING CLUSTERS
# Label positions are adjusted to reduce overlap.
# ---------------------------------------------------------------------

ax = axes[1, 0]

ax.scatter(
    clusters["avg_order_value"],
    clusters["avg_premium_item_share"] * 100,
    s=clusters["users"] / 2,
    c=clusters["cluster"],
    cmap="viridis",
    alpha=0.8,
    edgecolors="white",
    linewidth=1.2,
)

label_offsets = {
    0: (10, 10),
    1: (10, 6),
    2: (12, -35),
    3: (12, 25),
}

for _, row in clusters.iterrows():
    cluster_id = int(row["cluster"])
    ax.annotate(
        f"Cluster {cluster_id} (n={int(row['users']):,})",
        (
            row["avg_order_value"],
            row["avg_premium_item_share"] * 100,
        ),
        xytext=label_offsets.get(cluster_id, (8, 8)),
        textcoords="offset points",
        fontsize=8,
        bbox=dict(
            boxstyle="round,pad=0.2",
            fc="white",
            ec="none",
            alpha=0.8,
        ),
    )

ax.set_title("Descriptive Shopping Clusters", fontweight="bold")
ax.set_xlabel("Average order value (₹)")
ax.set_ylabel("Premium-item share (%)")

# Keep the disclaimer away from the low-AOV cluster labels.
ax.text(
    0.02,
    0.98,
    "Synthetic clusters; not validated personas",
    transform=ax.transAxes,
    fontsize=7,
    color=ACCENT,
    ha="left",
    va="top",
)

# ---------------------------------------------------------------------
# CHART 4: ILLUSTRATIVE RICE COMPARISON
# ---------------------------------------------------------------------

ax = axes[1, 1]

options = pd.DataFrame(
    {
        "option": [
            "Personalized rail",
            "Dedicated tab",
            "Standalone app",
        ],
        "score": [612, 716, 86],
    }
).sort_values("score")

bar_colors = [
    PRIMARY if option == "Personalized rail" else MUTED
    for option in options["option"]
]

bars = ax.barh(options["option"], options["score"], color=bar_colors)
ax.set_title("Illustrative RICE Scores", fontweight="bold")
ax.set_xlabel("Planning score (assumptions, not measured outcomes)")
ax.set_xlim(0, options["score"].max() * 1.25)

for bar, value in zip(bars, options["score"]):
    ax.text(
        value + 8,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.0f}",
        va="center",
        fontsize=9,
    )

ax.text(
    0.98,
    0.04,
    "Proposed first test: personalized rail\nSmaller, reversible experiment",
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    fontsize=8,
    color=PRIMARY,
)

# ---------------------------------------------------------------------
# SAVE OUTPUT
# ---------------------------------------------------------------------

plt.tight_layout(rect=[0, 0.015, 1, 0.92])
fig.savefig(OUTPUT_PATH, dpi=160, bbox_inches="tight")
plt.close(fig)

print(f"Saved dashboard: {OUTPUT_PATH}")
print("Synthetic-data disclaimer included.")
print(f"Held-out users: {len(scores):,}")
print(f"Top-decile users: {len(top_decile):,}")
print(f"Held-out baseline: {baseline_rate:.2%}")
print(f"Top-decile conversion: {top_decile_rate:.2%}")
print(f"Top-decile concentration: {lift:.2f}x")
