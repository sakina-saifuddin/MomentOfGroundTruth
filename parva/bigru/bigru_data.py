"""Tokenisation, vocabulary, FastText embedding matrix and dataset for the BiGRU."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

PAD, UNK = "<pad>", "<unk>"
PAD_IDX, UNK_IDX = 0, 1
MAX_LEN = 300


def tokenize(text: str) -> list[str]:
    """Whitespace, word-level tokenisation (text is already cleaned and lowercased)."""
    return str(text).split()


def build_vocab(narratives: list[str], max_vocab_size: int = 50_000) -> dict[str, int]:
    """Vocabulary from the TRAINING narratives only: PAD, UNK, then the most frequent words
    (capped at max_vocab_size entries in total)."""
    counts = Counter(token for text in narratives for token in tokenize(text))
    vocab = {PAD: PAD_IDX, UNK: UNK_IDX}
    for token, _ in counts.most_common(max(0, max_vocab_size - len(vocab))):
        vocab[token] = len(vocab)
    return vocab


def build_embedding_matrix(vocab: dict[str, int], fasttext_path: str | Path, cache_dir: str | Path) -> np.ndarray:
    """Look every vocab word up in cc.en.300.bin (subword vectors cover OOV words). Cached as .npy."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    matrix_path = cache_dir / "embedding_matrix.npy"
    vocab_path = cache_dir / "vocab.json"
    if matrix_path.is_file() and vocab_path.is_file():
        cached_vocab = json.loads(vocab_path.read_text(encoding="utf-8"))
        if cached_vocab == vocab:
            print(f"Loaded cached embedding matrix from {matrix_path}")
            return np.load(matrix_path)

    import fasttext  # imported lazily so the rest of the code works without it

    fasttext_path = Path(fasttext_path)
    if not fasttext_path.is_file():
        raise FileNotFoundError(
            f"FastText model not found: {fasttext_path}. Download cc.en.300.bin and pass --fasttext-path."
        )
    print(f"Loading FastText model {fasttext_path} (large; this can take a few minutes)...")
    ft = fasttext.load_model(str(fasttext_path))
    dim = ft.get_dimension()
    matrix = np.zeros((len(vocab), dim), dtype=np.float32)  # PAD row stays zero
    for word, idx in vocab.items():
        if word == PAD:
            continue
        if word == UNK:
            continue
        matrix[idx] = ft.get_word_vector(word)
    # UNK = mean of all word vectors so unseen val/test words get a neutral vector.
    matrix[UNK_IDX] = matrix[2:].mean(axis=0)
    np.save(matrix_path, matrix)
    vocab_path.write_text(json.dumps(vocab, ensure_ascii=False), encoding="utf-8")
    return matrix


class NarrativeDataset(Dataset):
    """Rows of `narrative_clean` -> padded/truncated token-id tensors plus integer label."""

    def __init__(self, csv_path: str | Path, vocab: dict[str, int], max_len: int = MAX_LEN) -> None:
        frame = pd.read_csv(csv_path)
        for column in ("narrative_clean", "label"):
            if column not in frame.columns:
                raise ValueError(f"{csv_path} is missing required column '{column}'.")
        frame = frame.dropna(subset=["narrative_clean"])
        self.labels = frame["label"].astype(int).tolist()
        self.max_len = max_len
        self.samples: list[list[int]] = []
        for text in frame["narrative_clean"]:
            ids = [vocab.get(token, UNK_IDX) for token in tokenize(text)][:max_len]
            self.samples.append(ids or [UNK_IDX])

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> tuple[list[int], int]:
        return self.samples[index], self.labels[index]


def collate_batch(batch: list[tuple[list[int], int]]) -> dict[str, torch.Tensor]:
    lengths = torch.tensor([len(ids) for ids, _ in batch], dtype=torch.long)
    padded = torch.full((len(batch), int(lengths.max())), PAD_IDX, dtype=torch.long)
    for row, (ids, _) in enumerate(batch):
        padded[row, : len(ids)] = torch.tensor(ids, dtype=torch.long)
    labels = torch.tensor([label for _, label in batch], dtype=torch.long)
    return {"input_ids": padded, "lengths": lengths, "label": labels}
