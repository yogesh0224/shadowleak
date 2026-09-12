import unittest

from model_interface.hf_model import HuggingFaceModelInterface
from research.benchmark_manifest import build_manifest
from research.run_benchmark import run_benchmark


class FakeGenerator:
    def __init__(self):
        self.full_input = None
        self.options = None

    def __call__(self, full_input, **options):
        self.full_input = full_input
        self.options = options
        return [{"generated_text": "  safe completion  "}]


class HuggingFaceAdapterTests(unittest.TestCase):
    def test_adapter_does_not_return_prompt_or_context_prefix(self):
        adapter = HuggingFaceModelInterface.__new__(HuggingFaceModelInterface)
        adapter.generator = FakeGenerator()
        result = adapter.generate("user request", "private context")

        self.assertEqual(result, "safe completion")
        self.assertIn("private context", adapter.generator.full_input)
        self.assertIn("user request", adapter.generator.full_input)
        self.assertFalse(adapter.generator.options["return_full_text"])

    def test_hf_runs_require_immutable_revision(self):
        with self.assertRaisesRegex(ValueError, "40-character commit SHA"):
            run_benchmark(
                build_manifest(record_count=1),
                model_name="hf",
                model_id="organization/model",
                model_revision="main",
            )


if __name__ == "__main__":
    unittest.main()
