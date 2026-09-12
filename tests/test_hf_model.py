import unittest

from model_interface.hf_model import HuggingFaceModelInterface
from research.benchmark_manifest import build_manifest
from research.run_benchmark import run_benchmark


class FakeTensor:
    shape = (1, 4)

    def __getitem__(self, item):
        return [100, 101]


class FakeInputs(dict):
    def __init__(self):
        super().__init__(input_ids=FakeTensor())

    def to(self, device):
        self.device = device
        return self


class FakeTokenizer:
    pad_token_id = 0
    eos_token_id = 1

    def apply_chat_template(self, messages, tokenize, add_generation_prompt):
        self.messages = messages
        self.template_options = (tokenize, add_generation_prompt)
        return "rendered-chat"

    def __call__(self, rendered, return_tensors):
        self.rendered = rendered
        self.return_tensors = return_tensors
        return FakeInputs()

    def decode(self, tokens, skip_special_tokens):
        self.decoded_tokens = tokens
        self.skip_special_tokens = skip_special_tokens
        return "  safe completion  "


class FakeModel:
    def generate(self, **kwargs):
        self.kwargs = kwargs
        return [FakeTensor()]


class FakeInferenceMode:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class FakeTorch:
    __version__ = "test"

    @staticmethod
    def inference_mode():
        return FakeInferenceMode()


class HuggingFaceAdapterTests(unittest.TestCase):
    def test_adapter_uses_chat_template_and_decodes_only_new_tokens(self):
        adapter = HuggingFaceModelInterface.__new__(HuggingFaceModelInterface)
        adapter.tokenizer = FakeTokenizer()
        adapter.model = FakeModel()
        adapter.torch = FakeTorch()
        adapter.device = "cpu"
        adapter.max_new_tokens = 32

        result = adapter.generate("user request", "synthetic context")

        self.assertEqual(result, "safe completion")
        message = adapter.tokenizer.messages[0]
        self.assertEqual(message["role"], "user")
        self.assertIn("synthetic context", message["content"])
        self.assertIn("user request", message["content"])
        self.assertEqual(adapter.tokenizer.template_options, (False, True))
        self.assertTrue(adapter.tokenizer.skip_special_tokens)
        self.assertFalse(adapter.model.kwargs["do_sample"])

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
