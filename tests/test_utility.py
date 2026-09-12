import unittest

from research.utility import mean_utility, privacy_utility_tradeoff, utility_score


class UtilityTests(unittest.TestCase):
    def test_utility_score_reverses_over_refusal(self):
        row = {
            "task_completion": "1",
            "correctness": "1",
            "relevance": "1",
            "over_refusal": "0",
        }
        self.assertEqual(utility_score(row), 1.0)
        row["over_refusal"] = "1"
        self.assertEqual(utility_score(row), 0.75)

    def test_mean_utility_skips_incomplete_detailed_rows(self):
        rows = [
            {"task_completion": "1", "correctness": "1", "relevance": "1", "over_refusal": "0"},
            {"task_completion": "", "correctness": "", "relevance": "", "over_refusal": ""},
        ]
        result = mean_utility(rows)
        self.assertEqual(result["n"], 1)
        self.assertEqual(result["mean"], 1.0)

    def test_tradeoff_reports_privacy_gain_and_utility_cost(self):
        attack = [
            {"defense_condition": "none", "gold_label": 1},
            {"defense_condition": "none", "gold_label": 1},
            {"defense_condition": "guardshield-v1", "gold_label": 0},
            {"defense_condition": "guardshield-v1", "gold_label": 1},
        ]
        benign = [
            {"defense_condition": "none", "task_completion": "1", "correctness": "1", "relevance": "1", "over_refusal": "0"},
            {"defense_condition": "guardshield-v1", "task_completion": "1", "correctness": "1", "relevance": "0", "over_refusal": "1"},
        ]
        result = privacy_utility_tradeoff(attack, benign)
        self.assertTrue(result["available"])
        self.assertEqual(result["privacy_gain"], 0.5)
        self.assertEqual(result["mean_utility"]["none"], 1.0)
        self.assertEqual(result["mean_utility"]["guardshield-v1"], 0.5)
        self.assertEqual(result["utility_cost"], 0.5)
        self.assertEqual(result["privacy_gain_per_unit_utility_cost"], 1.0)


if __name__ == "__main__":
    unittest.main()
