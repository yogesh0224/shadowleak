import copy
import unittest

from research.power_analysis import minimum_records_by_simulation
from research.study_plan import load_study_plan, validate_study_plan


class StudyPlanTests(unittest.TestCase):
    def setUp(self):
        self.plan, self.digest = load_study_plan("studies/pilot_v1.json")

    def test_frozen_pilot_plan_is_valid_and_hashed(self):
        self.assertEqual(len(self.digest), 64)
        self.assertEqual(self.plan["benchmark"]["expected_cases_per_model"], 64)
        self.assertEqual(len(self.plan["models"]), 2)
        self.assertTrue(
            all(len(model["revision"]) == 40 for model in self.plan["models"])
        )

    def test_confirmatory_v1_uses_v2_case_count_and_four_pinned_models(self):
        plan, digest = load_study_plan("studies/confirmatory_v1.json")
        self.assertEqual(len(digest), 64)
        self.assertEqual(plan["benchmark"]["attack_template_version"], "v2")
        self.assertEqual(plan["benchmark"]["record_count"], 30)
        self.assertEqual(plan["benchmark"]["expected_cases_per_model"], 1860)
        self.assertEqual(len(plan["models"]), 4)
        self.assertEqual(
            [model["role"] for model in plan["models"]].count("primary"), 1
        )

    def test_cluster_power_simulation_is_deterministic(self):
        first = minimum_records_by_simulation(
            candidates=[12, 16, 20],
            target_power=0.80,
            pairs_per_record=27,
            no_defense_leakage=0.15,
            defended_leakage=0.10,
            record_latent_share=0.40,
            pair_latent_share=0.20,
            alpha=0.05,
            iterations=200,
            seed=42,
        )
        second = minimum_records_by_simulation(
            candidates=[12, 16, 20],
            target_power=0.80,
            pairs_per_record=27,
            no_defense_leakage=0.15,
            defended_leakage=0.10,
            record_latent_share=0.40,
            pair_latent_share=0.20,
            alpha=0.05,
            iterations=200,
            seed=42,
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first["results"]), 3)

    def test_moving_model_revision_is_rejected(self):
        changed = copy.deepcopy(self.plan)
        changed["models"][0]["revision"] = "main"
        with self.assertRaisesRegex(ValueError, "commit SHA"):
            validate_study_plan(changed)

    def test_case_count_must_match_benchmark_design(self):
        changed = copy.deepcopy(self.plan)
        changed["benchmark"]["expected_cases_per_model"] = 63
        with self.assertRaisesRegex(ValueError, "must equal 64"):
            validate_study_plan(changed)


if __name__ == "__main__":
    unittest.main()
