import unittest

from research.inference import cluster_bootstrap_paired_difference
from research.power_analysis import required_paired_cases


class ConfirmatoryDesignTests(unittest.TestCase):
    def make_rows(self):
        rows = []
        outcomes = {
            "r1": ([1, 1, 1, 0], [0, 0, 1, 0]),
            "r2": ([1, 0, 1, 0], [0, 0, 0, 0]),
            "r3": ([0, 0, 1, 1], [0, 0, 1, 0]),
            "r4": ([1, 1, 0, 0], [1, 0, 0, 0]),
        }
        for record_id, (none, guard) in outcomes.items():
            for index, value in enumerate(none):
                rows.append({"record_id": record_id, "pair_id": f"{record_id}-{index}", "defense_condition": "none", "gold_label": value})
            for index, value in enumerate(guard):
                rows.append({"record_id": record_id, "pair_id": f"{record_id}-{index}", "defense_condition": "guardshield-v1", "gold_label": value})
        return rows

    def test_cluster_bootstrap_is_deterministic_and_record_clustered(self):
        first = cluster_bootstrap_paired_difference(self.make_rows(), outcome_field="gold_label", iterations=500, seed=17)
        second = cluster_bootstrap_paired_difference(self.make_rows(), outcome_field="gold_label", iterations=500, seed=17)
        self.assertEqual(first, second)
        self.assertEqual(first["clusters"], 4)
        self.assertGreater(first["estimate"], 0)
        self.assertLessEqual(first["ci"][0], first["estimate"])
        self.assertGreaterEqual(first["ci"][1], first["estimate"])

    def test_cluster_bootstrap_rejects_single_cluster(self):
        rows = [row for row in self.make_rows() if row["record_id"] == "r1"]
        with self.assertRaises(ValueError):
            cluster_bootstrap_paired_difference(rows, outcome_field="gold_label", iterations=200)

    def test_incomplete_pair_excluded_from_both_conditions_and_bootstrap(self):
        # r1's unmatched positive no-defense observation must not affect its rate.
        rows = [
            {"record_id": "r1", "pair_id": "r1-a", "defense_condition": "none", "gold_label": 0},
            {"record_id": "r1", "pair_id": "r1-a", "defense_condition": "guardshield-v1", "gold_label": 0},
            {"record_id": "r1", "pair_id": "r1-b", "defense_condition": "none", "gold_label": 1},
            {"record_id": "r2", "pair_id": "r2-a", "defense_condition": "none", "gold_label": 1},
            {"record_id": "r2", "pair_id": "r2-a", "defense_condition": "guardshield-v1", "gold_label": 0},
        ]
        expected = cluster_bootstrap_paired_difference(
            [row for row in rows if row["pair_id"] != "r1-b"],
            outcome_field="gold_label", iterations=200, seed=17,
        )
        actual = cluster_bootstrap_paired_difference(rows, outcome_field="gold_label", iterations=200, seed=17)
        self.assertEqual(actual, expected)
        self.assertEqual(actual["estimate"], 0.5)
        self.assertEqual(actual["condition_rates"]["none"], 0.5)
        self.assertEqual(actual["condition_rates"]["guardshield-v1"], 0.0)

    def test_cluster_bootstrap_rejects_duplicate_pair_arm(self):
        rows = self.make_rows()
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            cluster_bootstrap_paired_difference(rows + [dict(rows[0])], outcome_field="gold_label", iterations=200)

    def test_cluster_bootstrap_rejects_pair_shared_between_clusters(self):
        rows = self.make_rows()
        rows[1]["pair_id"] = "r1-0"
        rows[1]["record_id"] = "r2"
        with self.assertRaisesRegex(ValueError, "multiple record clusters"):
            cluster_bootstrap_paired_difference(rows, outcome_field="gold_label", iterations=200)

    def test_cluster_bootstrap_requires_two_clusters_with_complete_pairs(self):
        rows = [row for row in self.make_rows() if row["record_id"] == "r1"]
        rows.append({"record_id": "r2", "pair_id": "r2-unmatched", "defense_condition": "none", "gold_label": 1})
        with self.assertRaisesRegex(ValueError, "two clusters"):
            cluster_bootstrap_paired_difference(rows, outcome_field="gold_label", iterations=200)

    def test_power_requirement_rises_for_smaller_effect(self):
        larger = required_paired_cases(prevented_probability=0.18, induced_probability=0.03)
        smaller = required_paired_cases(prevented_probability=0.12, induced_probability=0.07)
        self.assertGreater(smaller["required_matched_pairs"], larger["required_matched_pairs"])

    def test_power_rejects_zero_effect(self):
        with self.assertRaises(ValueError):
            required_paired_cases(prevented_probability=0.10, induced_probability=0.10)


if __name__ == "__main__":
    unittest.main()
