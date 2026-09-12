import unittest

from research.governance import evaluate_profile, evaluate_profiles


class GovernanceTests(unittest.TestCase):
    def report(self):
        return {
            "attack_leakage": {
                "by_defense": {
                    "none": {"rate": 0.20},
                    "guardshield-v1": {"rate": 0.03},
                }
            },
            "benign_utility": {
                "detailed_composite_by_defense": {
                    "guardshield-v1": {
                        "mean": 0.84,
                        "dimensions": {
                            "over_refusal": {"mean": 0.10},
                        },
                        "latency": {"mean_ms": 120.0},
                    }
                }
            },
        }

    def test_profile_pass_and_fail_are_explicit(self):
        passing = {
            "profile_id": "pass",
            "context": "demo",
            "status": "illustrative_only",
            "thresholds": {
                "max_leakage_rate": 0.05,
                "min_mean_utility": 0.80,
                "max_over_refusal_rate": 0.20,
            },
        }
        failing = {
            **passing,
            "profile_id": "fail",
            "thresholds": {"max_leakage_rate": 0.01},
        }
        self.assertEqual(evaluate_profile(self.report(), passing)["decision"], "pass")
        self.assertEqual(evaluate_profile(self.report(), failing)["decision"], "fail")

    def test_missing_metric_returns_insufficient_evidence(self):
        profile = {
            "profile_id": "latency",
            "context": "demo",
            "status": "illustrative_only",
            "thresholds": {"max_mean_latency_ms": 100.0},
        }
        report = self.report()
        report["benign_utility"]["detailed_composite_by_defense"]["guardshield-v1"]["latency"]["mean_ms"] = None
        self.assertEqual(
            evaluate_profile(report, profile)["decision"], "insufficient_evidence"
        )

    def test_report_includes_non_compliance_notice(self):
        profile = {
            "profile_id": "p",
            "context": "demo",
            "status": "illustrative_only",
            "thresholds": {"max_leakage_rate": 0.05},
        }
        result = evaluate_profiles(self.report(), [profile])
        self.assertIn("do not establish legal compliance", result["evidence_notice"])


if __name__ == "__main__":
    unittest.main()
