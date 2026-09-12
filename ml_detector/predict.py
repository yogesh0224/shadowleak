import os
import joblib
import pandas as pd
from ml_detector.features import extract_features

MODEL_PATH = "ml_detector/model_artifacts/leak_classifier.joblib"


class LeakMLPredictor:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Trained model not found. Train it first.")
        artifact = joblib.load(MODEL_PATH)
        if not isinstance(artifact, dict) or "model" not in artifact:
            raise ValueError("Legacy model artifact detected; retrain with independent gold labels")
        self.model = artifact["model"]
        self.feature_columns = artifact["feature_columns"]

    def predict(self, prompt_text: str, prompt_category: str, output_text: str, record):
        features = extract_features(
            prompt_text=prompt_text,
            prompt_category=prompt_category,
            output_text=output_text,
            record=record,
        )

        X = pd.DataFrame([features])[self.feature_columns]
        pred = self.model.predict(X)[0]

        if hasattr(self.model, "predict_proba"):
            prob = float(self.model.predict_proba(X)[0][1])
        else:
            prob = None

        return {
            "prediction": int(pred),
            "confidence": prob,
            "features": features,
        }
