import pandas as pd
from core.models import ModelResponse
from ml_detector.features import extract_features
from research.annotations import load_gold_annotations


def build_dataset(gold_labels_path, strict=True):
    """Build features against independent labels, never detector output labels."""
    gold = load_gold_annotations(gold_labels_path)
    rows = []
    responses = list(ModelResponse.objects.select_related("prompt", "prompt__record").all())
    database_ids = {response.id for response in responses}
    missing_in_database = set(gold) - database_ids
    if missing_in_database:
        raise ValueError(
            "Gold annotations reference missing response IDs: "
            f"{sorted(missing_in_database)[:10]}"
        )
    if strict:
        missing_annotations = database_ids - set(gold)
        if missing_annotations:
            raise ValueError(
                "Responses are missing independent gold annotations: "
                f"{sorted(missing_annotations)[:10]}"
            )

    for response in responses:
        annotation = gold.get(response.id)
        if annotation is None:
            continue
        record = response.prompt.record
        features = extract_features(
            prompt_text=response.prompt.final_prompt,
            prompt_category=response.prompt.category,
            output_text=response.output_text,
            record=record,
        )

        row = {
            **features,
            "label": annotation.gold_label,
            "response_id": response.id,
            "record_id": record.id,
            "attack_strategy": response.prompt.attack_strategy or "template",
            "prompt_template_id": response.prompt.template_id,
        }
        rows.append(row)

    return pd.DataFrame(rows)
