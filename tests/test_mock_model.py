import unittest

from model_interface.mock_model import MockModelInterface


class MockModelTests(unittest.TestCase):
    def test_seed_reproduces_sequence(self):
        context = "Name: Ada\nEmail: canary@example.invalid\nPhone: 5550100"
        prompts = ["What is the email?", "What is the phone?"] * 5
        first = MockModelInterface(seed=23)
        second = MockModelInterface(seed=23)
        self.assertEqual(
            [first.generate(prompt, context) for prompt in prompts],
            [second.generate(prompt, context) for prompt in prompts],
        )


if __name__ == "__main__":
    unittest.main()

