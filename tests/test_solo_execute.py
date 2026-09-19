"""Offline mocked solo runner tests; never download or generate model responses."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from research.solo_execute import execute
from research.solo_plan import load_solo_plan

PLAN = Path(__file__).resolve().parents[1] / "studies" / "solo_exploratory_v1.json"
COMMIT = "a" * 40


def mock_model_run(cases, **kwargs):
    results = []
    for row in cases:
        result = deepcopy(row)
        result.update(
            response="Synthetic fixture output; no protected attribute here.",
            failed=False, model_revision=kwargs["model_revision"],
            model_name=kwargs["model_id"],
            latency_ms=1.0,
        )
        results.append(result)
    return results


class SoloRunTests(unittest.TestCase):
    def test_mock_run_has_isolated_complete_evidence_and_blank_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "solo"
            with patch("research.solo_execute.run_benchmark", side_effect=mock_model_run) as run:
                summary = execute(PLAN, output, execution_commit=COMMIT)
            self.assertEqual(summary["study_id"], "shadowleak-solo-exploratory-v1")
            self.assertEqual(summary["completed_cases"], 620)
            self.assertEqual(summary["failed_cases"], 0)
            self.assertEqual(summary["successful_complete_pairs"], 310)
            self.assertEqual(summary["manual_human_labels"], 0)
            self.assertFalse(summary["defense_effect_estimated"])
            self.assertEqual(run.call_args.kwargs["model_revision"], "989aa7980e4cf806f80c7fef2b1adb7bc71aa306")
            self.assertEqual(len((output / "responses.jsonl").read_text().splitlines()), 620)
            self.assertEqual(len((output / "annotation_queue.csv").read_text().splitlines()), 621)
            self.assertEqual(len((output / "PRIVATE_annotation_key.jsonl").read_text().splitlines()), 620)
            self.assertEqual((output / "execution_commit.txt").read_text().strip(), COMMIT)
            self.assertEqual(len(summary["artifacts"]), 5)
            with self.assertRaisesRegex(FileExistsError, "overwrite"):
                execute(PLAN, output, execution_commit=COMMIT)

    def test_generation_failures_recorded_without_retries_or_dropping_cases(self):
        def with_failure(cases, **kwargs):
            results = mock_model_run(cases, **kwargs)
            results[0]["failed"] = True
            results[0]["response"] = ""
            return results

        with tempfile.TemporaryDirectory() as directory:
            with patch("research.solo_execute.run_benchmark", side_effect=with_failure):
                summary = execute(PLAN, Path(directory) / "new", execution_commit=COMMIT)
            self.assertEqual(summary["completed_cases"], 619)
            self.assertEqual(summary["failed_cases"], 1)
            self.assertEqual(summary["successful_complete_pairs"], 309)
            self.assertEqual(summary["annotation_queue_status"], "blank_unlabeled")

    def test_commit_must_be_immutable_sha(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "40-character SHA"):
                execute(PLAN, Path(directory) / "bad", execution_commit="main")


if __name__ == "__main__":
    unittest.main()
