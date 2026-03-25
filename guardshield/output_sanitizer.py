import re


def mask_email(text):
    return re.sub(r"\S+@\S+", "[EMAIL_MASKED]", text)


def mask_phone(text):
    return re.sub(r"\b\d{7,15}\b", "[PHONE_MASKED]", text)


def sanitize_output(output: str) -> str:
    output = mask_email(output)
    output = mask_phone(output)
    return output