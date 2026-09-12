import os
from datetime import datetime, timezone
import joblib
from sklearn.ensemble import RandomForestClassifier

from ml_detector.dataset_builder import build_dataset
from ml_detector.evaluation import evaluate_grouped_classifier, feature_columns, write_evaluation_report


MODEL_DIR = "ml_detector/model_artifacts"
MODEL_PATH = os.path.join(MODEL_DIR, "leak_classifier.joblib")


def train_binary_classifier(gold_labels_path, report_path="reports/grouped_cv_metrics.json", seed=42):
    df = build_dataset(gold_labels_path=gold_labels_path, strict=True)

    if df.empty:
        raise ValueError("Dataset is empty. Run experiments first.")

    evaluation = evaluate_grouped_classifier(df, n_splits=5, seed=seed)
    evaluation["created_at"] = datetime.now(timezone.utc).isoformat()
    evaluation["gold_labels_path"] = os.fspath(gold_labels_path)
    write_evaluation_report(evaluation, report_path)

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=seed,
        class_weight="balanced",
        min_samples_leaf=2,
    )
    columns = feature_columns(df)
    model.fit(df[columns], df["label"].astype(int))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "feature_columns": columns,
            "evaluation_protocol": evaluation["protocol"],
            "seed": seed,
        },
        MODEL_PATH,
    )

    return evaluation
