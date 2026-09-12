"""Blinded double-annotation agreement and adjudication workflow."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from research.annotation_queue import QUEUE_FIELDS
from research.benchmark_analysis import inter_annotator_agreement, read_annotations

STIMULUS_FIELDS = (
    "annotation_id",
    "task_type",
    "prompt",
    "synthetic_context",
    "target_field",
    "protected_value",
    "response",
)

OUTCOME_FIELDS = (
    "gold_label",
    "leak_type",
    "utility_preserved",
    "task_completion",
    "correctness",
    "relevance",
    "over_refusal",
)

ADJUDICATION_FIELDS = (
    *STIMULUS_FIELDS,
    "annotator_a_gold_label",
    "annotator_a_leak_type",
    "annotator_a_utility_preserved",
    "annotator_a_task_completion",
    "annotator_a_correctness",
    "annotator_a_relevance",
    "annotator_a_over_refusal",
    "annotator_a_rationale",
    "annotator_b_gold_label",
    "annotator_b_leak_type",
    "annotator_b_utility_preserved",
    "annotator_b_task_completion",
    "annotator_b_correctness",
    "annotator_b_relevance",
    "annotator_b_over_refusal",
    "annotator_b_rationale",
    "final_gold_label",
    "final_leak_type",
    "final_utility_preserved",
    "final_task_completion",
    "final_correctness",
    "final_relevance",
    "final_over_refusal",
    "adjudicator_id",
    "adjudication_rationale",
)


def _by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    result = {row["annotation_id"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError("Annotation files must not contain duplicate annotation_id values")
    return result


def _validate_same_stimulus(
    annotator_a: list[dict[str, str]], annotator_b: list[dict[str, str]]
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    a = _by_id(annotator_a)
    b = _by_id(annotator_b)
    if set(a) != set(b):
        raise ValueError("Annotator files must contain the same annotation_id values")
    for annotation_id in sorted(a):
        for field in STIMULUS_FIELDS:
            if a[annotation_id].get(field, "") != b[annotation_id].get(field, ""):
                raise ValueError(
                    f"Annotator files disagree on blinded stimulus field {field} "
                    f"for {annotation_id}"
                )
    return a, b


def _relevant_outcomes(row: dict[str, str]) -> tuple[str, ...]:
    if row.get("task_type") == "benign":
        return OUTCOME_FIELDS
    return ("gold_label", "leak_type")


def disagreement_ids(
    annotator_a: list[dict[str, str]], annotator_b: list[dict[str, str]]
) -> list[str]:
    a, b = _validate_same_stimulus(annotator_a, annotator_b)
    return [
        annotation_id
        for annotation_id in sorted(a)
        if any(
            a[annotation_id].get(field, "").strip()
            != b[annotation_id].get(field, "").strip()
            for field in _relevant_outcomes(a[annotation_id])
        )
    ]


def build_adjudication_queue(
    annotator_a: list[dict[str, str]], annotator_b: list[dict[str, str]]
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Return disagreement-only rows without exposing study condition metadata."""
    a, b = _validate_same_stimulus(annotator_a, annotator_b)
    disagreements = set(disagreement_ids(annotator_a, annotator_b))
    queue: list[dict[str, str]] = []
    for annotation_id in sorted(disagreements):
        row_a = a[annotation_id]
        row_b = b[annotation_id]
        output = {field: row_a.get(field, "") for field in STIMULUS_FIELDS}
        for prefix, source in (("annotator_a", row_a), ("annotator_b", row_b)):
            for field in OUTCOME_FIELDS:
                output[f"{prefix}_{field}"] = source.get(field, "")
            output[f"{prefix}_rationale"] = source.get("rationale", "")
        for field in OUTCOME_FIELDS:
            output[f"final_{field}"] = ""
        output["adjudicator_id"] = ""
        output["adjudication_rationale"] = ""
        queue.append(output)

    agreement = inter_annotator_agreement(annotator_a, annotator_b)
    agreement["disagreement_count"] = len(disagreements)
    agreement["disagreement_rate"] = len(disagreements) / len(a)
    agreement["agreement_scope"] = "gold_label"
    return queue, agreement


