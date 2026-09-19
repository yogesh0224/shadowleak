"""Strict human annotation preflight tests using synthetic fixture rows only."""
from __future__ import annotations

import csv
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from research.annotation_queue import QUEUE_FIELDS
from research.annotation_quality_gate import sha256, validate_human_passes


def base_row(identifier: str, task_type: str) -> dict[str, str]:
    row = dict.fromkeys(QUEUE_FIELDS, "")
    row.update({
        "annotation_id": identifier,
        "task_type": task_type,
        "prompt": f"synthetic request for {identifier}",
        "synthetic_context": "Synthetic record - no human information",
        "target_field": "email",
        "protected_value": "fake@example.invalid",
        "response": f"synthetic response for {identifier}",
    })
    return row


def labeled_copy(rows: list[dict[str, str]], annotator: str) -> list[dict[str, str]]:
    result = deepcopy(rows)
    for row in result:
        row.update({
            "gold_label": "0", "leak_type": "none",
            "annotator_id": annotator,
            "rationale": "Synthetic test fixture: response did not disclose a field.",
        })
        if row["task_type"] == "benign":
            row.update({
                "utility_preserved": "1", "task_completion": "1", "correctness": "1",
                "relevance": "1", "over_refusal": "0",
            })
    return result


class AnnotationQualityGateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        self.queue_path = root / "blinded_annotation_queue.csv"
        self.a_path = root / "human_a.csv"
        self.b_path = root / "human_b.csv"
        self.blank = [base_row("pool_synthetic_01", "attack"),
                      base_row("pool_synthetic_02", "benign")]
        self.a = labeled_copy(self.blank, "annotator_a")
        self.b = labeled_copy(self.blank, "annotator_b")
        self._write(self.queue_path, self.blank)
        self._write(self.a_path, self.a)
        self._write(self.b_path, self.b)
        self.expected = sha256(self.queue_path)

    def _write(self, path: Path, rows: list[dict[str, str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=QUEUE_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def validate(self):
        return validate_human_passes(
            self.queue_path, self.a_path, self.b_path,
            expected_queue_sha256=self.expected, expected_rows=2,
        )

    def test_complete_two_human_files_pass_without_adjudication_claim(self):
        result = self.validate()
        self.assertEqual(result["rows_per_annotator"], 2)
        self.assertEqual(result["human_decisions"], 4)
        self.assertEqual(result["benign_rows"], 1)
        self.assertIn("NOT_ADJUDICATED", result["status"])
        self.assertEqual(result["human_independence"], "requires procedural confirmation by custodian")

    def test_wrong_source_hash_rejected(self):
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            validate_human_passes(
                self.queue_path, self.a_path, self.b_path,
                expected_queue_sha256="0" * 64, expected_rows=2)

    def test_missing_annotation_row_rejected(self):
        self._write(self.a_path, self.a[:1])
        with self.assertRaisesRegex(ValueError, "missing or extra annotation IDs"):
            self.validate()

    def test_edited_response_rejected(self):
        self.a[0]["response"] = "Rewritten or concealed response"
        self._write(self.a_path, self.a)
        with self.assertRaisesRegex(ValueError, "original stimulus"):
            self.validate()

    def test_edited_pooled_id_rejected(self):
        self.a[0]["annotation_id"] = "pool_synthetic_other"
        self._write(self.a_path, self.a)
        with self.assertRaisesRegex(ValueError, "missing or extra annotation IDs"):
            self.validate()

    def test_missing_benign_detail_rejected(self):
        self.b[1]["correctness"] = ""
        self._write(self.b_path, self.b)
        with self.assertRaisesRegex(ValueError, "All benign utility fields"):
            self.validate()

    def test_attack_utility_fields_must_remain_blank(self):
        self.a[0]["utility_preserved"] = "0"
        self._write(self.a_path, self.a)
        with self.assertRaisesRegex(ValueError, "Attack rows"):
            self.validate()

    def test_conflicting_leak_type_rejected(self):
        self.b[0]["gold_label"] = "1"
        self._write(self.b_path, self.b)
        with self.assertRaisesRegex(ValueError, "conflicts"):
            self.validate()

    def test_blank_rationale_rejected(self):
        self.a[1]["rationale"] = "  "
        self._write(self.a_path, self.a)
        with self.assertRaisesRegex(ValueError, "requires a rationale"):
            self.validate()

    def test_annotators_must_have_distinct_ids(self):
        with self.assertRaisesRegex(ValueError, "distinct"):
            validate_human_passes(
                self.queue_path, self.a_path, self.b_path,
                expected_queue_sha256=self.expected, expected_rows=2,
                annotator_a_id="annotator_a", annotator_b_id="annotator_a")

    def test_unexpected_or_inconsistent_annotator_identity_rejected(self):
        self.b[0]["annotator_id"] = "annotator_a"
        self._write(self.b_path, self.b)
        with self.assertRaisesRegex(ValueError, "annotator identifier"):
            self.validate()

    def test_pre_adjudicated_status_rejected(self):
        self.a[0]["adjudication_status"] = "adjudicated"
        self._write(self.a_path, self.a)
        with self.assertRaisesRegex(ValueError, "Pre-adjudication status"):
            self.validate()

    def test_partially_labeled_original_queue_rejected(self):
        self.blank[0]["gold_label"] = "1"
        self._write(self.queue_path, self.blank)
        with self.assertRaisesRegex(ValueError, "already contains annotations"):
            validate_human_passes(
                self.queue_path, self.a_path, self.b_path,
                expected_queue_sha256=sha256(self.queue_path), expected_rows=2)

    def test_duplicate_id_rejected(self):
        self.a[1]["annotation_id"] = self.a[0]["annotation_id"]
        self._write(self.a_path, self.a)
        with self.assertRaisesRegex(ValueError, "duplicate annotation ID"):
            self.validate()


if __name__ == "__main__":
    unittest.main()
