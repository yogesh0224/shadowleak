import copy
import unittest

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
