import unittest

from research.canaries import generate_canaries


class CanaryTests(unittest.TestCase):
    def test_records_are_deterministic_and_visibly_synthetic(self):
        first = generate_canaries(count=5, seed=17)
        second = generate_canaries(count=5, seed=17)
        self.assertEqual(first, second)
        self.assertEqual(len({record.email for record in first}), 5)
        self.assertTrue(all(record.email.endswith("@example.invalid") for record in first))
        self.assertTrue(all(record.name.startswith("Canary Subject") for record in first))

    def test_requires_positive_count(self):
        with self.assertRaises(ValueError):
            generate_canaries(count=0)


if __name__ == "__main__":
    unittest.main()
