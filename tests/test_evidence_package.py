import json
import tempfile
import unittest
from pathlib import Path

from research.evidence_package import build_evidence_package


class EvidencePackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_builds_deterministic_manifest(self):
        study = self.write(
            "study.json",
            json.dumps({
                "schema_version": "shadowleak.study-plan.v1",
                "study_id": "test-study",
                "status": "frozen_before_model_execution",
                "benchmark": {
                    "record_count": 1,
                    "seed": 42,
                    "attack_template_version": "v1",
                    "expected_cases_per_model": 32,
                },
                "generation": {"do_sample": False, "max_new_tokens": 8},
                "failure_policy": {"maximum_failure_rate": 0.05},
                "models": [
                    {
                        "key": "m1",
                        "model_id": "org/m1",
                        "revision": "a" * 40,
                        "license": "test",
                        "model_card": "https://huggingface.co/org/m1",
                    },
                    {
                        "key": "m2",
                        "model_id": "org/m2",
                        "revision": "b" * 40,
                        "license": "test",
                        "model_card": "https://huggingface.co/org/m2",
                    },
                ],
                "evidence_boundary": "test boundary",
            }, sort_keys=True),
        )
        reporting = self.write(
            "reporting.json",
            json.dumps({
                "schema_version": "shadowleak.reporting-plan.v1",
                "study_id": "test-study",
                "status": "frozen_before_confirmatory_outcome_inspection",
            }, sort_keys=True),
        )
        artifact = self.write("run_summary.json", '{"completed_cases": 32}\n')

        first = build_evidence_package(
            study,
            reporting,
            {"primary_run_summary": artifact},
        )
        second = build_evidence_package(
            study,
            reporting,
            {"primary_run_summary": artifact},
        )

        self.assertEqual(first, second)
        self.assertEqual(first["study_id"], "test-study")
        self.assertEqual(first["artifact_count"], 3)
        roles = [item["role"] for item in first["artifacts"]]
        self.assertEqual(
            roles,
            ["study_plan", "reporting_plan", "primary_run_summary"],
        )

    def test_rejects_reporting_plan_for_other_study(self):
        study = self.write(
            "study.json",
            json.dumps({
                "schema_version": "shadowleak.study-plan.v1",
                "study_id": "test-study",
                "status": "frozen_before_model_execution",
                "benchmark": {
                    "record_count": 1,
                    "seed": 42,
                    "attack_template_version": "v1",
                    "expected_cases_per_model": 32,
                },
                "generation": {"do_sample": False, "max_new_tokens": 8},
                "failure_policy": {"maximum_failure_rate": 0.05},
                "models": [
                    {
                        "key": "m1",
                        "model_id": "org/m1",
                        "revision": "a" * 40,
                        "license": "test",
                        "model_card": "https://huggingface.co/org/m1",
                    },
                    {
                        "key": "m2",
                        "model_id": "org/m2",
                        "revision": "b" * 40,
                        "license": "test",
                        "model_card": "https://huggingface.co/org/m2",
                    },
                ],
                "evidence_boundary": "test boundary",
            }),
        )
        reporting = self.write(
            "reporting.json",
            json.dumps({
                "schema_version": "shadowleak.reporting-plan.v1",
                "study_id": "different-study",
                "status": "frozen_before_confirmatory_outcome_inspection",
            }),
        )
        with self.assertRaisesRegex(ValueError, "different studies"):
            build_evidence_package(study, reporting)


if __name__ == "__main__":
    unittest.main()
