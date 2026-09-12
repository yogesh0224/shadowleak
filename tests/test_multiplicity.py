import unittest

from research.multiplicity import adjust_named_pvalues, holm_bonferroni


class MultiplicityTests(unittest.TestCase):
    def test_holm_adjustment_is_monotone_and_bounded(self):
        adjusted = holm_bonferroni([0.01, 0.04, 0.20])
        self.assertEqual(len(adjusted), 3)
        self.assertTrue(all(0 <= value <= 1 for value in adjusted))
        self.assertAlmostEqual(adjusted[0], 0.03)
        self.assertAlmostEqual(adjusted[1], 0.08)
        self.assertAlmostEqual(adjusted[2], 0.20)

    def test_named_adjustment_preserves_names(self):
        result = adjust_named_pvalues({"a": 0.01, "b": 0.2})
        self.assertEqual(set(result), {"a", "b"})
        self.assertIn("adjusted_pvalue", result["a"])


if __name__ == "__main__":
    unittest.main()
