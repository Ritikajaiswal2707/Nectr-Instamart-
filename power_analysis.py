"""Illustrative sample size for the personalised-rail A/B test.

Two-sided test of two proportions, alpha = 0.05, power = 0.80.
Baseline is the synthetic 30-day first-purchase rate (2.97%); a real
test must use the real baseline.
"""
import math

ALPHA_Z = 1.96      # two-sided alpha 0.05
POWER_Z = 0.8416    # power 0.80
BASELINE = 0.0297

def users_per_arm(p1: float, p2: float) -> int:
    p_bar = (p1 + p2) / 2
    num = (ALPHA_Z * math.sqrt(2 * p_bar * (1 - p_bar))
           + POWER_Z * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / (p2 - p1) ** 2)

if __name__ == "__main__":
    print("Relative lift | Treatment rate | Users per arm")
    for lift in (0.10, 0.20, 0.30):
        p2 = BASELINE * (1 + lift)
        print(f"{lift:>12.0%} | {p2:>14.2%} | {users_per_arm(BASELINE, p2):>13,}")
