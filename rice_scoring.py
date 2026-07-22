"""
Instamart Nectr — RICE Scoring
Scores three product options using real numbers from the clustering/propensity
work: reach = actual segment sizes, impact/confidence grounded in the model's
measured lift, effort estimated on relative engineering complexity.
"""

import pandas as pd

df = pd.read_csv("/home/claude/instamart/data/user_segments_with_propensity.csv")

total_active_users = len(df)
top_decile_threshold = df["propensity_score"].quantile(0.90)
top_decile_users = df[df["propensity_score"] >= top_decile_threshold]
premium_explorer_users = df[df["persona_label"] == "Premium Explorer / Health-Conscious"]

overall_adoption = df["will_buy_premium_future"].mean()
top_decile_adoption = top_decile_users["will_buy_premium_future"].mean()
persona_adoption = premium_explorer_users["will_buy_premium_future"].mean()

print("=" * 70)
print("REACH NUMBERS (real, from the dataset)")
print("=" * 70)
print(f"Total active users: {total_active_users}")
print(f"Top-decile propensity segment: {len(top_decile_users)} users ({len(top_decile_users)/total_active_users:.1%})")
print(f"Premium Explorer persona: {len(premium_explorer_users)} users ({len(premium_explorer_users)/total_active_users:.1%})")
print(f"\nOverall premium adoption rate: {overall_adoption:.1%}")
print(f"Top-decile adoption rate: {top_decile_adoption:.1%}")
print(f"Premium Explorer persona adoption rate: {persona_adoption:.1%}")

rice_data = {
    "Option": [
        "A: Personalized rail (top-decile segment only)",
        "B: Dedicated premium tab (all users)",
        "C: Standalone premium surface/app",
    ],
    "Reach (users/quarter)": [
        len(top_decile_users),
        total_active_users,
        int(total_active_users * 0.15),
    ],
    "Impact (0.25/0.5/1/2/3)": [2, 1, 3],
    "Confidence (%)": [80, 50, 30],
    "Effort (person-months)": [1.5, 4, 9],
}

rice_df = pd.DataFrame(rice_data)
rice_df["RICE Score"] = (
    rice_df["Reach (users/quarter)"]
    * rice_df["Impact (0.25/0.5/1/2/3)"]
    * (rice_df["Confidence (%)"] / 100)
    / rice_df["Effort (person-months)"]
).round(0)

rice_df = rice_df.sort_values("RICE Score", ascending=False)

print("\n" + "=" * 70)
print("RICE SCORING")
print("=" * 70)
print(rice_df.to_string(index=False))

print("""
Rationale:
Option A (Personalized rail, top-decile only):
  Reach: real number from the model. Impact: Medium (2) - meaningful lift in a
  small high-intent group. Confidence: High (80%) - grounded in the measured
  2.8x concentration, not a guess. Effort: Low (1.5mo) - reuses existing feed infra.

Option B (Dedicated tab, all users):
  Reach: full active base. Impact: Low (1) - most users are Value Shoppers with
  ~2% premium share, so relevance is diluted. Confidence: Medium (50%) - untested
  at scale, risks brand dilution. Effort: Medium-High (4mo).

Option C (Standalone surface/app):
  Reach: ~15% assumed discovery/download rate - an assumption, stated as such.
  Impact: High (3) - cleanest brand separation. Confidence: Low (30%) - no
  internal precedent. Effort: Very High (9mo) - full separate product surface.
""")

rice_df.to_csv("/home/claude/instamart/data/rice_scoring.csv", index=False)
print("Saved: rice_scoring.csv")
