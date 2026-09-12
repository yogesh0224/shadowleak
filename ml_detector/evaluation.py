"""Leakage-safe, record-grouped evaluation for the ML detector."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

from research.metrics import binary_metrics


METADATA_COLUMNS = {
    "label", "response_id", "record_id", "attack_strategy", "prompt_template_id",
}


def feature_columns(frame) -> list[str]:
    columns = [column for column in frame.columns if column not in METADATA_COLUMNS]
    if not columns:
        raise ValueError("No detector feature columns were found")
    return columns


def validate_training_frame(frame) -> None:
    required = {"label", "response_id", "record_id"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Training frame is missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Training frame is empty")
    if set(frame["label"].astype(int).unique()) != {0, 1}:
        raise ValueError("Training data must contain both leak and non-leak labels")
    if frame["record_id"].nunique() < 2:
        raise ValueError("At least two independent records are required")


def evaluate_grouped_classifier(frame, model=None, n_splits: int = 5, seed: int = 42):
    """Evaluate without putting responses from one sensitive record in both sets."""
    validate_training_frame(frame)
    columns = feature_columns(frame)
    X = frame[columns]
    y = frame["label"].astype(int).to_numpy()
    groups = frame["record_id"].to_numpy()
    split_count = min(n_splits, len(np.unique(groups)))
    if split_count < 2:
        raise ValueError("At least two group folds are required")

    estimator = model or RandomForestClassifier(
        n_estimators=300, random_state=seed, class_weight="balanced", min_samples_leaf=2,
    )
    splitter = StratifiedGroupKFold(n_splits=split_count, shuffle=True, random_state=seed)
    predictions = np.zeros(len(frame), dtype=int)
    probabilities = np.zeros(len(frame), dtype=float)
    folds: list[dict[str, object]] = []

    for fold_number, (train_index, test_index) in enumerate(splitter.split(X, y, groups), start=1):
        train_groups = set(groups[train_index])
        test_groups = set(groups[test_index])
        if train_groups & test_groups:
            raise AssertionError("Record groups overlap between training and test folds")
        if len(set(y[train_index])) < 2:
            raise ValueError("A training fold has one class; add independently annotated records")

        fitted = clone(estimator)
        fitted.fit(X.iloc[train_index], y[train_index])
        predictions[test_index] = fitted.predict(X.iloc[test_index])
        if hasattr(fitted, "predict_proba"):
            probabilities[test_index] = fitted.predict_proba(X.iloc[test_index])[:, 1]
        else:
            probabilities[test_index] = predictions[test_index]
        folds.append({
            "fold": fold_number,
            "train_record_ids": sorted(str(value) for value in train_groups),
            "test_record_ids": sorted(str(value) for value in test_groups),
            "test_size": int(len(test_index)),
        })

    metrics = binary_metrics(y.tolist(), predictions.tolist())
    metrics["roc_auc"] = float(roc_auc_score(y, probabilities))
    return {
        "protocol": "stratified_group_k_fold_by_sensitive_record",
        "seed": seed, "n_splits": split_count, "feature_columns": columns,
        "metrics": metrics, "folds": folds,
        "predictions": predictions.tolist(), "probabilities": probabilities.tolist(),
    }


def write_evaluation_report(report: dict[str, object], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

