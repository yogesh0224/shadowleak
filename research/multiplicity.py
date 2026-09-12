"""Multiple-comparison helpers for confirmatory subgroup analyses."""

from __future__ import annotations

from typing import Iterable


def holm_bonferroni(pvalues: Iterable[float]) -> list[float]:
    """Return Holm-adjusted p-values in original order."""
    values = [float(value) for value in pvalues]
    if any(value < 0 or value > 1 for value in values):
        raise ValueError("p-values must be between 0 and 1")
    m = len(values)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda index: values[index])
    adjusted_sorted = []
    running = 0.0
    for rank, index in enumerate(order):
        adjusted = min(1.0, (m - rank) * values[index])
        running = max(running, adjusted)
        adjusted_sorted.append((index, running))
    result = [0.0] * m
    for index, adjusted in adjusted_sorted:
        result[index] = adjusted
    return result


def adjust_named_pvalues(named: dict[str, float], method: str = "holm") -> dict[str, dict[str, float]]:
    """Adjust a named family of p-values with a pre-specified method."""
    if method != "holm":
        raise ValueError("Only holm correction is currently supported")
    names = list(named)
    adjusted = holm_bonferroni(named[name] for name in names)
    return {
        name: {"raw_pvalue": float(named[name]), "adjusted_pvalue": adjusted[index]}
        for index, name in enumerate(names)
    }
