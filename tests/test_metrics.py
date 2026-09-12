import unittest

from research.metrics import binary_metrics, wilson_interval


class MetricsTests(unittest.TestCase):
    def test_confusion_matrix_and_rates(self):
        result = binary_metrics([1, 1, 0, 0], [1, 0, 1, 0])
        self.assertEqual(result["true_positive"], 1)
        self.assertEqual(result["false_negative"], 1)
        self.assertEqual(result["false_positive"], 1)
        self.assertEqual(result["true_negative"], 1)
        self.assertEqual(result["precision"], 0.5)
        self.assertEqual(result["recall"], 0.5)
        self.assertEqual(result["false_positive_rate"], 0.5)

    def test_wilson_interval_contains_observed_rate(self):
        low, high = wilson_interval(6, 10)
        self.assertLess(low, 0.6)
        self.assertGreater(high, 0.6)

    def test_rejects_mismatched_inputs(self):
        with self.assertRaises(ValueError):
            binary_metrics([1, 0], [1])


if __name__ == "__main__":
    unittest.main()

