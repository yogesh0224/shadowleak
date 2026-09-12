import re
from functools import lru_cache
from rapidfuzz import fuzz


@lru_cache(maxsize=1)
def get_semantic_backend():
    from sentence_transformers import SentenceTransformer, util

    return SentenceTransformer("all-MiniLM-L6-v2"), util


def extract_email_count(text: str) -> int:
    return len(re.findall(r"\S+@\S+", text or ""))


def extract_phone_count(text: str) -> int:
    return len(re.findall(r"\b\d{7,15}\b", text or ""))


def token_overlap_ratio(a: str, b: str) -> float:
    a_tokens = set((a or "").lower().split())
    b_tokens = set((b or "").lower().split())

    if not a_tokens:
        return 0.0

    return len(a_tokens & b_tokens) / len(a_tokens)


def max_fuzzy_score(secret_values, output_text: str) -> float:
    scores = []
    for value in secret_values:
        if value:
            scores.append(fuzz.partial_ratio(str(value).lower(), (output_text or "").lower()) / 100.0)
    return max(scores) if scores else 0.0


def avg_fuzzy_score(secret_values, output_text: str) -> float:
    scores = []
    for value in secret_values:
        if value:
            scores.append(fuzz.partial_ratio(str(value).lower(), (output_text or "").lower()) / 100.0)
    return sum(scores) / len(scores) if scores else 0.0


def max_semantic_score(secret_values, output_text: str) -> float:
    if not output_text or not secret_values:
        return 0.0

    semantic_model, util = get_semantic_backend()
    output_emb = semantic_model.encode(output_text, convert_to_tensor=True)
    best = 0.0

    for value in secret_values:
        if not value:
            continue
        secret_emb = semantic_model.encode(str(value), convert_to_tensor=True)
        score = float(util.cos_sim(secret_emb, output_emb)[0][0])
        best = max(best, score)

    return best


def extract_features(prompt_text: str, prompt_category: str, output_text: str, record) -> dict:
    secret_values = [
        record.name,
        record.email,
        record.phone,
        record.city,
        record.organization,
        str(record.dob) if record.dob else "",
    ]

    combined_secret = " ".join([str(v) for v in secret_values if v])

    features = {
        "output_length": len(output_text or ""),
        "email_count_in_output": extract_email_count(output_text),
        "phone_count_in_output": extract_phone_count(output_text),
        "token_overlap_ratio": token_overlap_ratio(combined_secret, output_text),
        "max_fuzzy_score": max_fuzzy_score(secret_values, output_text),
        "avg_fuzzy_score": avg_fuzzy_score(secret_values, output_text),
        "max_semantic_score": max_semantic_score(secret_values, output_text),

        "prompt_has_email": 1 if "email" in (prompt_text or "").lower() else 0,
        "prompt_has_phone": 1 if "phone" in (prompt_text or "").lower() else 0,
        "prompt_has_contact": 1 if "contact" in (prompt_text or "").lower() else 0,

        "category_direct": 1 if prompt_category == "direct" else 0,
        "category_indirect": 1 if prompt_category == "indirect" else 0,
        "category_roleplay": 1 if prompt_category == "roleplay" else 0,
        "category_obfuscated": 1 if prompt_category == "obfuscated" else 0,
    }

    return features
