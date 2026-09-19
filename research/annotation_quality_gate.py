"""Validate independently completed blinded annotations before adjudication.

Does not inspect model identities, defense conditions, detector outputs or private
crosswalks. Does not generate human labels. CLI emits metadata only, not text.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from research.annotation_queue import QUEUE_FIELDS

STIMULUS_FIELDS = (
    "annotation_id", "task_type", "prompt", "synthetic_context",
    "target_field", "protected_value", "response",
)
LABEL_FIELDS = tuple(field for field in QUEUE_FIELDS if field not in STIMULUS_FIELDS)
UTILITY_FIELDS = (
    "utility_preserved", "task_completion", "correctness", "relevance", "over_refusal"
)
LEAK_TYPES = {"none", "exact", "partial", "semantic", "inferred"}


def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != QUEUE_FIELDS:
            raise ValueError("Unexpected CSV columns: queue must use the frozen schema")
        rows = list(reader)
    if not rows:
        raise ValueError("CSV must contain at least one annotation row")
    seen: set[str] = set()
    for line_number, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"Malformed CSV fields at line {line_number}")
        ann = row["annotation_id"]
        if not ann or ann in seen:
            raise ValueError(f"Missing or duplicate annotation ID at line {line_number}")
        seen.add(ann)
    return rows


def validate_source(queue: list[dict[str, str]], *, expected_rows: int) -> None:
    if len(queue) != expected_rows:
        raise ValueError(f"Unexpected source row count: expected {expected_rows}")
    for index, row in enumerate(queue, start=2):
        if row["task_type"] not in {"attack", "benign"}:
            raise ValueError(f"Unexpected task type at line {index}")
        if any(row[field].strip() for field in LABEL_FIELDS):
            raise ValueError(f"Source queue already contains annotations at line {index}")


def _validate_one(
    queue: list[dict[str, str]],
    completed: list[dict[str, str]],
    *,
    expected_annotator: str,
) -> dict[str, int]:
    original = {row["annotation_id"]: row for row in queue}
    reviewed = {row["annotation_id"]: row for row in completed}
    if set(original) != set(reviewed):
        raise ValueError("Annotated CSV has missing or extra annotation IDs")
    totals = {"attack": 0, "benign": 0}
    for annotation_id, source in original.items():
        row = reviewed[annotation_id]
        if any(row[field] != source[field] for field in STIMULUS_FIELDS):
            raise ValueError("An original stimulus value was edited or replaced")
        if row["annotator_id"] != expected_annotator:
            raise ValueError("Incorrect, blank, or inconsistent annotator identifier")
        if row["gold_label"] not in {"0", "1"} or row["leak_type"] not in LEAK_TYPES:
            raise ValueError("Missing or invalid human disclosure label/type")
        if (row["gold_label"] == "0") != (row["leak_type"] == "none"):
            raise ValueError("Binary disclosure label conflicts with disclosure type")
        if row["adjudication_status"].strip():
            raise ValueError("Pre-adjudication status must remain blank")
        if not row["rationale"].strip():
            raise ValueError("Every human label requires a rationale")
        if source["task_type"] == "benign":
            if any(row[field] not in {"0", "1"} for field in UTILITY_FIELDS):
                raise ValueError("All benign utility fields must be 0 or 1")
        elif any(row[field].strip() for field in UTILITY_FIELDS):
            raise ValueError("Attack rows must leave utility fields blank")
        totals[source["task_type"]] += 1
    return totals


def validate_human_passes(
    source_path: str | Path,
    annotator_a_path: str | Path,
    annotator_b_path: str | Path,
    *,
    expected_queue_sha256: str,
    expected_rows: int = 7440,
    annotator_a_id: str = "annotator_a",
    annotator_b_id: str = "annotator_b",
) -> dict:
    """Strict metadata-only gate; no inference that labels were truly independent."""
    if expected_rows < 1:
        raise ValueError("Expected row count must be positive")
    if not annotator_a_id or not annotator_b_id or annotator_a_id == annotator_b_id:
        raise ValueError("Annotators must have distinct nonempty identifiers")
    expected = expected_queue_sha256.lower()
    if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
        raise ValueError("Expected queue SHA-256 must be 64 hexadecimal characters")
    actual = sha256(source_path)
    if actual != expected:
        raise ValueError("Blinded source queue SHA-256 mismatch")
    queue = _rows(source_path)
    validate_source(queue, expected_rows=expected_rows)
    a = _rows(annotator_a_path)
    b = _rows(annotator_b_path)
    count_a = _validate_one(queue, a, expected_annotator=annotator_a_id)
    count_b = _validate_one(queue, b, expected_annotator=annotator_b_id)
    if count_a != count_b:
        raise ValueError("Human annotation passes cover different task populations")
    return {
        "status": "COMPLETE_FILES_VALIDATED_NOT_ADJUDICATED",
        "source_sha256": actual,
        "rows_per_annotator": expected_rows,
        "attack_rows": count_a["attack"],
        "benign_rows": count_a["benign"],
        "human_decisions": 2 * expected_rows,
        "annotator_a_file_sha256": sha256(annotator_a_path),
        "annotator_b_file_sha256": sha256(annotator_b_path),
        "human_independence": "requires procedural confirmation by custodian",
        "adjudication": "not performed by this tool",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--queue-sha256", required=True)
    parser.add_argument("--annotator-a", type=Path, required=True)
    parser.add_argument("--annotator-b", type=Path, required=True)
    parser.add_argument("--annotator-a-id", default="annotator_a")
    parser.add_argument("--annotator-b-id", default="annotator_b")
    parser.add_argument("--expected-rows", type=int, default=7440)
    args = parser.parse_args()
    result = validate_human_passes(
        args.queue,
        args.annotator_a,
        args.annotator_b,
        expected_queue_sha256=args.queue_sha256,
        expected_rows=args.expected_rows,
        annotator_a_id=args.annotator_a_id,
        annotator_b_id=args.annotator_b_id,
    )
    # Print metadata only. Never print model responses or individual human labels.
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
