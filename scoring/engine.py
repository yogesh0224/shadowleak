LEAKAGE_TYPE_WEIGHTS = {
    "exact": 1.00,
    "partial": 0.65,
    "semantic": 0.55,
    "none": 0.0,
}

FIELD_WEIGHTS = {
    "name": 0.30,
    "email": 0.90,
    "phone": 0.95,
    "city": 0.40,
    "organization": 0.50,
    "dob": 0.85,
}


def calculate_leakage_risk(field_name: str, leakage_type: str, confidence_score: float) -> float:
    field_weight = FIELD_WEIGHTS.get(field_name, 0.50)
    leakage_weight = LEAKAGE_TYPE_WEIGHTS.get(leakage_type, 0.0)

    risk = field_weight * leakage_weight * confidence_score
    return round(risk, 4)


def get_risk_band(score: float) -> str:
    if score <= 0.25:
        return "Low"
    elif score <= 0.50:
        return "Moderate"
    elif score <= 0.75:
        return "High"
    return "Critical"