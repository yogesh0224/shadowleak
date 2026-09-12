import csv
import tempfile
import unittest
from pathlib import Path

from research.annotations import load_gold_annotations


class AnnotationTests(unittest.TestCase):
    def write_rows(self, rows):
        temp = tempfile.NamedTemporaryFile(mode="w", newline="", suffix=".csv", delete=False)
        writer = csv.DictWriter(temp, fieldnames=[
            "response_id", "gold_label", "leak_type", "annotator_id",
            "adjudication_status", "rationale",
        ])
        writer.writeheader()
        writer.writerows(rows)
        temp.close()
        self.addCleanup(Path(temp.name).unlink, missing_ok=True)
        return temp.name

    def test_loads_independent_gold_labels(self):
        path = self.write_rows([{
            "response_id": 7, "gold_label": 1, "leak_type": "semantic",
            "annotator_id": "a1", "adjudication_status": "adjudicated",
            "rationale": "The protected organization is disclosed.",
        }])
        self.assertEqual(load_gold_annotations(path)[7].gold_label, 1)

    def test_rejects_inconsistent_non_leak_type(self):
        path = self.write_rows([{
            "response_id": 8, "gold_label": 0, "leak_type": "partial",
            "annotator_id": "a1", "adjudication_status": "adjudicated",
            "rationale": "Invalid on purpose.",
        }])
        with self.assertRaises(ValueError):
            load_gold_annotations(path)

    def test_rejects_duplicate_response_ids(self):
        row = {
            "response_id": 9, "gold_label": 0, "leak_type": "none",
            "annotator_id": "a1", "adjudication_status": "single_annotator",
            "rationale": "No protected attribute.",
        }
        path = self.write_rows([row, row])
        with self.assertRaises(ValueError):
            load_gold_annotations(path)


if __name__ == "__main__":
    unittest.main()

