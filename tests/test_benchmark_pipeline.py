import copy
import unittest

from research.annotation_queue import build_annotation_queue
from research.benchmark_analysis import (
    analyze,
    exact_mcnemar_pvalue,
    inter_annotator_agreement,
)
from research.benchmark_manifest import build_manifest
from research.run_benchmark import run_benchmark


def completed_annotations(queue):
    rows = copy.deepcopy(queue)
    for row in rows:
        leaked = row["protected_value"] != "not_applicable" and row["protected_value"] in row["response"]
        row["gold_label"] = "1" if leaked else "0"
        row["leak_type"] = "exact" if leaked else "none"
        row["utility_preserved"] = (
            "1" if row["task_type"] == "benign" and "[BLOCKED]" not in row["response"] else "0"
        )
        if row["task_type"] == "benign":
            preserved = row["utility_preserved"]
            row["task_completion"] = preserved
            row["correctness"] = preserved
            row["relevance"] = preserved
            row["over_refusal"] = "0" if preserved == "1" else "1"
        else:
            row["task_completion"] = ""
            row["correctness"] = ""
            row["relevance"] = ""
            row["over_refusal"] = ""
        row["annotator_id"] = "smoke-test"
        row["adjudication_status"] = "adjudicated"
        row["rationale"] = "Synthetic plumbing assertion; not a research annotation."
    return rows


class BenchmarkPipelineTests(unittest.TestCase):
    def setUp(self):
        self.cases = build_manifest(record_count=1, seed=42)
        self.responses = run_benchmark(self.cases, seed=42, run_id="test-run")

    def test_mock_outputs_are_order_independent_and_marked_non_empirical(self):
        reversed_responses = run_benchmark(
            list(reversed(self.cases)), seed=42, run_id="test-run"
        )
        first = {row["case_id"]: row for row in self.responses}
        second = {row["case_id"]: row for row in reversed_responses}
        for case_id in first:
            self.assertEqual(first[case_id]["response"], second[case_id]["response"])
            self.assertEqual(first[case_id]["input_blocked"], second[case_id]["input_blocked"])
            self.assertEqual(first[case_id]["evidence_class"], "plumbing_only")

    def test_annotation_queue_hides_condition_and_case_key(self):
        queue, key = build_annotation_queue(self.responses, seed=13)
        self.assertEqual(len(queue), len(self.responses))
        self.assertEqual(
            {row["annotation_id"] for row in queue},
            {row["annotation_id"] for row in key},
        )
        for row in queue:
            self.assertNotIn("case_id", row)
            self.assertNotIn("pair_id", row)
            self.assertNotIn("defense_condition", row)
            self.assertNotIn("input_blocked", row)

    def test_end_to_end_report_includes_paired_leakage_and_utility(self):
        queue, key = build_annotation_queue(self.responses, seed=42)
        report = analyze(self.responses, key, completed_annotations(queue))
        self.assertEqual(report["sample_accounting"]["responses"], 32)
        self.assertEqual(report["sample_accounting"]["attack_cases"], 24)
        self.assertEqual(report["sample_accounting"]["benign_cases"], 8)
        self.assertEqual(
            report["attack_leakage"]["paired_defense_effect"]["complete_pairs"],
            12,
        )
        self.assertEqual(
            report["benign_utility"]["paired_defense_effect"]["complete_pairs"],
            4,
        )
        self.assertEqual(report["benign_utility"]["detailed_composite_overall"]["n"], 8)
        self.assertTrue(report["privacy_utility_tradeoff"]["available"])
        family_effects = report["attack_leakage"]["paired_defense_effect_by_attack_family"]
        self.assertTrue(family_effects)
        for effect in family_effects.values():
            self.assertIn("holm_adjusted_mcnemar_pvalue", effect)

    def test_exact_mcnemar_pvalue(self):
        self.assertEqual(exact_mcnemar_pvalue(0, 0), 1.0)
        self.assertAlmostEqual(exact_mcnemar_pvalue(5, 0), 0.0625)
        self.assertEqual(exact_mcnemar_pvalue(2, 2), 1.0)

    def test_inter_annotator_agreement(self):
        a = [
            {"annotation_id": "a", "gold_label": "1"},
            {"annotation_id": "b", "gold_label": "0"},
        ]
        b = copy.deepcopy(a)
        agreement = inter_annotator_agreement(a, b)
        self.assertEqual(agreement["raw_agreement"], 1.0)
        self.assertEqual(agreement["cohen_kappa"], 1.0)


if __name__ == "__main__":
    unittest.main()
