import unittest

from research.economics import compare_conditions, sensitivity_grid


class EconomicsTests(unittest.TestCase):
    def report(self):
        return {
            "attack_leakage": {
                "by_defense": {
                    "none": {"rate": 0.20},
                    "guardshield-v1": {"rate": 0.05},
                }
            },
            "benign_utility": {
                "detailed_composite_by_defense": {
                    "none": {"mean": 0.95, "latency": {"mean_ms": 100.0}},
                    "guardshield-v1": {"mean": 0.75, "latency": {"mean_ms": 130.0}},
                }
            },
        }

    def test_low_privacy_cost_can_prefer_no_defense(self):
        result = compare_conditions(
            self.report(), leakage_cost=1.0, utility_loss_cost=5.0
        )
        self.assertEqual(result["preferred_conditions"], ["none"])

    def test_high_privacy_cost_can_prefer_defense(self):
        result = compare_conditions(
            self.report(), leakage_cost=10.0, utility_loss_cost=1.0
        )
        self.assertEqual(result["preferred_conditions"], ["guardshield-v1"])

    def test_sensitivity_grid_counts_preferences(self):
        result = sensitivity_grid(
            self.report(),
            leakage_costs=[1.0, 10.0],
            utility_loss_costs=[1.0],
            latency_costs_per_ms=[0.0],
        )
        self.assertEqual(result["scenario_count"], 2)
        self.assertEqual(
            sum(result["preference_counts"].values()), 2 + result["tie_count"]
        )
        self.assertIn("not market prices", result["interpretation_notice"])


if __name__ == "__main__":
    unittest.main()
