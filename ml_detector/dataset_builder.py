import pandas as pd
from core.models import ModelResponse, LeakageResult
from ml_detector.features import extract_features


LEAK_PRIORITY = {
    "exact": 3,
    "partial": 2,
    "semantic": 1,
}


def get_binary_label(response) -> int:
    has_leak = LeakageResult.objects.filter(response=response).exists()
    return 1 if has_leak else 0


def get_multiclass_label(response) -> str:
    leaks = LeakageResult.objects.filter(response=response)

    if not leaks.exists():
        return "no_leak"

    best_type = "semantic"
    best_score = -1

    for leak in leaks:
        score = LEAK_PRIORITY.get(leak.leakage_type, 0)
        if score > best_score:
            best_type = leak.leakage_type
            best_score = score

    return best_type


def build_dataset(binary=True):
    rows = []

    responses = ModelResponse.objects.select_related("prompt", "prompt__record").all()

    for response in responses:
        record = response.prompt.record
        features = extract_features(
            prompt_text=response.prompt.final_prompt,
            prompt_category=response.prompt.category,
            output_text=response.output_text,
            record=record,
        )

        if binary:
            label = get_binary_label(response)
        else:
            label = get_multiclass_label(response)

        row = {
            **features,
            "label": label,
            "response_id": response.id,
        }
        rows.append(row)

    return pd.DataFrame(rows)