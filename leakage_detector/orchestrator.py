from leakage_detector.exact import exact_match
from leakage_detector.fuzzy import fuzzy_match
from leakage_detector.semantic import semantic_similarity


def analyze_output(record, output_text):
    results = []

    fields = {
        "name": record.name,
        "email": record.email,
        "phone": record.phone,
        "city": record.city,
        "organization": record.organization,
        "dob": str(record.dob) if record.dob else "",
    }

    for field_name, value in fields.items():
        if not value:
            continue

        # 1. Exact leakage
        if exact_match(value, output_text):
            results.append({
                "field_name": field_name,
                "leakage_type": "exact",
                "matched_text": str(value),
                "similarity_score": 1.0,
                "confidence_score": 1.0,
            })
            continue

        # 2. Partial leakage
        fuzzy_score, fuzzy_found = fuzzy_match(value, output_text, threshold=80)
        if fuzzy_found:
            score_normalized = round(fuzzy_score / 100.0, 4)
            results.append({
                "field_name": field_name,
                "leakage_type": "partial",
                "matched_text": str(value),
                "similarity_score": score_normalized,
                "confidence_score": score_normalized,
            })
            continue

        # 3. Semantic leakage
        secret_fact = f"{record.name}'s {field_name} is {value}"
        semantic_score, semantic_found = semantic_similarity(
            secret_fact,
            output_text,
            threshold=0.65
        )
        if semantic_found:
            results.append({
                "field_name": field_name,
                "leakage_type": "semantic",
                "matched_text": str(value),
                "similarity_score": round(semantic_score, 4),
                "confidence_score": round(semantic_score, 4),
            })

    return results