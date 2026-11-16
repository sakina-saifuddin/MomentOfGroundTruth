"""Build the model file the Streamlit app loads.

The repository does not track trained weights, so this script recreates the project's best
configuration locally: frozen ``bert-base-uncased`` + mean pooling + one linear head (768 -> 8),
trained with class-weighted cross-entropy on ``data/experiment1/train.csv`` (Experiment 1).
Hyperparameters follow ``sakina/scripts/run_experiment_a.py``: AdamW, lr 2e-3, batch 16,
up to 20 epochs, early stopping (patience 5) on validation macro-F1, seed 42.

Because BERT is frozen, every narrative is encoded once and the pooled vectors are cached in
``app/artifacts/features_*.npy``; the head then trains in seconds. The small head file
(``head.pt``, ~25 KB) and its measured test scores (``head_metrics.json``) are written next to it.

Run from the repository root::

    python app/build_head.py
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, f1_score
from torch import nn
from transformers import AutoTokenizer, BertModel

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "app" / "artifacts"
MODEL_NAME = "bert-base-uncased"
MAX_LEN = 512
SEED = 42


def encode(texts: list[str], tokenizer, bert, batch_size: int = 16) -> np.ndarray:
    """Mean-pooled (padding ignored) BERT vectors, in the original row order."""
    order = np.argsort([len(t) for t in texts])
    out = np.zeros((len(texts), 768), dtype=np.float32)
    with torch.no_grad():
        for start in range(0, len(texts), batch_size):
            idx = order[start : start + batch_size]
            enc = tokenizer([texts[i] for i in idx], padding=True, truncation=True, max_length=MAX_LEN, return_tensors="pt")
            hidden = bert(**enc).last_hidden_state
            mask = enc["attention_mask"].unsqueeze(-1).to(hidden.dtype)
            out[idx] = ((hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-9)).numpy()
            if (start // batch_size) % 10 == 0:
                print(f"  encoded {min(start + batch_size, len(texts))}/{len(texts)}", flush=True)
    return out


def get_features(split: str, tokenizer, bert) -> tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(ROOT / "data" / "experiment1" / f"{split}.csv")
    path = ART / f"features_{split}.npy"
    if path.exists():
        return np.load(path), df["label"].to_numpy()
    print(f"Encoding {split} ({len(df)} narratives)...", flush=True)
    feats = encode(df["narrative_clean"].tolist(), tokenizer, bert)
    np.save(path, feats)
    return feats, df["label"].to_numpy()


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    bert = BertModel.from_pretrained(MODEL_NAME).eval()
    data = {s: get_features(s, tokenizer, bert) for s in ("train", "val", "test")}

    weights = torch.tensor(json.loads((ROOT / "data" / "experiment1" / "class_weights.json").read_text())["ordered_by_label"], dtype=torch.float32)
    xt, yt = torch.tensor(data["train"][0]), torch.tensor(data["train"][1])
    head = nn.Linear(768, 8)
    opt = torch.optim.AdamW(head.parameters(), lr=2e-3)
    loss_fn = nn.CrossEntropyLoss(weight=weights)

    def predict(x):
        with torch.no_grad():
            return head(torch.tensor(x)).argmax(1).numpy()

    best, best_state, best_epoch, bad = -1.0, None, 0, 0
    for epoch in range(1, 21):
        head.train()
        perm = torch.randperm(len(xt))
        for i in range(0, len(xt), 16):
            b = perm[i : i + 16]
            opt.zero_grad(); loss_fn(head(xt[b]), yt[b]).backward(); opt.step()
        val_f1 = f1_score(data["val"][1], predict(data["val"][0]), average="macro")
        print(f"epoch {epoch:2d}  val macro-F1 {val_f1:.4f}", flush=True)
        if val_f1 > best:
            best, best_epoch, bad = val_f1, epoch, 0
            best_state = {k: v.clone() for k, v in head.state_dict().items()}
        else:
            bad += 1
            if bad >= 5:
                break
    head.load_state_dict(best_state)
    pred = predict(data["test"][0])
    metrics = {
        "model": f"{MODEL_NAME} (frozen) + mean pooling + linear head, Experiment 1 settings",
        "best_epoch": best_epoch,
        "val_macro_f1": best,
        "test_accuracy": float(accuracy_score(data["test"][1], pred)),
        "test_macro_f1": float(f1_score(data["test"][1], pred, average="macro")),
        "test_rows": int(len(pred)),
        "note": "Retrained locally for the app; close to but not identical to the Colab run in sakina/results_mean_pooling/.",
    }
    torch.save(best_state, ART / "head.pt")
    (ART / "head_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    sys.exit(main())
