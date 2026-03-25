import re

RISKY_PATTERNS = [
    r"email",
    r"phone",
    r"contact",
    r"address",
    r"where does .* live",
    r"give me .* details",
]


def is_prompt_risky(prompt: str) -> bool:
    prompt_lower = prompt.lower()

    for pattern in RISKY_PATTERNS:
        if re.search(pattern, prompt_lower):
            return True

    return False


def sanitize_prompt(prompt: str) -> str:
    return "[BLOCKED] This request may expose sensitive information."