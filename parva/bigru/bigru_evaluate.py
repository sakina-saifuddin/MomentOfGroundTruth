"""Evaluate a saved BiGRU checkpoint on the test set (classification report + confusion matrix).

Usage (from the repository root):
    python parva/bigru/bigru_evaluate.py --checkpoint parva/bigru/bigru_best_exp1.pt --experiment exp1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
from torch.utils.data import DataLoader

PARVA = Path(__file__).resolve().parents[1]
ROOT = PARVA.parent
for path in (str(PARVA), str(PARVA / "bigru")):
    if path not in sys.path:
        sys.path.insert(0, path)

from bigru_data import NarrativeDataset, collate_batch  # noqa: E402
from bigru_model import BiGRUClassifier  # noqa: E402
from evaluate.evaluate import evaluate  # noqa: E402


def predict(model: torch.nn.Module, loader: DataLoader, device: torch.device) -> tuple[list[int], list[int]]:
    model.eval()
    y_true: list[int] = []
    y_pred: list[int] = []
    with torch.no_grad():
        for batch in loader:
            logits = model(batch["input_ids"].to(device), batch["lengths"].to(device))
            y_true.extend(batch["label"].tolist())
            y_pred.extend(logits.argmax(dim=1).cpu().tolist())
    return y_true, y_pred


def save_confusion_matrix_plot(matrix: list[list[int]], label_names: list[str], path: Path, title: str) -> None:
    array = np.asarray(matrix, dtype=float)
    totals = array.sum(axis=1, keepdims=True)
    normalized = np.divide(array, totals, out=np.zeros_like(array), where=totals != 0)
    figure, axis = plt.subplots(figsize=(11, 8.5))
    sns.heatmap(normalized, annot=True, fmt=".2f", cmap="Blues", vmin=0, vmax=1,
                xticklabels=label_names, yticklabels=label_names, ax=axis)
    axis.set_title(title)
    axis.set_xlabel("Predicted cause")
    axis.set_ylabel("True cause")
    axis.tick_params(axis="x", labelrotation=45)
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def evaluate_checkpoint(checkpoint_path: Path, test_csv: Path, label_names: list[str],
                        device: torch.device, batch_size: int = 64) -> dict[str, Any]:
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    vocab = checkpoint["vocab"]
    cfg = checkpoint["hyperparameters"]
    model = BiGRUClassifier(
        embedding_matrix=np.zeros((len(vocab), cfg["embedding_dim"]), dtype=np.float32),
        hidden_size=cfg["hidden_size"], num_layers=cfg["num_layers"],
        num_classes=len(label_names), dropout=cfg["dropout"],
    )
    model.load_state_dict(checkpoint["model_state_dict"])  # restores the saved FastText vectors
    model.to(device)
    dataset = NarrativeDataset(test_csv, vocab, max_len=cfg["max_len"])
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, collate_fn=collate_batch)
    y_true, y_pred = predict(model, loader, device)
    return evaluate(y_true, y_pred, label_names)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default=str(PARVA / "bigru" / "bigru_best_exp1.pt"))
    parser.add_argument("--experiment", default="exp1")
    parser.add_argument("--test-csv", default=str(ROOT / "data" / "experiment1" / "test.csv"))  # identical for exp1/exp2
    parser.add_argument("--label-map", default=str(ROOT / "data" / "processed" / "label_map.json"))
    args = parser.parse_args()

    labels = json.loads(Path(args.label_map).read_text(encoding="utf-8"))
    label_names = [labels["id2label"][str(i)] for i in range(len(labels["id2label"]))]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    metrics = evaluate_checkpoint(Path(args.checkpoint), Path(args.test_csv), label_names, device)
    out_dir = PARVA / "bigru"
    save_confusion_matrix_plot(metrics["confusion_matrix"], label_names,
                               out_dir / f"bigru_{args.experiment}_confusion_matrix.png",
                               f"BiGRU {args.experiment}: confusion matrix (row-normalised)")
    print(f"Test macro-F1={metrics['macro_f1']:.4f} accuracy={metrics['accuracy']:.4f}")
    for name, scores in metrics["per_class"].items():
        print(f"{name:35} P={scores['precision']:.3f} R={scores['recall']:.3f} F1={scores['f1-score']:.3f}")


if __name__ == "__main__":
    main()
