"""Create a randomized annotation queue and a separate re-identification key."""

from __future__ import annotations

import argparse
import csv
import hashlib
import random
from pathlib import Path
from typing import Any

from research.io import read_jsonl, write_jsonl

QUEUE_FIELDS = (
    "annotation_id",
    "task_type",
    "prompt",
    "synthetic_context",
    "target_field",
    "protected_value",
    "response",
    "gold_label",
    "leak_type",
    "utility_preserved",
    "annotator_id",
    "adjudication_status",
    "rationale",
)


def _annotation_id(case_id: str, seed: int) -> str:
    digest = hashlib.sha256(f"{seed}:{case_id}".encode("utf-8")).hexdigest()
    return f"ann_{digest[:20]}"


def build_annotation_queue(
    responses: list[dict[str, Any]], seed: int = 42
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return blinded queue rows and a key that must be withheld from annotators."""
    queue: list[dict[str, Any]] = []
    key: list[dict[str, Any]] = []
    seen: set[str] = set()
    for response in responses:
        if response.get("failed"):
            continue
        case_id = str(response.get("case_id", ""))
        if not case_id or case_id in seen:
            raise ValueError("Every response must have a unique, non-empty case_id")
        seen.add(case_id)
        annotation_id = _annotation_id(case_id, seed)
        queue.append(
            {
                "annotation_id": annotation_id,
                "task_type": response["task_type"],
                "prompt": response["prompt"],
                "synthetic_context": response["context"],
                "target_field": response["target_field"],
                "protected_value": response["protected_value"],
                "response": response["response"],
                "gold_label": "",
                "leak_type": "",
                "utility_preserved": "",
                "annotator_id": "",
                "adjudication_status": "",
                "rationale": "",
            }
        )
        key.append(
            {
                "key_schema_version": "shadowleak.annotation-key.v1",
                "annotation_id": annotation_id,
                "case_id": case_id,
            }
        )
    random.Random(seed).shuffle(queue)
    if not queue:
        raise ValueError("No successful responses are available for annotation")
    return queue, key


def write_queue(path: str | Path, rows: list[dict[str, Any]]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=QUEUE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True)
    parser.add_argument("--queue", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    queue, key = build_annotation_queue(read_jsonl(args.responses), seed=args.seed)
    write_queue(args.queue, queue)
    write_jsonl(args.key, key)
    print(f"Wrote {len(queue)} blinded rows to {args.queue}")
    print(f"Keep the case key separate from annotators: {args.key}")


if __name__ == "__main__":
    main()
