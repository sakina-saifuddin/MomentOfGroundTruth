"""Sanity checks that the combined comparison reads every saved result consistently."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))
import compare_models as cm  # noqa: E402


def test_all_eight_runs_load():
    runs = cm.load_all()
    assert len(runs) == 8
    assert {(r.model_key, r.experiment) for r in runs} == {(m[0], e) for m in cm.MODELS for e in (1, 2)}


def test_runs_share_the_same_test_set():
    for r in cm.load_all():
        assert sum(v["support"] for v in r.per_class.values()) == 458
        assert int(r.confusion.sum()) == 458
        assert r.classes == cm.load_all()[0].classes


def test_reported_macro_f1_matches_per_class_mean():
    for r in cm.load_all():
        assert abs(np.mean([v["f1"] for v in r.per_class.values()]) - r.macro_f1) < 1e-6, r.label


def test_accuracy_matches_confusion_diagonal():
    for r in cm.load_all():
        assert abs(np.trace(r.confusion) / r.confusion.sum() - r.accuracy) < 1e-6, r.label
