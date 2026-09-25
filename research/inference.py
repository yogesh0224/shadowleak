"""Cluster-aware inference for repeated-record benchmark observations."""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Any


def _complete_pair_rows(rows: list[dict[str, Any]], *, cluster_field: str) -> list[dict[str, Any]]:
    """Retain only complete, unique two-condition pairs within one record.

    This enforces the frozen protocol's incomplete-pair exclusion *before*
    calculating condition rates or sampling record clusters. An incomplete
    pair is excluded from both arms rather than contributing a single arm.
    """
    pairs: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    pair_cluster: dict[str, str] = {}
    for row in rows:
        if cluster_field not in row or not str(row[cluster_field]):
            raise ValueError(f"Missing cluster field: {cluster_field}")
        pair_id = str(row.get("pair_id", ""))
        if not pair_id:
            raise ValueError("Missing pair_id")
        cluster = str(row[cluster_field])
        if pair_id in pair_cluster and pair_cluster[pair_id] != cluster:
            raise ValueError(f"Pair {pair_id} belongs to multiple record clusters")
        pair_cluster[pair_id] = cluster
        condition = str(row["defense_condition"])
        if condition not in {"none", "guardshield-v1"}:
            raise ValueError(f"Unexpected defense condition: {condition}")
        if condition in pairs[pair_id]:
            raise ValueError(f"Duplicate {condition} observation for pair {pair_id}")
        pairs[pair_id][condition] = row

    return [
        condition_row
        for pair in pairs.values()
        if set(pair) == {"none", "guardshield-v1"}
        for condition_row in (pair["none"], pair["guardshield-v1"])
    ]


def _paired_record_effect(rows: list[dict[str, Any]], *, outcome_field: str, cluster_field: str) -> dict[str, float]:
    """Compute equal-record-weighted condition rates on identical complete pairs."""
    by_cluster: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for row in _complete_pair_rows(rows, cluster_field=cluster_field):
        cluster = str(row[cluster_field])
        condition = str(row["defense_condition"])
        by_cluster[cluster][condition].append(int(row[outcome_field]))

    if not by_cluster:
        raise ValueError("No complete pairs available for paired inference")

    none_cluster_rates = [sum(values["none"]) / len(values["none"]) for values in by_cluster.values()]
    guard_cluster_rates = [sum(values["guardshield-v1"]) / len(values["guardshield-v1"]) for values in by_cluster.values()]
    none_rate = sum(none_cluster_rates) / len(none_cluster_rates)
    guard_rate = sum(guard_cluster_rates) / len(guard_cluster_rates)
    return {
        "cluster_count": float(len(by_cluster)),
        "no_defense_rate": none_rate,
        "guardshield_rate": guard_rate,
        "guardshield_minus_no_defense": guard_rate - none_rate,
        "no_defense_minus_guardshield": none_rate - guard_rate,
    }


def cluster_bootstrap_paired_difference(
    rows: list[dict[str, Any]],
    *,
    outcome_field: str,
    cluster_field: str = "record_id",
    iterations: int = 5000,
    seed: int = 42,
    confidence: float = 0.95,
) -> dict[str, Any]:
    """Bootstrap a paired condition difference by resampling whole records.

    Repeated prompts for the same synthetic record are correlated. Resampling
    record IDs rather than prompt rows keeps that dependence intact and avoids
    treating every prompt as an independent experimental unit.
    """
    if iterations < 100:
        raise ValueError("iterations must be at least 100")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")

    by_cluster: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in _complete_pair_rows(rows, cluster_field=cluster_field):
        by_cluster[str(row[cluster_field])].append(row)

    cluster_ids = sorted(by_cluster)
    if len(cluster_ids) < 2:
        raise ValueError("At least two clusters are required for cluster bootstrap")

    observed = _paired_record_effect(rows, outcome_field=outcome_field, cluster_field=cluster_field)
    rng = random.Random(seed)
    draws: list[float] = []
    for _ in range(iterations):
        sampled_rows: list[dict[str, Any]] = []
        for draw_index in range(len(cluster_ids)):
            selected = rng.choice(cluster_ids)
            synthetic_cluster = f"bootstrap_{draw_index}"
            for row in by_cluster[selected]:
                copied = dict(row)
                copied[cluster_field] = synthetic_cluster
                copied["pair_id"] = f"{synthetic_cluster}:{row['pair_id']}"
                sampled_rows.append(copied)
        effect = _paired_record_effect(sampled_rows, outcome_field=outcome_field, cluster_field=cluster_field)
        draws.append(effect["no_defense_minus_guardshield"])

    draws.sort()
    alpha = 1 - confidence
    low_index = max(0, int((alpha / 2) * iterations))
    high_index = min(iterations - 1, int((1 - alpha / 2) * iterations) - 1)
    return {
        "method": "record_cluster_percentile_bootstrap",
        "cluster_field": cluster_field,
        "clusters": len(cluster_ids),
        "iterations": iterations,
        "seed": seed,
        "confidence": confidence,
        "estimand": "no_defense_minus_guardshield",
        "estimate": observed["no_defense_minus_guardshield"],
        "ci": [draws[low_index], draws[high_index]],
        "condition_rates": {"none": observed["no_defense_rate"], "guardshield-v1": observed["guardshield_rate"]},
    }
