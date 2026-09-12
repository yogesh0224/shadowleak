"""Validated, independently supplied gold annotations for privacy leakage."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


VALID_LEAK_TYPES = {"none", "exact", "partial", "semantic", "inferred"}
VALID_STATUSES = {"adjudicated", "single_annotator"}


@dataclass(frozen=True)
class GoldAnnotation:
    response_id: int
    gold_label: int
    leak_type: str
    annotator_id: str
    adjudication_status: str
    rationale: str


def load_gold_annotations(path: str | Path) -> dict[int, GoldAnnotation]:
    """Load annotations without consulting ShadowLeak detector outputs."""
    annotations: dict[int, GoldAnnotation] = {}
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {
            "response_id", "gold_label", "leak_type", "annotator_id",
            "adjudication_status", "rationale",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Gold annotation file is missing columns: {sorted(missing)}")

        for line_number, row in enumerate(reader, start=2):
            try:
                response_id = int(row["response_id"])
                gold_label = int(row["gold_label"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid numeric value on line {line_number}") from exc

            if response_id in annotations:
                raise ValueError(f"Duplicate response_id in gold annotations: {response_id}")
            if gold_label not in {0, 1}:
                raise ValueError(f"gold_label must be 0 or 1 on line {line_number}")

            leak_type = row["leak_type"].strip().lower()
            if leak_type not in VALID_LEAK_TYPES:
                raise ValueError(f"Invalid leak_type on line {line_number}: {leak_type}")
            if gold_label == 0 and leak_type != "none":
                raise ValueError(f"Non-leak label must use leak_type=none on line {line_number}")
            if gold_label == 1 and leak_type == "none":
                raise ValueError(f"Leak label must specify a leak type on line {line_number}")

            status = row["adjudication_status"].strip().lower()
            if status not in VALID_STATUSES:
                raise ValueError(f"Invalid adjudication_status on line {line_number}: {status}")
            annotator_id = row["annotator_id"].strip()
            rationale = row["rationale"].strip()
            if not annotator_id or not rationale:
                raise ValueError(f"Annotator and rationale are required on line {line_number}")

            annotations[response_id] = GoldAnnotation(
                response_id=response_id,
                gold_label=gold_label,
                leak_type=leak_type,
                annotator_id=annotator_id,
                adjudication_status=status,
                rationale=rationale,
            )

    if not annotations:
        raise ValueError("Gold annotation file contains no annotations")
    return annotations

