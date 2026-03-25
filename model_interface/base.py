class BaseModelInterface:
    def generate(self, prompt: str, context: str = "") -> str:
        raise NotImplementedError