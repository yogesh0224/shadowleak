from transformers import pipeline
from .base import BaseModelInterface


class HuggingFaceModelInterface(BaseModelInterface):

    def __init__(self, model_name="distilgpt2"):
        self.generator = pipeline(
            "text-generation",
            model=model_name,
            max_new_tokens=50,
            do_sample=False,
            temperature=0.7,
        )

    def generate(self, prompt: str, context: str = "") -> str:
        full_input = f"{prompt}\n{context}"

        result = self.generator(full_input)

        if result and len(result) > 0:
            return result[0]["generated_text"]

        return ""