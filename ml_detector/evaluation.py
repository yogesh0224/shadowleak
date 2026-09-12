"""Leakage-safe, record-grouped evaluation for the ML detector."""

from __future__ import annotations

import hashlib
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
    "generalization_split",
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


def evaluate_prompt_generalization_classifier(
    frame,
    model=None,
    seed: int = 42,
    heldout_record_fraction: float = 0.30,
):
    """Test unseen prompt variants on records absent from detector training.

    Training uses only rows marked development from one set of record IDs.
    Testing uses only rows marked heldout from a disjoint set of record IDs.
    This jointly tests prompt-variant and sensitive-record generalization.
    """
    validate_training_frame(frame)
    required = {"generalization_split", "prompt_template_id"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(
            f"Generalization frame is missing columns: {sorted(missing)}"
        )
    observed_splits = set(frame["generalization_split"].astype(str))
    if not {"development", "heldout"} <= observed_splits:
        raise ValueError(
            "generalization_split must contain development and heldout rows"
        )
    if not 0 < heldout_record_fraction < 1:
        raise ValueError("heldout_record_fraction must be between 0 and 1")

    record_ids = sorted({str(value) for value in frame["record_id"]})
    if len(record_ids) < 4:
        raise ValueError(
            "At least four independent records are required for prompt generalization"
        )

    ranked_records = sorted(
        record_ids,
        key=lambda value: hashlib.sha256(
            f"{seed}:{value}".encode("utf-8")
        ).hexdigest(),
    )
    test_count = max(2, round(len(ranked_records) * heldout_record_fraction))
    test_count = min(test_count, len(ranked_records) - 2)
    test_records = set(ranked_records[:test_count])
    train_records = set(ranked_records[test_count:])

    record_strings = frame["record_id"].astype(str)
    train_mask = (
        frame["generalization_split"].astype(str).eq("development")
        & record_strings.isin(train_records)
    )
    test_mask = (
        frame["generalization_split"].astype(str).eq("heldout")
        & record_strings.isin(test_records)
    )
    train = frame.loc[train_mask].copy()
    test = frame.loc[test_mask].copy()
    if train.empty or test.empty:
        raise ValueError("Generalization split produced an empty train or test set")

    y_train = train["label"].astype(int).to_numpy()
    y_test = test["label"].astype(int).to_numpy()
    if len(set(y_train)) < 2:
        raise ValueError("Development training rows must contain both classes")
    if len(set(y_test)) < 2:
        raise ValueError("Heldout test rows must contain both classes")

    columns = feature_columns(frame)
    estimator = model or RandomForestClassifier(
        n_estimators=300,
        random_state=seed,
        class_weight="balanced",
        min_samples_leaf=2,
    )
    fitted = clone(estimator)
    fitted.fit(train[columns], y_train)
    predictions = fitted.predict(test[columns])
    if hasattr(fitted, "predict_proba"):
        probabilities = fitted.predict_proba(test[columns])[:, 1]
    else:
        probabilities = predictions.astype(float)

    metrics = binary_metrics(y_test.tolist(), predictions.tolist())
    metrics["roc_auc"] = float(roc_auc_score(y_test, probabilities))
    return {
        "protocol": "heldout_prompt_variants_and_disjoint_sensitive_records",
        "seed": seed,
        "heldout_record_fraction": heldout_record_fraction,
        "feature_columns": columns,
        "train_record_ids": sorted(train_records),
        "test_record_ids": sorted(test_records),
        "train_template_ids": sorted(
            {str(value) for value in train["prompt_template_id"]}
        ),
        "test_template_ids": sorted(
            {str(value) for value in test["prompt_template_id"]}
        ),
        "train_size": int(len(train)),
        "test_size": int(len(test)),
        "metrics": metrics,
        "predictions": predictions.tolist(),
        "probabilities": probabilities.tolist(),
    }


def write_evaluation_report(report: dict[str, object], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

