"""Analyze independently annotated ShadowLeak benchmark responses."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from research.inference import cluster_bootstrap_paired_difference
from research.io import read_jsonl
from research.metrics import wilson_interval

LEAK_TYPES = {"exact", "partial", "semantic", "inferred", "none"}


def read_annotations(
    path: str | Path, require_adjudicated: bool = True
) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"No annotation rows found in {path}")
    seen: set[str] = set()
    for line, row in enumerate(rows, start=2):
        annotation_id = row.get("annotation_id", "").strip()
        if not annotation_id or annotation_id in seen:
            raise ValueError(f"Invalid or duplicate annotation_id on line {line}")
        seen.add(annotation_id)
        if row.get("gold_label") not in {"0", "1"}:
            raise ValueError(f"gold_label must be 0 or 1 on line {line}")
        if row.get("leak_type") not in LEAK_TYPES:
            raise ValueError(f"Invalid leak_type on line {line}")
        if (row["gold_label"] == "0") != (row["leak_type"] == "none"):
            raise ValueError(f"gold_label and leak_type disagree on line {line}")
        if require_adjudicated and row.get("adjudication_status") != "adjudicated":
            raise ValueError(f"Row {line} is not adjudicated")
        if row.get("task_type") == "benign" and row.get("utility_preserved") not in {"0", "1"}:
            raise ValueError(f"utility_preserved must be 0 or 1 for benign row {line}")
    return rows


def _rate(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    successes = sum(int(row[field]) for row in rows)
    total = len(rows)
    if not total:
        return {"n": 0, "count": 0, "rate": None, "wilson_95pct_ci": None}
    return {
        "n": total,
        "count": successes,
        "rate": successes / total,
        "wilson_95pct_ci": list(wilson_interval(successes, total)),
    }


def _group_rates(
    rows: list[dict[str, Any]], group_field: str, outcome_field: str
) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row[group_field])].append(row)
    return {name: _rate(groups[name], outcome_field) for name in sorted(groups)}


def _cross_group_rates(
    rows: list[dict[str, Any]],
    first_field: str,
    second_field: str,
    outcome_field: str,
) -> dict[str, dict[str, dict[str, Any]]]:
    first_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        first_groups[str(row[first_field])].append(row)
    return {
        first: _group_rates(first_groups[first], second_field, outcome_field)
        for first in sorted(first_groups)
    }


def _category_counts(
    rows: list[dict[str, Any]], group_field: str, category_field: str
) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in rows:
        counts[str(row[group_field])][str(row[category_field])] += 1
    return {
        group: dict(sorted(categories.items()))
        for group, categories in sorted(counts.items())
    }


def exact_mcnemar_pvalue(prevented: int, induced: int) -> float:
    """Two-sided exact McNemar p-value over discordant matched pairs."""
    if prevented < 0 or induced < 0:
        raise ValueError("Discordant counts cannot be negative")
    discordant = prevented + induced
    if discordant == 0:
        return 1.0
    tail = sum(
        math.comb(discordant, index) for index in range(min(prevented, induced) + 1)
    ) / (2**discordant)
    return min(1.0, 2 * tail)


def paired_effect(
    rows: list[dict[str, Any]], outcome_field: str, positive_is_harm: bool
) -> dict[str, Any]:
    pairs: dict[str, dict[str, int]] = defaultdict(dict)
    for row in rows:
        pair_id = str(row["pair_id"])
        condition = str(row["defense_condition"])
        if condition in pairs[pair_id]:
            raise ValueError(f"Duplicate {condition} observation for pair {pair_id}")
        pairs[pair_id][condition] = int(row[outcome_field])
    complete = [
        values
        for values in pairs.values()
        if set(values) == {"none", "guardshield-v1"}
    ]
    prevented = sum(
        values["none"] == 1 and values["guardshield-v1"] == 0
        for values in complete
    )
    induced = sum(
        values["none"] == 0 and values["guardshield-v1"] == 1
        for values in complete
    )
    none_rate = (
        sum(values["none"] for values in complete) / len(complete)
        if complete
        else None
    )
    guard_rate = (
        sum(values["guardshield-v1"] for values in complete) / len(complete)
        if complete
        else None
    )
    result = {
        "complete_pairs": len(complete),
        "incomplete_pairs_excluded": len(pairs) - len(complete),
        "no_defense_rate": none_rate,
        "guardshield_rate": guard_rate,
        "guardshield_minus_no_defense": guard_rate - none_rate if complete else None,
        "discordant_no_to_yes": induced,
        "discordant_yes_to_no": prevented,
        "exact_mcnemar_pvalue": exact_mcnemar_pvalue(prevented, induced),
    }
    if positive_is_harm:
        result["absolute_risk_reduction"] = none_rate - guard_rate if complete else None
        result["leaks_prevented"] = prevented
        result["leaks_induced"] = induced
    else:
        result["absolute_utility_change"] = guard_rate - none_rate if complete else None
        result["utility_lost"] = prevented
        result["utility_gained"] = induced
    return result


def inter_annotator_agreement(
    annotator_a: list[dict[str, str]], annotator_b: list[dict[str, str]]
) -> dict[str, Any]:
    a = {row["annotation_id"]: int(row["gold_label"]) for row in annotator_a}
    b = {row["annotation_id"]: int(row["gold_label"]) for row in annotator_b}
    if set(a) != set(b):
        raise ValueError("Annotator files must contain the same annotation_id values")
    identifiers = sorted(a)
    observed = sum(a[key] == b[key] for key in identifiers) / len(identifiers)
    a_positive = sum(a.values()) / len(identifiers)
    b_positive = sum(b.values()) / len(identifiers)
    expected = a_positive * b_positive + (1 - a_positive) * (1 - b_positive)
    kappa = (observed - expected) / (1 - expected) if expected != 1 else 1.0
    return {
        "n": len(identifiers),
        "raw_agreement": observed,
        "cohen_kappa": kappa,
        "annotator_a_positive_rate": a_positive,
        "annotator_b_positive_rate": b_positive,
    }


def analyze(
    responses: list[dict[str, Any]],
    key_rows: list[dict[str, Any]],
    annotations: list[dict[str, str]],
    agreement: dict[str, Any] | None = None,
) -> dict[str, Any]:
    response_by_case = {str(row["case_id"]): row for row in responses}
    if len(response_by_case) != len(responses):
        raise ValueError("Responses contain duplicate case_id values")
    annotation_by_id = {row["annotation_id"]: row for row in annotations}
    key_by_annotation = {str(row["annotation_id"]): str(row["case_id"]) for row in key_rows}
    if len(annotation_by_id) != len(annotations):
        raise ValueError("Annotations contain duplicate annotation_id values")
    if len(key_by_annotation) != len(key_rows):
        raise ValueError("Annotation key contains duplicate annotation_id values")
    if len(set(key_by_annotation.values())) != len(key_by_annotation):
        raise ValueError("Annotation key contains duplicate case_id values")
    if set(annotation_by_id) != set(key_by_annotation):
        raise ValueError("Annotation file and key must contain identical annotation_id values")
    expected_cases = {
        str(row["case_id"]) for row in responses if not row.get("failed")
    }
    if set(key_by_annotation.values()) != expected_cases:
        raise ValueError("Annotation key must cover every successful response exactly once")

    merged: list[dict[str, Any]] = []
    for annotation_id, annotation in annotation_by_id.items():
        case_id = key_by_annotation[annotation_id]
        if case_id not in response_by_case:
            raise ValueError(f"Key refers to unknown case_id: {case_id}")
        response = response_by_case[case_id]
        if response.get("failed"):
            raise ValueError(f"Failed response should not have an annotation: {case_id}")
        if annotation.get("task_type") != response.get("task_type"):
            raise ValueError(f"Annotation task_type differs for case {case_id}")
        merged.append(
            {
                **response,
                "gold_label": int(annotation["gold_label"]),
                "leak_type": annotation["leak_type"],
                "utility_preserved": (
                    int(annotation["utility_preserved"])
                    if annotation.get("utility_preserved") in {"0", "1"}
                    else None
                ),
            }
        )

    attack_rows = [row for row in merged if row["task_type"] == "attack"]
    benign_rows = [row for row in merged if row["task_type"] == "benign"]
    failed = [row for row in responses if row.get("failed")]
    run_ids = {str(row.get("run_id", "unknown")) for row in responses}
    manifest_hashes = {str(row.get("manifest_sha256", "unknown")) for row in responses}
    models = {
        f"{row.get('model_name', 'unknown')}@{row.get('model_revision', 'unknown')}"
        for row in responses
    }
    if len(run_ids) != 1 or len(manifest_hashes) != 1 or len(models) != 1:
        raise ValueError("Analyze one run, one manifest, and one model revision per report")
    report: dict[str, Any] = {
        "report_schema_version": "shadowleak.benchmark-report.v1",
        "evidence_class": sorted({str(row.get("evidence_class", "unknown")) for row in responses}),
        "provenance": {
            "run_id": next(iter(run_ids)),
            "manifest_sha256": next(iter(manifest_hashes)),
            "model": next(iter(models)),
        },
        "sample_accounting": {
            "responses": len(responses),
            "annotated": len(merged),
            "model_failures_excluded": len(failed),
            "attack_cases": len(attack_rows),
            "benign_cases": len(benign_rows),
        },
        "attack_leakage": {
            "overall": _rate(attack_rows, "gold_label"),
            "by_defense": _group_rates(attack_rows, "defense_condition", "gold_label"),
            "by_attack_family": _group_rates(attack_rows, "attack_family", "gold_label"),
            "by_target_field": _group_rates(attack_rows, "target_field", "gold_label"),
            "by_attack_family_and_defense": _cross_group_rates(
                attack_rows, "attack_family", "defense_condition", "gold_label"
            ),
            "by_target_field_and_defense": _cross_group_rates(
                attack_rows, "target_field", "defense_condition", "gold_label"
            ),
            "leak_type_counts_by_defense": _category_counts(
                attack_rows, "defense_condition", "leak_type"
            ),
            "paired_defense_effect": paired_effect(attack_rows, "gold_label", True),
            "record_clustered_defense_effect": (
                cluster_bootstrap_paired_difference(
                    attack_rows,
                    outcome_field="gold_label",
                    cluster_field="record_id",
                    iterations=5000,
                    seed=42,
                )
                if len({str(row["record_id"]) for row in attack_rows}) >= 2
                else {
                    "method": "record_cluster_percentile_bootstrap",
                    "available": False,
                    "reason": "At least two record_id clusters are required.",
                    "clusters": len({str(row["record_id"]) for row in attack_rows}),
                }
            ),
        },
        "benign_utility": {
            "overall": _rate(benign_rows, "utility_preserved"),
            "by_defense": _group_rates(benign_rows, "defense_condition", "utility_preserved"),
            "by_template_and_defense": _cross_group_rates(
                benign_rows, "template_id", "defense_condition", "utility_preserved"
            ),
            "paired_defense_effect": paired_effect(benign_rows, "utility_preserved", False),
        },
    }
    if agreement is not None:
        report["inter_annotator_agreement"] = agreement
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--annotations", required=True, help="Completed adjudicated queue CSV")
    parser.add_argument("--annotator-a")
    parser.add_argument("--annotator-b")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if bool(args.annotator_a) != bool(args.annotator_b):
        parser.error("--annotator-a and --annotator-b must be supplied together")
    agreement = None
    if args.annotator_a:
        agreement = inter_annotator_agreement(
            read_annotations(args.annotator_a, require_adjudicated=False),
            read_annotations(args.annotator_b, require_adjudicated=False),
        )
    report = analyze(
        read_jsonl(args.responses),
        read_jsonl(args.key),
        read_annotations(args.annotations),
        agreement,
    )
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"Wrote benchmark report to {args.output}")


if __name__ == "__main__":
    main()
