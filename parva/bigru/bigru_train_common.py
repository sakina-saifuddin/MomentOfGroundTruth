"""Shared training pipeline for both experiments. Hyperparameters live in bigru_config.py.

Exp 1: data/experiment1/train.csv, class-weighted CrossEntropyLoss.
Exp 2: data/experiment2/train.csv (real + synthetic), plain CrossEntropyLoss.
The test set is touched exactly once, after training, using the best-validation checkpoint.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import f1_score
from torch import nn
from torch.utils.data import DataLoader

PARVA = Path(__file__).resolve().parents[1]
for path in (str(PARVA), str(PARVA / "bigru")):
    if path not in sys.path:
        sys.path.insert(0, path)

from bigru_config import CONFIG, EXPERIMENTS  # noqa: E402
from bigru_data import NarrativeDataset, build_embedding_matrix, build_vocab, collate_batch  # noqa: E402
from bigru_evaluate import evaluate_checkpoint, predict, save_confusion_matrix_plot  # noqa: E402
from bigru_model import BiGRUClassifier  # noqa: E402


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def pick_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def val_loss_and_f1(model, loader, loss_fn, device) -> tuple[float, float]:
    model.eval()
    total, count = 0.0, 0
    y_true, y_pred = [], []
    with torch.no_grad():
        for batch in loader:
            labels = batch["label"].to(device)
            logits = model(batch["input_ids"].to(device), batch["lengths"].to(device))
            total += float(loss_fn(logits, labels).item()) * len(labels)
            count += len(labels)
            y_true.extend(labels.cpu().tolist())
            y_pred.extend(logits.argmax(dim=1).cpu().tolist())
    return total / count, float(f1_score(y_true, y_pred, average="macro", zero_division=0))


def run(experiment: str) -> None:
    exp = EXPERIMENTS[experiment]
    cfg = dict(CONFIG)
    parser = argparse.ArgumentParser(description=f"BiGRU {experiment}")
    parser.add_argument("--fasttext-path", default=cfg["fasttext_path"])
    parser.add_argument("--smoke-test", action="store_true",
                        help="Random embeddings, 1 epoch; writes *_smoke files only.")
    args = parser.parse_args()

    needed = [exp["train_csv"], exp["val_csv"], exp["test_csv"], cfg["label_map"]]
    if exp["use_class_weights"]:
        needed.append(exp["class_weights"])
    for f in needed:
        if not Path(f).is_file():
            raise FileNotFoundError(f"Required input not found: {f}")

    set_seed(cfg["seed"])
    device = pick_device()
    print(f"Experiment: {exp['name']} | device: {device}")

    labels = json.loads(Path(cfg["label_map"]).read_text(encoding="utf-8"))
    label_names = [labels["id2label"][str(i)] for i in range(cfg["num_labels"])]

    weight_tensor = None
    if exp["use_class_weights"]:
        data = json.loads(Path(exp["class_weights"]).read_text(encoding="utf-8"))
        if data["label_order"] != label_names:
            raise ValueError("class_weights.json label order does not match label_map.json.")
        weight_tensor = torch.tensor(data["ordered_by_label"], dtype=torch.float32, device=device)
    loss_fn = nn.CrossEntropyLoss(weight=weight_tensor)  # exp2: weight=None -> plain loss
    print(f"Loss: CrossEntropyLoss(weight={'class weights' if weight_tensor is not None else 'None'})")

    train_texts = pd.read_csv(exp["train_csv"])["narrative_clean"].dropna().tolist()
    vocab = build_vocab(train_texts, cfg["max_vocab_size"])
    print(f"Training rows: {len(train_texts):,} | vocabulary size: {len(vocab):,}")

    if args.smoke_test:
        embedding = np.random.default_rng(cfg["seed"]).normal(size=(len(vocab), cfg["embed_dim"])).astype(np.float32)
        embedding[0] = 0
        cfg["epochs"] = 1
    else:
        embedding = build_embedding_matrix(vocab, args.fasttext_path, PARVA / "cache" / experiment)
        if embedding.shape[1] != cfg["embed_dim"]:
            raise ValueError(f"Embedding dim {embedding.shape[1]} != config embed_dim {cfg['embed_dim']}.")

    train_ds = NarrativeDataset(exp["train_csv"], vocab, cfg["max_length"])
    val_ds = NarrativeDataset(exp["val_csv"], vocab, cfg["max_length"])
    gen = torch.Generator().manual_seed(cfg["seed"])
    train_loader = DataLoader(train_ds, batch_size=cfg["batch_size"], shuffle=True, collate_fn=collate_batch, generator=gen)
    val_loader = DataLoader(val_ds, batch_size=64, shuffle=False, collate_fn=collate_batch)

    model = BiGRUClassifier(embedding, hidden_size=cfg["hidden_size"], num_layers=cfg["num_layers"],
                            num_classes=cfg["num_labels"], dropout=cfg["dropout"]).to(device)
    if cfg["freeze_embeddings"] != (not model.embedding.weight.requires_grad):
        raise RuntimeError("Embedding freeze state does not match config.")
    print(f"Trainable parameters: {model.count_trainable_params():,} | embeddings frozen: {cfg['freeze_embeddings']}")
    optimizer = torch.optim.Adam((q for q in model.parameters() if q.requires_grad), lr=cfg["lr"])

    out_dir = PARVA / "bigru"
    suffix = "_smoke" if args.smoke_test else ""
    ckpt_path = out_dir / f"bigru_best_{experiment}{suffix}.pt"
    hyper = {
        "embedding_dim": int(embedding.shape[1]), "hidden_size": cfg["hidden_size"],
        "num_layers": cfg["num_layers"], "dropout": cfg["dropout"], "max_len": cfg["max_length"],
        "max_vocab_size": cfg["max_vocab_size"], "lr": cfg["lr"], "batch_size": cfg["batch_size"],
        "max_epochs": cfg["epochs"], "patience": cfg["patience"], "grad_clip": cfg["grad_clip"],
        "optimizer": "Adam", "seed": cfg["seed"], "freeze_embeddings": cfg["freeze_embeddings"],
        "train_csv": Path(exp["train_csv"]).relative_to(PARVA.parent).as_posix(),
        "loss": "CrossEntropyLoss(weight=class_weights)" if exp["use_class_weights"] else "CrossEntropyLoss()",
    }

    best_f1, best_epoch, stale, history = float("-inf"), 0, 0, []
    for epoch in range(1, cfg["epochs"] + 1):
        model.train()
        total, count = 0.0, 0
        for batch in train_loader:
            y = batch["label"].to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = loss_fn(model(batch["input_ids"].to(device), batch["lengths"].to(device)), y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=cfg["grad_clip"])
            optimizer.step()
            total += float(loss.item()) * len(y)
            count += len(y)
        v_loss, v_f1 = val_loss_and_f1(model, val_loader, loss_fn, device)
        history.append({"epoch": epoch, "train_loss": total / count, "val_loss": v_loss, "val_macro_f1": v_f1})
        print(f"Epoch {epoch:02d}/{cfg['epochs']} | train loss {total / count:.4f} | val loss {v_loss:.4f} | val macro-F1 {v_f1:.4f}")
        if v_f1 > best_f1:
            best_f1, best_epoch, stale = v_f1, epoch, 0
            torch.save({"model_state_dict": model.state_dict(), "vocab": vocab, "hyperparameters": hyper,
                        "best_epoch": epoch, "best_val_macro_f1": v_f1}, ckpt_path)
        else:
            stale += 1
            if stale >= cfg["patience"]:
                print(f"Early stopping: no validation macro-F1 improvement for {cfg['patience']} epochs.")
                break

    metrics = evaluate_checkpoint(ckpt_path, Path(exp["test_csv"]), label_names, device)
    results = {"model": "BiGRU + FastText (frozen)", "experiment": exp["name"], **metrics,
               "best_val_macro_f1": best_f1, "best_epoch": best_epoch, "epochs_run": len(history),
               "hyperparameters": hyper, "training_history": history}
    results_path = out_dir / f"bigru_{experiment}_results{suffix}.json"
    results_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    save_confusion_matrix_plot(metrics["confusion_matrix"], label_names,
                               out_dir / f"bigru_{experiment}_confusion_matrix{suffix}.png",
                               f"BiGRU {experiment}: confusion matrix (row-normalised)")
    print(f"Best val macro-F1 {best_f1:.4f} (epoch {best_epoch}) | test macro-F1 {metrics['macro_f1']:.4f} "
          f"| test accuracy {metrics['accuracy']:.4f}")
    print(f"Saved: {ckpt_path.name}, {results_path.name}")
