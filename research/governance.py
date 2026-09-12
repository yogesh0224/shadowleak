"""Evaluate benchmark reports against explicit governance decision profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_profiles(path: str | Path) -> list[dict[str, Any]]:
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    profiles = document.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("Governance profile file must contain a non-empty profiles list")
    return profiles


def _metric(report: dict[str, Any], condition: str) -> dict[str, float | None]:
    leakage = report["attack_leakage"]["by_defense"].get(condition, {}).get("rate")
    utility = (
        report.get("benign_utility", {})
        .get("detailed_composite_by_defense", {})
        .get(condition, {})
        .get("mean")
    )
    over_refusal = (
        report.get("benign_utility", {})
        .get("detailed_composite_by_defense", {})
        .get(condition, {})
        .get("dimensions", {})
        .get("over_refusal", {})
        .get("mean")
    )
    latency = (
        report.get("benign_utility", {})
        .get("detailed_composite_by_defense", {})
        .get(condition, {})
        .get("latency", {})
        .get("mean_ms")
    )
    return {
        "leakage_rate": leakage,
        "mean_utility": utility,
        "over_refusal_rate": over_refusal,
        "mean_latency_ms": latency,
    }


def evaluate_profile(
    report: dict[str, Any],
    profile: dict[str, Any],
    condition: str = "guardshield-v1",
) -> dict[str, Any]:
    """Apply a transparent decision profile to one evaluated configuration."""
    required = {"profile_id", "context", "thresholds", "status"}
    missing = required - profile.keys()
    if missing:
        raise ValueError(f"Governance profile is missing fields: {sorted(missing)}")
    thresholds = profile["thresholds"]
    if not isinstance(thresholds, dict) or not thresholds:
        raise ValueError("Governance profile thresholds must be a non-empty object")

    observed = _metric(report, condition)
    checks: dict[str, dict[str, Any]] = {}

    rules = {
        "max_leakage_rate": ("leakage_rate", "<="),
        "min_mean_utility": ("mean_utility", ">="),
        "max_over_refusal_rate": ("over_refusal_rate", "<="),
        "max_mean_latency_ms": ("mean_latency_ms", "<="),
    }
    for threshold_name, threshold_value in thresholds.items():
        if threshold_name not in rules:
            raise ValueError(f"Unsupported governance threshold: {threshold_name}")
        metric_name, operator = rules[threshold_name]
        actual = observed[metric_name]
        passed = None
        if actual is not None:
            passed = actual <= threshold_value if operator == "<=" else actual >= threshold_value
        checks[threshold_name] = {
            "metric": metric_name,
            "operator": operator,
            "threshold": threshold_value,
            "observed": actual,
            "passed": passed,
        }

    decided = [item["passed"] for item in checks.values() if item["passed"] is not None]
    all_available = len(decided) == len(checks)
    overall = all(decided) if all_available else None
    return {
        "profile_id": profile["profile_id"],
        "context": profile["context"],
        "profile_status": profile["status"],
        "condition": condition,
        "decision": "pass" if overall is True else "fail" if overall is False else "insufficient_evidence",
        "checks": checks,
        "notes": profile.get("notes", ""),
    }


def evaluate_profiles(
    report: dict[str, Any],
    profiles: list[dict[str, Any]],
    condition: str = "guardshield-v1",
) -> dict[str, Any]:
    return {
        "schema_version": "shadowleak.governance-decision.v1",
        "evidence_notice": (
            "Decision profiles encode explicit organizational assumptions; "
            "they do not establish legal compliance, certification, or sector-wide acceptability."
        ),
        "condition": condition,
        "profiles": [evaluate_profile(report, profile, condition) for profile in profiles],
    }
