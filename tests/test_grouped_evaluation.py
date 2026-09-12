import unittest

import pandas as pd

from ml_detector.evaluation import evaluate_grouped_classifier


class GroupedEvaluationTests(unittest.TestCase):
    def make_frame(self):
        rows = []
        for record_id in range(1, 7):
            for label in (0, 1):
                for replicate in range(2):
                    rows.append({
                        "response_id": record_id * 100 + label * 10 + replicate,
                        "record_id": record_id,
                        "attack_strategy": "direct" if label else "benign",
                        "prompt_template_id": replicate,
                        "signal": label + record_id * 0.001,
                        "length": 20 + replicate,
                        "label": label,
                    })
        return pd.DataFrame(rows)

    def test_record_groups_never_overlap(self):
        report = evaluate_grouped_classifier(self.make_frame(), n_splits=3, seed=11)
        for fold in report["folds"]:
            self.assertTrue(set(fold["train_record_ids"]).isdisjoint(fold["test_record_ids"]))
        self.assertEqual(report["metrics"]["n"], 24)

    def test_requires_both_classes(self):
        frame = self.make_frame()
        frame["label"] = 1
        with self.assertRaises(ValueError):
            evaluate_grouped_classifier(frame)


if __name__ == "__main__":
    unittest.main()

