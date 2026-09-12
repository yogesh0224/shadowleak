import unittest
from collections import defaultdict

from research.benchmark_manifest import build_manifest


class BenchmarkManifestTests(unittest.TestCase):
    def test_manifest_is_deterministic_complete_and_paired(self):
        first = build_manifest(record_count=2, seed=17)
        second = build_manifest(record_count=2, seed=17)

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        self.assertEqual(len({row["case_id"] for row in first}), 64)
        self.assertEqual(len({row["record_id"] for row in first}), 2)

        conditions = defaultdict(set)
        for row in first:
            conditions[row["pair_id"]].add(row["defense_condition"])
            self.assertTrue(row["synthetic_data"])
            self.assertIn("@example.invalid", row["context"])
        self.assertTrue(conditions)
        self.assertTrue(
            all(value == {"none", "guardshield-v1"} for value in conditions.values())
        )

    def test_attack_and_benign_mix_is_explicit(self):
        cases = build_manifest(record_count=1, seed=42)
        attack = [row for row in cases if row["task_type"] == "attack"]
        benign = [row for row in cases if row["task_type"] == "benign"]
        self.assertEqual(len(attack), 24)
        self.assertEqual(len(benign), 8)
        self.assertEqual(len({row["attack_family"] for row in attack}), 9)

    def test_v2_expands_prompt_variants_and_marks_holdouts(self):
        cases = build_manifest(record_count=1, seed=42, attack_template_version="v2")
        attack = [row for row in cases if row["task_type"] == "attack"]
        benign = [row for row in cases if row["task_type"] == "benign"]
        self.assertEqual(len(attack), 54)
        self.assertEqual(len(benign), 8)
        self.assertEqual(len({row["attack_family"] for row in attack}), 9)
        self.assertEqual(
            {row["generalization_split"] for row in attack},
            {"development", "heldout"},
        )
        by_family = defaultdict(set)
        for row in attack:
            by_family[row["attack_family"]].add(row["generalization_split"])
        self.assertTrue(
            all(value == {"development", "heldout"} for value in by_family.values())
        )

    def test_non_positive_record_count_is_rejected(self):
        with self.assertRaises(ValueError):
            build_manifest(record_count=0)


if __name__ == "__main__":
    unittest.main()
