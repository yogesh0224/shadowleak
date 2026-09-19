"""Prospective solo-pilot plan tests. No real model response text is read."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from research.solo_plan import load_solo_plan, validate_solo_plan, write_new_manifest

PLAN_PATH = Path(__file__).resolve().parents[1] / "studies" / "solo_exploratory_v1.json"


class SoloExploratoryPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))

    def test_new_plan_has_correct_counts_pairs_and_distinct_records(self):
        plan, expected_hash, cases = load_solo_plan(PLAN_PATH)
        self.assertEqual(plan["study_id"], "shadowleak-solo-exploratory-v1")
        self.assertEqual(expected_hash, hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest())
        self.assertEqual(len(cases), 620)
        self.assertEqual(sum(c["task_type"] == "attack" for c in cases), 540)
        self.assertEqual(sum(c["task_type"] == "benign" for c in cases), 80)
        self.assertEqual(len({c["pair_id"] for c in cases}), 310)
        self.assertEqual(len({c["record_id"] for c in cases}), 10)
        self.assertEqual({c["defense_condition"] for c in cases},
                         {"none", "guardshield-v1"})

    def test_original_confirmatory_outputs_are_disallowed(self):
        wrong = deepcopy(self.plan)
        wrong["original_study_outputs_allowed"] = True
        with self.assertRaisesRegex(ValueError, "distinct from the original"):
            validate_solo_plan(wrong)

    def test_single_human_cannot_be_pretended_independently_adjudicated(self):
        wrong = deepcopy(self.plan)
        wrong["annotation"]["adjudicated_human_gold"] = True
        with self.assertRaisesRegex(ValueError, "independently adjudicated"):
            validate_solo_plan(wrong)

    def test_switching_to_confirmatory_significance_rejected(self):
        wrong = deepcopy(self.plan)
        wrong["analysis"]["registered_primary_significance_test"] = True
        with self.assertRaisesRegex(ValueError, "confirmatory primary"):
            validate_solo_plan(wrong)

    def test_changed_sample_seed_model_or_defense_rejected(self):
        changes = [
            ("benchmark", "seed", 42),
            ("benchmark", "record_count", 30),
            ("benchmark", "planned_cases", 7440),
            ("model", "revision", "0" * 40),
            ("generation", "max_new_tokens", 128),
            ("benchmark", "defense_conditions", ["none"]),
        ]
        for section, key, changed in changes:
            with self.subTest(section=section, key=key):
                wrong = deepcopy(self.plan)
                wrong[section][key] = changed
                with self.assertRaises(ValueError):
                    validate_solo_plan(wrong)

    def test_manifest_written_once_and_hashed_with_private_permissions(self):
        cases = validate_solo_plan(self.plan)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "private" / "solo_manifest.jsonl"
            reported_hash = write_new_manifest(target, cases)
            self.assertEqual(reported_hash, hashlib.sha256(target.read_bytes()).hexdigest())
            self.assertEqual(len(target.read_text().splitlines()), 620)
            self.assertEqual(json.loads(target.read_text().splitlines()[0])["benchmark_version"],
                             "2.0.0")
            with self.assertRaises(FileExistsError):
                write_new_manifest(target, cases)


if __name__ == "__main__":
    unittest.main()
