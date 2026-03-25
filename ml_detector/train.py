import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier

from ml_detector.dataset_builder import build_dataset


MODEL_DIR = "ml_detector/model_artifacts"
MODEL_PATH = os.path.join(MODEL_DIR, "leak_classifier.joblib")


def train_binary_classifier():
    df = build_dataset(binary=True)

    if df.empty:
        raise ValueError("Dataset is empty. Run experiments first.")

    X = df.drop(columns=["label", "response_id"])
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(classification_report(y_test, preds))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"Model saved to {MODEL_PATH}")