"""Model loading, prediction and SHAP explanation for the Streamlit app."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn
from transformers import AutoTokenizer, BertModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_prep import clean_narrative  # noqa: E402

ART = Path(__file__).parent / "artifacts"
MODEL_NAME = "bert-base-uncased"
MAX_LEN = 512


class Classifier:
    """Frozen BERT + mean pooling + trained linear head (the project's Experiment 1 setup)."""

    def __init__(self) -> None:
        torch.set_num_threads(max(1, torch.get_num_threads()))
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.bert = BertModel.from_pretrained(MODEL_NAME).eval()
        self.head = nn.Linear(768, 8)
        self.head.load_state_dict(torch.load(ART / "head.pt", map_location="cpu"))
        self.head.eval()
        self.metrics = json.loads((ART / "head_metrics.json").read_text())

    @torch.no_grad()
    def proba(self, texts: list[str], batch_size: int = 16) -> np.ndarray:
        """Class probabilities for already-cleaned texts."""
        texts = [str(t) for t in texts]  # SHAP passes a numpy array
        out = []
        for i in range(0, len(texts), batch_size):
            enc = self.tokenizer(texts[i : i + batch_size], padding=True, truncation=True, max_length=MAX_LEN, return_tensors="pt")
            hidden = self.bert(**enc).last_hidden_state
            mask = enc["attention_mask"].unsqueeze(-1).to(hidden.dtype)
            pooled = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
            out.append(torch.softmax(self.head(pooled), dim=1).numpy())
        return np.vstack(out)

    def predict(self, raw_text: str) -> tuple[str, np.ndarray]:
        cleaned = clean_narrative(raw_text)
        return cleaned, self.proba([cleaned])[0]

    def explain(self, cleaned: str, class_index: int, max_evals: int = 250, progress=None) -> list[tuple[str, float]]:
        """SHAP values (change in the predicted class's probability) for each word segment.

        ``progress`` is an optional callback receiving a number from 0 to 1 as the model re-scores
        the narrative with words hidden.
        """
        import shap

        done = {"n": 0}

        def scored(texts):
            probs = self.proba(texts, batch_size=32)
            done["n"] += len(texts)
            if progress:
                progress(min(done["n"] / max_evals, 1.0))
            return probs

        masker = shap.maskers.Text(r"\W+", mask_token="[MASK]", collapse_mask_token=False)
        explainer = shap.Explainer(scored, masker, algorithm="partition")
        result = explainer([cleaned], max_evals=max_evals, batch_size=32, silent=True)
        values = result.values[0][:, class_index]
        return list(zip(result.data[0], values.tolist()))
