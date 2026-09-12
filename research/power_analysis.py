"""Pre-study sample-size planning for paired binary leakage outcomes."""

from __future__ import annotations

import argparse
import json
import math
from statistics import NormalDist


def required_paired_cases(
    *,
    prevented_probability: float,
    induced_probability: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> dict[str, float | int]:
    """Approximate required matched pairs for a two-sided McNemar design.

    prevented_probability is P(no-defense leak=1, defense leak=0).
    induced_probability is P(no-defense leak=0, defense leak=1).

    This is an asymptotic planning approximation. Confirmatory analysis can
    still use the exact McNemar test. Repeated-record designs should additionally
    account for clustering before the final study plan is frozen.
    """
    for name, value in {
        "prevented_probability": prevented_probability,
        "induced_probability": induced_probability,
    }.items():
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1")
    if prevented_probability + induced_probability > 1:
        raise ValueError("Discordant probabilities cannot sum to more than 1")
    if prevented_probability == induced_probability:
        raise ValueError("A non-zero discordant-pair difference is required")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")
    if not 0 < power < 1:
        raise ValueError("power must be between 0 and 1")

    discordant = prevented_probability + induced_probability
    effect = abs(prevented_probability - induced_probability)
    z_alpha = NormalDist().inv_cdf(1 - alpha / 2)
    z_power = NormalDist().inv_cdf(power)
    variance_alt = max(discordant - effect * effect, 0.0)
    numerator = (z_alpha * math.sqrt(discordant) + z_power * math.sqrt(variance_alt)) ** 2
    required = math.ceil(numerator / (effect * effect))
    return {
        "required_matched_pairs": required,
        "alpha": alpha,
        "power": power,
        "prevented_probability": prevented_probability,
        "induced_probability": induced_probability,
        "discordant_probability": discordant,
        "absolute_discordant_difference": effect,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prevented", type=float, required=True)
    parser.add_argument("--induced", type=float, required=True)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--power", type=float, default=0.80)
    args = parser.parse_args()
    print(json.dumps(required_paired_cases(
        prevented_probability=args.prevented,
        induced_probability=args.induced,
        alpha=args.alpha,
        power=args.power,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
