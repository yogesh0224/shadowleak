from rapidfuzz import fuzz


def fuzzy_match(secret_value: str, output_text: str, threshold: int = 80):
    if not secret_value or not output_text:
        return 0, False

    score = fuzz.partial_ratio(str(secret_value).lower(), str(output_text).lower())
    return score, score >= threshold