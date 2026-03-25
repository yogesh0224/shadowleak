import random
from .base import BaseModelInterface


class MockModelInterface(BaseModelInterface):

    def generate(self, prompt: str, context: str = "") -> str:
        prompt_lower = prompt.lower()

        # Stronger leakage probability for testing
        leak_chance = random.random()

        # Email leakage
        if "email" in prompt_lower and leak_chance > 0.2:
            for line in context.split("\n"):
                if "email:" in line.lower():
                    return f"The email is {line.split(':', 1)[1].strip()}"

        # Phone leakage
        if "phone" in prompt_lower and leak_chance > 0.3:
            for line in context.split("\n"):
                if "phone:" in line.lower():
                    return f"The phone number is {line.split(':', 1)[1].strip()}"

        # City leakage
        if "who lives in" in prompt_lower and leak_chance > 0.3:
            return context

        # Partial leakage
        if leak_chance > 0.5:
            for line in context.split("\n"):
                if "email:" in line.lower():
                    email = line.split(":")[1].strip()
                    return f"The email looks like {email[:4]}***@gmail.com"

        return "I cannot provide that information."