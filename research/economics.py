"""Economic sensitivity analysis for privacy, utility, and latency trade-offs."""

from __future__ import annotations

from itertools import product
from typing import Any, Iterable


def _condition_metrics(report: dict[str, Any], condition: str) -> dict[str, float]:
    leakage = report["attack_leakage"]["by_defense"].get(condition, {}).get("rate")
    utility = (
        report.get("benign_utility", {})
        .get("detailed_composite_by_defense", {})
        .get(condition, {})
        .get("mean")
    )
    latency = (
        report.get("benign_utility", {})
        .get("detailed_composite_by_defense", {})
        .get(condition, {})
        .get("latency", {})
        .get("mean_ms")
    )
    if leakage is None or utility is None:
        raise ValueError(f"Condition {condition} lacks leakage or utility evidence")
    return {
        "leakage_rate": float(leakage),
        "utility": float(utility),
        "latency_ms": float(latency or 0.0),
    }


def total_social_cost(
    metrics: dict[str, float],
    *,
    leakage_cost: float,
    utility_loss_cost: float,
    latency_cost_per_ms: float = 0.0,
) -> float:
    """Return a transparent normalized cost under one explicit weight vector."""
    if min(leakage_cost, utility_loss_cost, latency_cost_per_ms) < 0:
        raise ValueError("Cost weights must be non-negative")
    return (
        leakage_cost * metrics["leakage_rate"]
        + utility_loss_cost * (1 - metrics["utility"])
        + latency_cost_per_ms * metrics["latency_ms"]
    )


def compare_conditions(
    report: dict[str, Any],
    *,
    leakage_cost: float,
    utility_loss_cost: float,
    latency_cost_per_ms: float = 0.0,
    conditions: tuple[str, ...] = ("none", "guardshield-v1"),
) -> dict[str, Any]:
    costs: dict[str, float] = {}
    metrics: dict[str, dict[str, float]] = {}
    for condition in conditions:
        condition_metrics = _condition_metrics(report, condition)
        metrics[condition] = condition_metrics
        costs[condition] = total_social_cost(
            condition_metrics,
            leakage_cost=leakage_cost,
            utility_loss_cost=utility_loss_cost,
            latency_cost_per_ms=latency_cost_per_ms,
        )
    best_cost = min(costs.values())
    preferred = sorted(
        condition for condition, cost in costs.items() if abs(cost - best_cost) < 1e-12
    )
    return {
        "weights": {
            "leakage_cost": leakage_cost,
            "utility_loss_cost": utility_loss_cost,
            "latency_cost_per_ms": latency_cost_per_ms,
        },
        "condition_metrics": metrics,
        "condition_costs": costs,
        "preferred_conditions": preferred,
        "tie": len(preferred) > 1,
    }


def sensitivity_grid(
    report: dict[str, Any],
    *,
    leakage_costs: Iterable[float],
    utility_loss_costs: Iterable[float],
    latency_costs_per_ms: Iterable[float] = (0.0,),
    conditions: tuple[str, ...] = ("none", "guardshield-v1"),
) -> dict[str, Any]:
    """Evaluate preferred configurations across a preregisterable weight grid."""
    scenarios = [
        compare_conditions(
            report,
            leakage_cost=leakage,
            utility_loss_cost=utility,
            latency_cost_per_ms=latency,
            conditions=conditions,
        )
        for leakage, utility, latency in product(
            leakage_costs, utility_loss_costs, latency_costs_per_ms
        )
    ]
    if not scenarios:
        raise ValueError("Sensitivity grid must contain at least one scenario")

    preference_counts: dict[str, int] = {condition: 0 for condition in conditions}
    tie_count = 0
    for scenario in scenarios:
        if scenario["tie"]:
            tie_count += 1
        for condition in scenario["preferred_conditions"]:
            preference_counts[condition] += 1

    return {
        "schema_version": "shadowleak.economic-sensitivity.v1",
        "interpretation_notice": (
            "Weights are analyst- or stakeholder-supplied preference parameters, "
            "not market prices or objectively correct social values."
        ),
        "scenario_count": len(scenarios),
        "preference_counts": preference_counts,
        "tie_count": tie_count,
        "scenarios": scenarios,
    }
