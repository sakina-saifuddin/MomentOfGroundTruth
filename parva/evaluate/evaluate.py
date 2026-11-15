"""Shared-style evaluation function: evaluate(y_true, y_pred) -> report + confusion matrix.

Returns every metric required by PRD section 9 using sklearn's
classification_report(output_dict=True) and confusion_matrix. Values are not rounded.
"""

from __future__ import annotations

from typing import Any, Sequence

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def evaluate(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    label_names: Sequence[str],
) -> dict[str, Any]:
    label_ids = list(range(len(label_names)))
    report = classification_report(
        y_true,
        y_pred,
        labels=label_ids,
        target_names=list(label_names),
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(y_true, y_pred, labels=label_ids)
    per_class = {
        name: {
            "precision": report[name]["precision"],
            "recall": report[name]["recall"],
            "f1-score": report[name]["f1-score"],
            "support": int(report[name]["support"]),
        }
        for name in label_names
    }
    accuracy = float(accuracy_score(y_true, y_pred))
    micro = classification_report(
        y_true, y_pred, labels=label_ids, output_dict=True, zero_division=0
    )
    return {
        "accuracy": accuracy,
        "macro_precision": report["macro avg"]["precision"],
        "macro_recall": report["macro avg"]["recall"],
        "macro_f1": report["macro avg"]["f1-score"],
        # Single-label multi-class: micro P/R/F1 all equal accuracy.
        "micro_precision": accuracy,
        "micro_recall": accuracy,
        "micro_f1": accuracy,
        "weighted_f1": report["weighted avg"]["f1-score"],
        "per_class": per_class,
        "confusion_matrix": matrix.tolist(),
    }
