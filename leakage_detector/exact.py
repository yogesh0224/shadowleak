def normalize_text(text: str) -> str:
    if not text:
        return ""
    return str(text).strip().lower()


def exact_match(secret_value: str, output_text: str) -> bool:
    secret = normalize_text(secret_value)
    output = normalize_text(output_text)

    if not secret or not output:
        return False

    return secret in output