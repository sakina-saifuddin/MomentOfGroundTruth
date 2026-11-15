"""BiGRU classifier with frozen pretrained FastText embeddings (PRD section 5.1)."""

from __future__ import annotations

import numpy as np
import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


class BiGRUClassifier(nn.Module):
    """Frozen embeddings -> BiGRU x2 (hidden_size per direction, dropout 0.3) -> masked mean pool
    -> Linear(2*hidden_size, 8). With the shared config (hidden_size=128) the pooled vector is 256-d."""

    def __init__(
        self,
        embedding_matrix: np.ndarray,
        hidden_size: int = 128,
        num_layers: int = 2,
        num_classes: int = 8,
        dropout: float = 0.3,
        pad_idx: int = 0,
    ) -> None:
        super().__init__()
        if num_layers < 1:
            raise ValueError("num_layers must be at least 1.")
        weights = torch.as_tensor(embedding_matrix, dtype=torch.float32)
        # freeze=True: FastText vectors are not updated during training.
        self.embedding = nn.Embedding.from_pretrained(weights, freeze=True, padding_idx=pad_idx)
        embedding_dim = weights.shape[1]
        per_direction = hidden_size  # nn.GRU hidden size per direction; concatenated output is 2x
        concat_size = 2 * hidden_size

        self.gru_layers = nn.ModuleList()
        for layer in range(num_layers):
            self.gru_layers.append(
                nn.GRU(
                    input_size=embedding_dim if layer == 0 else concat_size,
                    hidden_size=per_direction,
                    batch_first=True,
                    bidirectional=True,
                )
            )
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(concat_size, num_classes)  # raw logits, no softmax

    def forward(self, input_ids: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        """input_ids: (batch, seq_len) padded with 0; lengths: (batch,) true lengths (>=1)."""
        seq_len = input_ids.size(1)
        output = self.embedding(input_ids)
        cpu_lengths = lengths.detach().cpu()
        for gru in self.gru_layers:
            packed = pack_padded_sequence(output, cpu_lengths, batch_first=True, enforce_sorted=False)
            packed_out, _ = gru(packed)
            output, _ = pad_packed_sequence(packed_out, batch_first=True, total_length=seq_len)
            output = self.dropout(output)

        # Mean pooling over real (non-pad) timesteps of both directions -> (batch, 2*hidden_size).
        mask = (torch.arange(seq_len, device=output.device)[None, :] < lengths[:, None]).unsqueeze(-1)
        summed = (output * mask).sum(dim=1)
        pooled = summed / lengths.clamp(min=1).unsqueeze(-1).to(output.dtype)
        return self.classifier(pooled)

    def count_trainable_params(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
