"""
Instamart Nectr — Dashboard Visualizations
Builds the key charts a Power BI dashboard would show, using the real
clustering/propensity results. Saved as PNGs since Power BI itself isn't
available in this environment — these are the exact charts to recreate
there if uploading the underlying CSVs.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

df = pd.read_csv("/home/claude/instamart/data/user_segments_with_propensity.csv")
rice_df = pd.read_csv("/home/claude/instamart/data/rice_scoring.csv")

COLOR_PRIMARY = "#2F6F63"
COLOR_SECONDARY = "#C9A227"
COLOR_MUTED = "#9BA6A0"
COLOR_ACCENT = "#B5563C"

fig, axes = plt.subplots(2, 2, figsize=(13, 10))
fig.suptitle("Instamart Nectr — Premium Targeting Dashboard", fontsize=16, fontweight="bold", y=0.98)

# ---------------------------------------------------------------------------
# CHART 1: Persona distribution (merging the two Value Shopper clusters, per
# the documented limitation)
# ---------------------------------------------------------------------------
persona_counts = df["persona_label"].value_counts()
ax1 = axes[0, 0]
colors1 = [COLOR_PRIMARY if "Premium" in p and "Occasional" not in p
           else COLOR_SECONDARY if "Occasional" in p
           else COLOR_MUTED for p in persona_counts.index]
bars1 = ax1.barh(persona_counts.index, persona_counts.values, color=colors1)
ax1.set_title("User Personas (n=5,731 active users)", fontweight="bold", fontsize=12)
ax1.set_xlabel("Number of users")
for bar, val in zip(bars1, persona_counts.values):
    ax1.text(val + 50, bar.get_y() + bar.get_height()/2, f"{val:,} ({val/len(df):.0%})",
             va="center", fontsize=9)
ax1.set_xlim(0, max(persona_counts.values) * 1.25)

# ---------------------------------------------------------------------------
# CHART 2: Propensity concentration — the headline number
# ---------------------------------------------------------------------------
ax2 = axes[0, 1]
top_decile_threshold = df["propensity_score"].quantile(0.90)
top_decile = df[df["propensity_score"] >= top_decile_threshold]
overall_rate = df["will_buy_premium_future"].mean()
top_decile_rate = top_decile["will_buy_premium_future"].mean()

bars2 = ax2.bar(
    ["All Active Users\n(n=5,731)", "Top-Decile Propensity\nSegment (n=574)"],
    [overall_rate * 100, top_decile_rate * 100],
    color=[COLOR_MUTED, COLOR_PRIMARY],
    width=0.5
)
ax2.set_title("Premium Adoption Rate — 2.8x Concentration", fontweight="bold", fontsize=12)
ax2.set_ylabel("% who buy premium (next 30 days)")
ax2.yaxis.set_major_formatter(mticker.PercentFormatter())
for bar, val in zip(bars2, [overall_rate * 100, top_decile_rate * 100]):
    ax2.text(bar.get_x() + bar.get_width()/2, val + 1, f"{val:.1f}%",
              ha="center", fontweight="bold", fontsize=11)
ax2.set_ylim(0, max(overall_rate, top_decile_rate) * 100 * 1.3)

# ---------------------------------------------------------------------------
# CHART 3: Persona profile — AOV vs Premium Share (bubble = user count)
# ---------------------------------------------------------------------------
ax3 = axes[1, 0]
profile = df.groupby("persona_label").agg(
    avg_order_value=("avg_order_value", "mean"),
    premium_share=("premium_item_share", "mean"),
    n_users=("user_id", "count")
).reset_index()

persona_colors = {"Value Shopper": COLOR_MUTED, "Occasional Premium Explorer": COLOR_SECONDARY,
                   "Premium Explorer / Health-Conscious": COLOR_PRIMARY}
for _, row in profile.iterrows():
    ax3.scatter(row["avg_order_value"], row["premium_share"] * 100,
                s=row["n_users"] / 2, alpha=0.7,
                color=persona_colors.get(row["persona_label"], COLOR_ACCENT),
                edgecolors="white", linewidth=1.5,
                label=row["persona_label"])
    ax3.annotate(row["persona_label"].split("/")[0].strip(),
                 (row["avg_order_value"], row["premium_share"] * 100),
                 xytext=(8, 8), textcoords="offset points", fontsize=8.5)

ax3.set_title("Persona Profile: AOV vs. Premium Share\n(bubble size = user count)", fontweight="bold", fontsize=12)
ax3.set_xlabel("Average Order Value (₹)")
ax3.set_ylabel("Premium item share (%)")

# ---------------------------------------------------------------------------
# CHART 4: RICE comparison — showing the override decision visually
# ---------------------------------------------------------------------------
ax4 = axes[1, 1]
rice_sorted = rice_df.sort_values("RICE Score", ascending=True)
option_labels = [o.split(":")[0] for o in rice_sorted["Option"]]
bar_colors = [COLOR_PRIMARY if "A" in o else COLOR_MUTED for o in option_labels]
bars4 = ax4.barh(option_labels, rice_sorted["RICE Score"], color=bar_colors)
ax4.set_title("RICE Scores — Recommendation Overrides Raw Ranking", fontweight="bold", fontsize=12)
ax4.set_xlabel("RICE Score")
for bar, val in zip(bars4, rice_sorted["RICE Score"]):
    ax4.text(val + 10, bar.get_y() + bar.get_height()/2, f"{val:.0f}", va="center", fontsize=9)
ax4.text(0.98, 0.02, "Recommended: Option A\n(highest confidence, lowest risk)",
          transform=ax4.transAxes, ha="right", va="bottom", fontsize=8.5,
          style="italic", color=COLOR_PRIMARY,
          bbox=dict(boxstyle="round", facecolor="white", edgecolor=COLOR_PRIMARY, alpha=0.9))

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("/home/claude/instamart/dashboard.png", dpi=150, bbox_inches="tight")
print("Saved dashboard.png")
