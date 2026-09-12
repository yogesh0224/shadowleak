from .base import BaseModelInterface


class HuggingFaceModelInterface(BaseModelInterface):
    """Deterministic local text-generation adapter with revision pinning."""

    def __init__(self, model_name, revision, max_new_tokens=64):
        from transformers import pipeline

        self.generator = pipeline(
            "text-generation",
            model=model_name,
            revision=revision,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )

    def generate(self, prompt: str, context: str = "") -> str:
        full_input = f"Context:\n{context}\n\nRequest:\n{prompt}\n\nResponse:\n"

        result = self.generator(full_input, return_full_text=False)

        if result and len(result) > 0:
            return result[0]["generated_text"].strip()

        return ""
