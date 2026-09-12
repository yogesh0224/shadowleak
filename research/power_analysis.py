"""Pre-study sample-size planning for paired binary leakage outcomes."""

from __future__ import annotations

import argparse
import json
import math
import random
from statistics import NormalDist, mean, stdev


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


def simulated_cluster_power(
    *,
    record_count: int,
    pairs_per_record: int = 27,
    no_defense_leakage: float = 0.15,
    defended_leakage: float = 0.10,
    record_latent_share: float = 0.40,
    pair_latent_share: float = 0.20,
    alpha: float = 0.05,
    iterations: int = 2000,
    seed: int = 42,
) -> dict[str, float | int]:
    """Estimate power while preserving within-record and within-pair dependence.

    Binary outcomes arise from a latent Gaussian construction. A record-level
    component induces correlation among prompts for the same synthetic identity,
    and a pair-level component correlates defended/undefended outcomes for the
    same prompt. This is a planning model, not an empirical claim about true ICC.
    """
    if record_count < 2 or pairs_per_record < 1:
        raise ValueError("record_count >= 2 and pairs_per_record >= 1 are required")
    for name, value in {
        "no_defense_leakage": no_defense_leakage,
        "defended_leakage": defended_leakage,
        "record_latent_share": record_latent_share,
        "pair_latent_share": pair_latent_share,
    }.items():
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1")
    if record_latent_share + pair_latent_share >= 1:
        raise ValueError("latent shares must sum to less than 1")
    if defended_leakage >= no_defense_leakage:
        raise ValueError("Planning alternative requires lower defended leakage")
    if iterations < 100:
        raise ValueError("iterations must be at least 100")

    rng = random.Random(seed)
    threshold_none = NormalDist().inv_cdf(no_defense_leakage)
    threshold_defended = NormalDist().inv_cdf(defended_leakage)
    critical = NormalDist().inv_cdf(1 - alpha / 2)
    residual_share = 1 - record_latent_share - pair_latent_share
    rejections = 0

    for _ in range(iterations):
        record_differences: list[float] = []
        for _record in range(record_count):
            record_latent = rng.gauss(0, 1)
            leaks_none = 0
            leaks_defended = 0
            for _pair in range(pairs_per_record):
                pair_latent = rng.gauss(0, 1)
                none_latent = (
                    math.sqrt(record_latent_share) * record_latent
                    + math.sqrt(pair_latent_share) * pair_latent
                    + math.sqrt(residual_share) * rng.gauss(0, 1)
                )
                defended_latent = (
                    math.sqrt(record_latent_share) * record_latent
                    + math.sqrt(pair_latent_share) * pair_latent
                    + math.sqrt(residual_share) * rng.gauss(0, 1)
                )
                leaks_none += int(none_latent < threshold_none)
                leaks_defended += int(defended_latent < threshold_defended)
            record_differences.append(
                (leaks_none - leaks_defended) / pairs_per_record
            )

        average = mean(record_differences)
        standard_error = stdev(record_differences) / math.sqrt(record_count)
        if standard_error > 0 and average / standard_error > critical:
            rejections += 1

    return {
        "record_count": record_count,
        "pairs_per_record": pairs_per_record,
        "no_defense_leakage": no_defense_leakage,
        "defended_leakage": defended_leakage,
        "minimum_absolute_effect": no_defense_leakage - defended_leakage,
        "record_latent_share": record_latent_share,
        "pair_latent_share": pair_latent_share,
        "alpha": alpha,
        "iterations": iterations,
        "seed": seed,
        "estimated_power": rejections / iterations,
    }


def minimum_records_by_simulation(
    *,
    candidates: list[int],
    target_power: float = 0.80,
    **kwargs,
) -> dict[str, object]:
    """Return the first candidate meeting target power under fixed assumptions."""
    if not candidates:
        raise ValueError("At least one candidate record count is required")
    results = [
        simulated_cluster_power(record_count=count, **kwargs)
        for count in sorted(set(candidates))
    ]
    qualifying = [
        result for result in results
        if float(result["estimated_power"]) >= target_power
    ]
    return {
        "target_power": target_power,
        "recommended_record_count": (
            int(qualifying[0]["record_count"]) if qualifying else None
        ),
        "results": results,
        "evidence_boundary": (
            "Planning simulation under stated latent-correlation assumptions; "
            "not an estimate of the benchmark's true intraclass correlation."
        ),
    }
