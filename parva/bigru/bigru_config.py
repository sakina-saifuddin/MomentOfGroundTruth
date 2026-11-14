"""Single source of truth for BiGRU hyperparameters. Matches Muhammad's BiLSTM config so the
two RNN models are compared fairly (same data, embeddings, sizes, optimiser and stopping rule)."""

from pathlib import Path

PARVA = Path(__file__).resolve().parents[1]
ROOT = PARVA.parent

CONFIG = {
    "label_map": str(ROOT / "data" / "processed" / "label_map.json"),
    "fasttext_path": str(PARVA / "cache" / "model.bin"),  # same facebook/fasttext-en-vectors model.bin
    "freeze_embeddings": True,
    "max_length": 300,
    "max_vocab_size": 50_000,  # PAD + UNK + most frequent training words
    "embed_dim": 300,
    "hidden_size": 128,  # per direction (nn.GRU convention) -> 256 after concatenation
    "num_layers": 2,
    "dropout": 0.3,
    "batch_size": 32,
    "lr": 1e-3,
    "epochs": 30,
    "patience": 5,
    "grad_clip": 5.0,
    "seed": 42,
    "num_labels": 8,
}

EXPERIMENTS = {
    "exp1": {
        "name": "exp1_class_weighted_loss",
        "train_csv": str(ROOT / "data" / "experiment1" / "train.csv"),
        "val_csv": str(ROOT / "data" / "experiment1" / "val.csv"),
        "test_csv": str(ROOT / "data" / "experiment1" / "test.csv"),
        "class_weights": str(ROOT / "data" / "experiment1" / "class_weights.json"),
        "use_class_weights": True,
    },
    "exp2": {
        "name": "exp2_smart_oversampling",
        "train_csv": str(ROOT / "data" / "experiment2" / "train.csv"),
        "val_csv": str(ROOT / "data" / "experiment2" / "val.csv"),
        "test_csv": str(ROOT / "data" / "experiment2" / "test.csv"),
        "class_weights": None,
        "use_class_weights": False,  # plain CrossEntropyLoss()
    },
}
