
"""
Nectr x Instamart — RICE Prioritization

Compares three product-surface options using illustrative planning assumptions.
Synthetic model results inform the product hypothesis but do not establish
causal impact or validated RICE confidence.

All data and model results in this portfolio project are synthetic.
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

SCORES_PATH = DATA_DIR / "heldout_first_nectr_scores.csv"
METRICS_PATH = DATA_DIR / "first_nectr_model_metrics.csv"
OUTPUT_PATH = DATA_DIR / "rice_scoring.csv"

for path in [SCORES_PATH, METRICS_PATH]:
    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path}\n"
            "Run generate_data.py and clustering_and_propensity.py first."
        )

scores = pd.read_csv(SCORES_PATH)
metrics = pd.read_csv(METRICS_PATH)

required_score_columns = {
    "user_id",
    "actual_first_nectr_purchase",
    "score_rank",
}
if not required_score_columns.issubset(scores.columns):
    missing = required_score_columns - set(scores.columns)
    raise ValueError(f"Missing score columns: {sorted(missing)}")

if scores.empty:
    raise ValueError("Held-out scores file is empty.")

# Use the same top-decile definition as the dashboard.
import math

top_decile_count = max(1, math.ceil(len(scores) * 0.10))
top_decile = scores.nsmallest(top_decile_count, "score_rank")

heldout_users = len(scores)
top_decile_users = len(top_decile)
baseline_rate = scores["actual_first_nectr_purchase"].mean()
top_decile_rate = top_decile["actual_first_nectr_purchase"].mean()
concentration = top_decile_rate / baseline_rate if baseline_rate > 0 else 0

print("=" * 72)
print("NECTR x INSTAMART — RICE PRIORITIZATION")
print("SYNTHETIC DATA | PLANNING ASSUMPTIONS, NOT MEASURED BUSINESS OUTCOMES")
print("=" * 72)

print("\nHELD-OUT MODEL RESULTS")
print(f"Held-out users: {heldout_users:,}")
print(f"Top-decile users: {top_decile_users:,}")
print(f"Held-out baseline conversion: {baseline_rate:.2%}")
print(f"Top-decile conversion: {top_decile_rate:.2%}")
print(f"Top-decile concentration: {concentration:.2f}x")
print(
    "\nThese are descriptive results from one synthetic test split. "
    "They do not measure causal impact."
)

# RICE formula:
# Reach × Impact × Confidence / Effort
#
# All reach, impact, confidence, and effort values below are illustrative
# planning inputs. Replace them with stakeholder-validated estimates before
# using them for an actual business decision.

rice_data = {
    "Option": [
        "A: Personalized rail",
        "B: Dedicated premium tab",
        "C: Standalone premium surface/app",
    ],
    "Reach (assumed users/quarter)": [
        574,
        5731,
        859,
    ],
    "Impact (assumed 0.25/0.5/1/2/3)": [
        2,
        1,
        3,
    ],
    "Confidence (assumed %)": [
        80,
        50,
        30,
    ],
    "Effort (assumed person-months)": [
        1.5,
        4,
        9,
    ],
}

rice_df = pd.DataFrame(rice_data)

rice_df["RICE Score"] = (
    rice_df["Reach (assumed users/quarter)"]
    * rice_df["Impact (assumed 0.25/0.5/1/2/3)"]
    * (rice_df["Confidence (assumed %)"] / 100)
    / rice_df["Effort (assumed person-months)"]
).round(0).astype(int)

rice_df = rice_df.sort_values("RICE Score", ascending=False)

print("\n" + "=" * 72)
print("ILLUSTRATIVE RICE SCORES")
print("=" * 72)
print(rice_df.to_string(index=False))

print(
    """
INTERPRETATION

Option A — Personalized rail
A relatively contained first experiment using the existing feed, subject to
engineering feasibility. The synthetic top-decile concentration motivates
testing targeted discovery; it does not justify an 80% evidence-based
confidence claim or prove incremental purchase lift.

Option B — Dedicated tab
Offers broader reach and a distinct destination, but actual adoption,
implementation effort, and brand impact remain unvalidated.

Option C — Standalone surface/app
Could offer greater brand separation, but the assumed reach, impact, and
effort require validation. It is the most substantial product commitment.

RECOMMENDATION
Consider testing Option A first as a smaller, reversible product hypothesis.
The raw RICE ranking favours Option B under the assumptions above. The
difference should be resolved through stakeholder validation and experiment
evidence, not by presenting assumed confidence values as measured facts.
"""
)

rice_df.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved: {OUTPUT_PATH}")
print("Reminder: all RICE inputs are illustrative planning assumptions.")
