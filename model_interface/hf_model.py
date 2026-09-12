from .base import BaseModelInterface


class HuggingFaceModelInterface(BaseModelInterface):
    """Deterministic chat-model adapter with immutable revision pinning."""

    PROMPT_FORMAT = "shadowleak.single-turn-chat.v1"

    def __init__(self, model_name, revision, max_new_tokens=64, device="auto"):
        import torch
        import transformers
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.transformers_version = transformers.__version__
        self.model_name = model_name
        self.revision = revision
        self.max_new_tokens = max_new_tokens
        self.device = (
            "cuda" if device == "auto" and torch.cuda.is_available() else device
        )
        if self.device == "auto":
            self.device = "cpu"
        dtype = torch.float16 if self.device.startswith("cuda") else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            revision=revision,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            revision=revision,
            torch_dtype=dtype,
        ).to(self.device)
        self.model.eval()

    def generate(self, prompt: str, context: str = "") -> str:
        content = f"Reference context:\n{context}\n\nRequest:\n{prompt}"
        rendered = self.tokenizer.apply_chat_template(
            [{"role": "user", "content": content}],
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self.tokenizer(rendered, return_tensors="pt").to(self.device)
        input_length = inputs["input_ids"].shape[-1]
        pad_token_id = self.tokenizer.pad_token_id or self.tokenizer.eos_token_id
        with self.torch.inference_mode():
            output = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                pad_token_id=pad_token_id,
            )
        generated_tokens = output[0][input_length:]
        return self.tokenizer.decode(
            generated_tokens, skip_special_tokens=True
        ).strip()

    def provenance(self):
        return {
            "adapter": "huggingface-transformers",
            "transformers_version": self.transformers_version,
            "torch_version": self.torch.__version__,
            "device": self.device,
            "prompt_format": self.PROMPT_FORMAT,
            "generation": {
                "do_sample": False,
                "max_new_tokens": self.max_new_tokens,
            },
        }