def _read_decisions(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows and Path(path).stat().st_size:
        return []
    return rows


def _final_outcomes_from_decision(
    decision: dict[str, str], task_type: str, annotation_id: str
) -> dict[str, str]:
    result = {field: decision.get(f"final_{field}", "").strip() for field in OUTCOME_FIELDS}
    if result["gold_label"] not in {"0", "1"}:
        raise ValueError(f"Adjudication {annotation_id} requires final_gold_label 0 or 1")
    if result["leak_type"] not in {"none", "exact", "partial", "semantic", "inferred"}:
        raise ValueError(f"Adjudication {annotation_id} has invalid final_leak_type")
    if (result["gold_label"] == "0") != (result["leak_type"] == "none"):
        raise ValueError(f"Adjudication {annotation_id} has inconsistent leak label/type")

    if task_type == "benign":
        for field in (
            "utility_preserved",
            "task_completion",
            "correctness",
            "relevance",
            "over_refusal",
        ):
            if result[field] not in {"0", "1"}:
                raise ValueError(
                    f"Adjudication {annotation_id} requires final_{field} 0 or 1"
                )
    else:
        for field in (
            "utility_preserved",
            "task_completion",
            "correctness",
            "relevance",
            "over_refusal",
        ):
            result[field] = ""
    return result


def finalize_annotations(
    annotator_a: list[dict[str, str]],
    annotator_b: list[dict[str, str]],
    decisions: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Create one final adjudicated queue from independent files plus decisions."""
    a, b = _validate_same_stimulus(annotator_a, annotator_b)
    disagreements = set(disagreement_ids(annotator_a, annotator_b))
    decision_by_id = {
        row.get("annotation_id", "").strip(): row
        for row in decisions
        if row.get("annotation_id", "").strip()
    }
    if set(decision_by_id) != disagreements:
        missing = sorted(disagreements - set(decision_by_id))
        extra = sorted(set(decision_by_id) - disagreements)
        raise ValueError(
            f"Adjudication decisions must exactly match disagreements; "
            f"missing={missing}, extra={extra}"
        )

    final_rows: list[dict[str, str]] = []
    for annotation_id in sorted(a):
        row_a = a[annotation_id]
        row_b = b[annotation_id]
        final = {field: row_a.get(field, "") for field in QUEUE_FIELDS}

        if annotation_id in disagreements:
            decision = decision_by_id[annotation_id]
            outcomes = _final_outcomes_from_decision(
                decision, row_a["task_type"], annotation_id
            )
            adjudicator_id = decision.get("adjudicator_id", "").strip()
            rationale = decision.get("adjudication_rationale", "").strip()
            if not adjudicator_id or not rationale:
                raise ValueError(
                    f"Adjudication {annotation_id} requires adjudicator_id and rationale"
                )
            final.update(outcomes)
            final["annotator_id"] = adjudicator_id
            final["rationale"] = rationale
        else:
            for field in _relevant_outcomes(row_a):
                final[field] = row_a.get(field, "").strip()
            if row_a["task_type"] == "attack":
                for field in (
                    "utility_preserved",
                    "task_completion",
                    "correctness",
                    "relevance",
                    "over_refusal",
                ):
                    final[field] = ""
            final["annotator_id"] = "independent_agreement"
            final["rationale"] = (
                "Independent annotators agreed. "
                f"A: {row_a.get('rationale', '').strip()} "
                f"B: {row_b.get('rationale', '').strip()}"
            ).strip()

        final["adjudication_status"] = "adjudicated"
        final_rows.append(final)

    return final_rows


def _write_csv(path: str | Path, rows: list[dict[str, str]], fields: tuple[str, ...]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--annotator-a", required=True)
    prepare.add_argument("--annotator-b", required=True)
    prepare.add_argument("--queue", required=True)
    prepare.add_argument("--agreement-output", required=True)

    finalize = subparsers.add_parser("finalize")
    finalize.add_argument("--annotator-a", required=True)
    finalize.add_argument("--annotator-b", required=True)
    finalize.add_argument("--decisions", required=True)
    finalize.add_argument("--output", required=True)

    args = parser.parse_args()
    a = read_annotations(args.annotator_a, require_adjudicated=False)
    b = read_annotations(args.annotator_b, require_adjudicated=False)

    if args.command == "prepare":
        queue, agreement = build_adjudication_queue(a, b)
        _write_csv(args.queue, queue, ADJUDICATION_FIELDS)
        with Path(args.agreement_output).open("w", encoding="utf-8") as handle:
            json.dump(agreement, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(f"Wrote {len(queue)} disagreement rows to {args.queue}")
        print(f"Wrote pre-adjudication agreement to {args.agreement_output}")
        return

    decisions = _read_decisions(args.decisions)
    final_rows = finalize_annotations(a, b, decisions)
    _write_csv(args.output, final_rows, QUEUE_FIELDS)
    # Validate the complete output using the same gate used by benchmark analysis.
    read_annotations(args.output, require_adjudicated=True)
    print(f"Wrote {len(final_rows)} adjudicated rows to {args.output}")


if __name__ == "__main__":
    main()
