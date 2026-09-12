import csv
import tempfile
import unittest
from pathlib import Path

from research.adjudication import (
    ADJUDICATION_FIELDS,
    build_adjudication_queue,
    finalize_annotations,
)


class AdjudicationTests(unittest.TestCase):
    def row(
        self,
        annotation_id,
        task_type,
        gold_label,
        leak_type,
        annotator_id,
        rationale,
        utility_preserved="",
        task_completion="",
        correctness="",
        relevance="",
        over_refusal="",
    ):
        return {
            "annotation_id": annotation_id,
            "task_type": task_type,
            "prompt": f"prompt-{annotation_id}",
            "synthetic_context": f"context-{annotation_id}",
            "target_field": "email",
            "protected_value": "person@example.invalid",
            "response": f"response-{annotation_id}",
            "gold_label": gold_label,
            "leak_type": leak_type,
            "utility_preserved": utility_preserved,
            "task_completion": task_completion,
            "correctness": correctness,
            "relevance": relevance,
            "over_refusal": over_refusal,
            "annotator_id": annotator_id,
            "adjudication_status": "",
            "rationale": rationale,
        }

    def test_prepare_contains_only_disagreements(self):
        a = [
            self.row("ann1", "attack", "0", "none", "a", "No disclosure."),
            self.row("ann2", "attack", "1", "semantic", "a", "Meaning disclosed."),
        ]
        b = [
            self.row("ann1", "attack", "0", "none", "b", "No disclosure."),
            self.row("ann2", "attack", "0", "none", "b", "No disclosure."),
        ]
        queue, agreement = build_adjudication_queue(a, b)
        self.assertEqual([row["annotation_id"] for row in queue], ["ann2"])
        self.assertEqual(agreement["n"], 2)
        self.assertEqual(agreement["disagreement_count"], 1)
        self.assertNotIn("case_id", ADJUDICATION_FIELDS)
        self.assertNotIn("defense_condition", ADJUDICATION_FIELDS)

    def test_finalize_uses_agreement_and_adjudicated_disagreement(self):
        a = [
            self.row("ann1", "attack", "0", "none", "a", "No disclosure."),
            self.row(
                "ann2", "benign", "0", "none", "a", "Benign answer.",
                "1", "1", "1", "1", "0",
            ),
        ]
        b = [
            self.row("ann1", "attack", "0", "none", "b", "No disclosure."),
            self.row(
                "ann2", "benign", "0", "none", "b", "Over-refusal.",
                "0", "0", "1", "1", "1",
            ),
        ]
        decisions = [{
            "annotation_id": "ann2",
            "final_gold_label": "0",
            "final_leak_type": "none",
            "final_utility_preserved": "1",
            "final_task_completion": "1",
            "final_correctness": "1",
            "final_relevance": "1",
            "final_over_refusal": "0",
            "adjudicator_id": "adj1",
            "adjudication_rationale": "The benign task was completed without refusal.",
        }]
        final = finalize_annotations(a, b, decisions)
        by_id = {row["annotation_id"]: row for row in final}
        self.assertEqual(by_id["ann1"]["adjudication_status"], "adjudicated")
        self.assertEqual(by_id["ann1"]["annotator_id"], "independent_agreement")
        self.assertEqual(by_id["ann2"]["annotator_id"], "adj1")
        self.assertEqual(by_id["ann2"]["utility_preserved"], "1")

    def test_finalize_rejects_missing_decision(self):
        a = [self.row("ann1", "attack", "1", "semantic", "a", "Disclosure.")]
        b = [self.row("ann1", "attack", "0", "none", "b", "No disclosure.")]
        with self.assertRaisesRegex(ValueError, "exactly match disagreements"):
            finalize_annotations(a, b, [])


if __name__ == "__main__":
    unittest.main()
