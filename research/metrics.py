"""Transparent binary-classification metrics for leakage evaluation."""

from __future__ import annotations

import math
from collections.abc import Iterable


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("total must be positive")
    if not 0 <= successes <= total:
        raise ValueError("successes must be between zero and total")
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    margin = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / total + z * z / (4 * total * total)
        )
        / denominator
    )
    return max(0.0, centre - margin), min(1.0, centre + margin)


def binary_metrics(y_true: Iterable[int], y_pred: Iterable[int]) -> dict[str, object]:
    truth = [int(value) for value in y_true]
    predictions = [int(value) for value in y_pred]
    if len(truth) != len(predictions) or not truth:
        raise ValueError("y_true and y_pred must have the same non-zero length")
    if set(truth) - {0, 1} or set(predictions) - {0, 1}:
        raise ValueError("Binary metrics require labels in {0, 1}")

    tp = sum(a == 1 and b == 1 for a, b in zip(truth, predictions))
    tn = sum(a == 0 and b == 0 for a, b in zip(truth, predictions))
    fp = sum(a == 0 and b == 1 for a, b in zip(truth, predictions))
    fn = sum(a == 1 and b == 0 for a, b in zip(truth, predictions))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    recall_ci = wilson_interval(tp, tp + fn) if tp + fn else (0.0, 0.0)
    fpr_ci = wilson_interval(fp, fp + tn) if fp + tn else (0.0, 0.0)
    return {
        "n": len(truth), "true_positive": tp, "true_negative": tn,
        "false_positive": fp, "false_negative": fn,
        "accuracy": (tp + tn) / len(truth), "precision": precision,
        "recall": recall, "recall_95pct_wilson_ci": list(recall_ci),
        "specificity": specificity, "false_positive_rate": fpr,
        "false_positive_rate_95pct_wilson_ci": list(fpr_ci), "f1": f1,
    }

