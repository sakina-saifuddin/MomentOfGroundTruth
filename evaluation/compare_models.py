"""Combine every model's saved test results into one comparison (3 models x 2 experiments).

Reads the metrics files each teammate already committed and writes:

* ``reports/final_comparison.md``  - master tables and written findings
* ``evaluation/master_results.csv`` / ``master_results.json`` - one row per run
* ``reports/figures/final/*.png``  - comparison figures

Nothing is retrained and no number is estimated: every value comes from a saved
``metrics.json`` / ``*_results.json`` file. The three teammates saved slightly different
schemas (``f1`` vs ``f1-score``, different top-level keys), so ``load_run`` normalises them.
Macro precision/recall and weighted F1 are recomputed from the per-class blocks for every run
so the same definition is used everywhere.

Run from the repository root::

    python evaluation/compare_models.py
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "reports" / "figures" / "final"
REPORT_PATH = ROOT / "reports" / "final_comparison.md"
CSV_PATH = ROOT / "evaluation" / "master_results.csv"
JSON_PATH = ROOT / "evaluation" / "master_results.json"

EXPERIMENTS = {
    1: "Exp 1: class-weighted loss",
    2: "Exp 2: smart oversampling",
}

# (model key, display name, {experiment: path to saved results})
MODELS = [
    (
        "bigru",
        "BiGRU + FastText",
        {
            1: ROOT / "parva" / "bigru" / "bigru_exp1_results.json",
            2: ROOT / "parva" / "bigru" / "bigru_exp2_results.json",
        },
    ),
    (
        "bilstm",
        "BiLSTM + attention + FastText",
        {
            1: ROOT / "muhammad" / "results" / "experiment_a" / "metrics.json",
            2: ROOT / "muhammad" / "results" / "experiment_b" / "metrics.json",
        },
    ),
    (
        "bert_mean",
        "Frozen BERT, mean pooling",
        {
            1: ROOT / "sakina" / "results_mean_pooling" / "experiment_a" / "metrics.json",
            2: ROOT / "sakina" / "results_mean_pooling" / "experiment_b" / "metrics.json",
        },
    ),
    (
        "bert_pooler",
        "Frozen BERT, pooler_output",
        {
            1: ROOT / "sakina" / "results" / "experiment_a" / "metrics.json",
            2: ROOT / "sakina" / "results" / "experiment_b" / "metrics.json",
        },
    ),
]

# Colour-blind-safe (Okabe-Ito) colours, one per model.
MODEL_COLORS = {
    "bigru": "#009E73",
    "bilstm": "#E69F00",
    "bert_mean": "#0072B2",
    "bert_pooler": "#56B4E9",
}


@dataclass
class Run:
    """One model trained under one experiment, with every metric on the test set."""

    model_key: str
    model: str
    experiment: int
    accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    micro_f1: float
    weighted_f1: float
    best_val_macro_f1: float
    best_epoch: int
    epochs_run: int
    trainable_parameters: int | None
    classes: list[str]
    per_class: dict[str, dict[str, float]]
    confusion: np.ndarray
    history: list[dict]

    @property
    def label(self) -> str:
        return f"{self.model} / Exp {self.experiment}"


def load_run(model_key: str, model: str, experiment: int, path: Path) -> Run:
    """Load one results file and normalise it to a ``Run``."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    classes = list(raw["per_class"])
    per_class = {
        name: {
            "precision": float(v["precision"]),
            "recall": float(v["recall"]),
            "f1": float(v["f1"] if "f1" in v else v["f1-score"]),
            "support": int(v["support"]),
        }
        for name, v in raw["per_class"].items()
    }
    support = np.array([per_class[c]["support"] for c in classes], dtype=float)
    f1 = np.array([per_class[c]["f1"] for c in classes])
    history = raw["training_history"]
    best_val = raw.get("best_val_f1", raw.get("best_val_macro_f1"))
    return Run(
        model_key=model_key,
        model=model,
        experiment=experiment,
        accuracy=float(raw["accuracy"]),
        macro_precision=float(np.mean([per_class[c]["precision"] for c in classes])),
        macro_recall=float(np.mean([per_class[c]["recall"] for c in classes])),
        macro_f1=float(raw["macro_f1"]),
        micro_f1=float(raw["micro_f1"]),
        weighted_f1=float((f1 * support).sum() / support.sum()),
        best_val_macro_f1=float(best_val),
        best_epoch=int(raw["best_epoch"]),
        epochs_run=int(raw.get("epochs_run", len(history))),
        trainable_parameters=raw.get("trainable_parameters"),
        classes=classes,
        per_class=per_class,
        confusion=np.array(raw["confusion_matrix"], dtype=int),
        history=history,
    )


def load_all() -> list[Run]:
    return [load_run(key, name, exp, path) for key, name, paths in MODELS for exp, path in paths.items()]


def short(cls: str) -> str:
    """Readable class name for axis labels."""
    names = {
        "MATERIAL FAILURE OF PIPE OR WELD": "Material failure",
        "OTHER OUTSIDE FORCE DAMAGE": "Other outside force",
        "OTHER INCIDENT CAUSE": "Other incident cause",
    }
    return names.get(cls, cls.title())


# --------------------------------------------------------------------------- figures


def _style(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)


def fig_overall(runs: list[Run]) -> None:
    """Macro-F1 and accuracy per model, Exp 1 vs Exp 2 side by side."""
    keys = [m[0] for m in MODELS]
    names = {m[0]: m[1] for m in MODELS}
    by = {(r.model_key, r.experiment): r for r in runs}
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    for ax, (metric, title) in zip(axes, [("macro_f1", "Test macro-F1"), ("accuracy", "Test accuracy")]):
        x = np.arange(len(keys))
        w = 0.38
        for j, exp in enumerate((1, 2)):
            vals = [getattr(by[(k, exp)], metric) for k in keys]
            hatch = "" if exp == 1 else "//"
            bars = ax.bar(
                x + (j - 0.5) * w,
                vals,
                w,
                color=[MODEL_COLORS[k] for k in keys],
                hatch=hatch,
                edgecolor="white" if exp == 1 else "#222222",
                linewidth=0.6,
            )
            ax.bar_label(bars, fmt="%.3f", fontsize=8, padding=2)
        ax.set_xticks(x, [names[k].replace(", ", ",\n").replace(" + ", " +\n", 1) for k in keys], fontsize=8)
        ax.set_title(title)
        ax.set_ylim(0, 0.75)
        _style(ax)
    axes[0].set_ylabel("Score on 458 held-out test narratives")
    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor="#888888", edgecolor="white"),
        plt.Rectangle((0, 0), 1, 1, facecolor="#888888", hatch="//", edgecolor="#222222"),
    ]
    axes[1].legend(handles, [EXPERIMENTS[1], EXPERIMENTS[2]], fontsize=8, loc="upper right")
    fig.suptitle("Three models x two class-imbalance strategies (BERT shown with both pooling methods)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "01_overall_comparison.png", dpi=160)
    plt.close(fig)


def fig_heatmap(runs: list[Run]) -> None:
    """Per-class F1 for all eight runs."""
    classes = runs[0].classes
    data = np.array([[r.per_class[c]["f1"] for r in runs] for c in classes])
    fig, ax = plt.subplots(figsize=(12, 5.2))
    im = ax.imshow(data, cmap="viridis", vmin=0, vmax=0.85, aspect="auto")
    ax.set_xticks(
        range(len(runs)),
        [f"{r.model.replace(', ', chr(10))}\nExp {r.experiment}".replace(" + ", " +\n", 1) for r in runs],
        fontsize=7.5,
    )
    ax.set_yticks(range(len(classes)), [short(c) for c in classes], fontsize=9)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center", fontsize=8, color="white" if data[i, j] < 0.5 else "black")
    fig.colorbar(im, ax=ax, label="Test F1")
    ax.set_title("Per-class test F1, every model and experiment")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "02_per_class_f1_heatmap.png", dpi=160)
    plt.close(fig)


def fig_delta(runs: list[Run]) -> None:
    """Per-class F1 change when moving from class weights (Exp 1) to oversampling (Exp 2)."""
    by = {(r.model_key, r.experiment): r for r in runs}
    classes = runs[0].classes
    keys = [m[0] for m in MODELS]
    names = {m[0]: m[1] for m in MODELS}
    x = np.arange(len(classes))
    w = 0.2
    fig, ax = plt.subplots(figsize=(12, 4.8))
    for i, k in enumerate(keys):
        d = [by[(k, 2)].per_class[c]["f1"] - by[(k, 1)].per_class[c]["f1"] for c in classes]
        ax.bar(x + (i - 1.5) * w, d, w, label=names[k], color=MODEL_COLORS[k])
    ax.axhline(0, color="#222222", linewidth=0.8)
    ax.set_xticks(x, [short(c) for c in classes], rotation=25, ha="right", fontsize=9)
    ax.set_ylabel("Test F1 change (Exp 2 minus Exp 1)")
    ax.set_title("Did oversampling help each class? Above zero = oversampling scored higher")
    ax.legend(fontsize=8)
    _style(ax)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "03_oversampling_effect_per_class.png", dpi=160)
    plt.close(fig)


def fig_confusions(runs: list[Run]) -> None:
    """Row-normalised confusion matrices for all runs (rows = true cause)."""
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    classes = runs[0].classes
    labels = [short(c) for c in classes]
    by = {(r.model_key, r.experiment): r for r in runs}
    for col, (key, name, _) in enumerate(MODELS):
        for row, exp in enumerate((1, 2)):
            r = by[(key, exp)]
            cm = r.confusion.astype(float)
            norm = cm / cm.sum(axis=1, keepdims=True)
            ax = axes[row, col]
            ax.imshow(norm, cmap="Blues", vmin=0, vmax=1)
            for i in range(8):
                for j in range(8):
                    ax.text(j, i, f"{norm[i, j]:.2f}", ha="center", va="center", fontsize=6.5, color="white" if norm[i, j] > 0.5 else "black")
            ax.set_xticks(range(8), labels, rotation=60, ha="right", fontsize=7)
            ax.set_yticks(range(8), labels if col == 0 else [""] * 8, fontsize=7)
            ax.set_title(f"{name}\nExp {exp}  (macro-F1 {r.macro_f1:.3f})", fontsize=9)
            if row == 1:
                ax.set_xlabel("Predicted cause", fontsize=8)
            if col == 0:
                ax.set_ylabel("True cause", fontsize=8)
    fig.suptitle("Confusion matrices, each row normalised to the share of that true cause", fontsize=13)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "04_confusion_matrices.png", dpi=130)
    plt.close(fig)


def fig_curves(runs: list[Run]) -> None:
    """Validation macro-F1 per epoch, one panel per experiment."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ax, exp in zip(axes, (1, 2)):
        for r in runs:
            if r.experiment != exp:
                continue
            ax.plot(
                [h["epoch"] for h in r.history],
                [h["val_macro_f1"] for h in r.history],
                label=r.model,
                color=MODEL_COLORS[r.model_key],
                linewidth=2,
            )
            ax.scatter([r.best_epoch], [r.best_val_macro_f1], color=MODEL_COLORS[r.model_key], zorder=3, s=30)
        ax.set_title(EXPERIMENTS[exp])
        ax.set_xlabel("Epoch")
        _style(ax)
    axes[0].set_ylabel("Validation macro-F1")
    axes[0].legend(fontsize=8)
    fig.suptitle("Validation macro-F1 during training (dot = checkpoint kept)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "05_validation_curves.png", dpi=160)
    plt.close(fig)


def fig_params(runs: list[Run]) -> None:
    """Trainable parameters against test macro-F1."""
    fig, ax = plt.subplots(figsize=(8, 5))
    plotted = [r for r in runs if r.trainable_parameters]
    for r in plotted:
        ax.scatter(
            r.trainable_parameters,
            r.macro_f1,
            s=90,
            color=MODEL_COLORS[r.model_key],
            marker="o" if r.experiment == 1 else "s",
            edgecolor="#222222",
            linewidth=0.6,
        )
        ax.annotate(f"Exp {r.experiment}", (r.trainable_parameters, r.macro_f1), textcoords="offset points", xytext=(7, 4), fontsize=8)
    ax.set_xscale("log")
    ax.set_xlabel("Trainable parameters (log scale)")
    ax.set_ylabel("Test macro-F1")
    ax.set_title("Model size vs score (circle = Exp 1, square = Exp 2)")
    handles = [plt.Line2D([], [], marker="o", linestyle="", color=MODEL_COLORS[k], label=n) for k, n, _ in MODELS if any(r.model_key == k and r.trainable_parameters for r in runs)]
    ax.legend(handles=handles, fontsize=8, loc="lower right")
    _style(ax)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "06_params_vs_macro_f1.png", dpi=160)
    plt.close(fig)


def fig_pooling(runs: list[Run]) -> None:
    """Focused view of the two BERT pooling methods."""
    by = {(r.model_key, r.experiment): r for r in runs}
    classes = runs[0].classes
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    x = np.arange(len(classes))
    w = 0.38
    for ax, exp in zip(axes, (1, 2)):
        for j, key in enumerate(("bert_pooler", "bert_mean")):
            r = by[(key, exp)]
            ax.bar(x + (j - 0.5) * w, [r.per_class[c]["f1"] for c in classes], w, color=MODEL_COLORS[key], label=f"{r.model} (macro-F1 {r.macro_f1:.3f})")
        ax.set_xticks(x, [short(c) for c in classes], rotation=30, ha="right", fontsize=8)
        ax.set_title(EXPERIMENTS[exp])
        ax.legend(fontsize=8, loc="upper right")
        ax.set_ylim(0, 0.95)
        _style(ax)
    axes[0].set_ylabel("Test F1")
    fig.suptitle("Frozen BERT: [CLS] pooler_output vs mean pooling, per class")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "07_bert_pooling_per_class.png", dpi=160)
    plt.close(fig)


# --------------------------------------------------------------------------- tables


def top_confusions(run: Run, n: int = 3) -> list[tuple[str, str, int, float]]:
    """Largest off-diagonal confusion cells as (true, predicted, count, share of true class)."""
    cells = []
    for i, true in enumerate(run.classes):
        total = run.confusion[i].sum()
        for j, pred in enumerate(run.classes):
            if i != j and run.confusion[i, j] > 0:
                cells.append((true, pred, int(run.confusion[i, j]), run.confusion[i, j] / total))
    return sorted(cells, key=lambda c: -c[2])[:n]


def md_table(header: list[str], rows: list[list[str]], left_cols: int = 1) -> str:
    align = ["---"] * left_cols + ["---:"] * (len(header) - left_cols)
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(align) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def write_tables(runs: list[Run]) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    fields = ["model", "experiment", "accuracy", "macro_precision", "macro_recall", "macro_f1", "micro_f1", "weighted_f1", "best_val_macro_f1", "best_epoch", "epochs_run", "trainable_parameters"]
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for r in runs:
            w.writerow([getattr(r, k) for k in fields])
    payload = [
        {**{k: getattr(r, k) for k in fields}, "per_class_f1": {c: r.per_class[c]["f1"] for c in r.classes}}
        for r in runs
    ]
    JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_report(runs: list[Run]) -> str:
    by = {(r.model_key, r.experiment): r for r in runs}
    classes = runs[0].classes
    keys = [m[0] for m in MODELS]
    names = {m[0]: m[1] for m in MODELS}

    master = md_table(
        ["Model", "Experiment", "Accuracy", "Macro-P", "Macro-R", "Macro-F1", "Micro-F1", "Weighted F1", "Best val macro-F1"],
        [
            [names[k], f"Exp {e}", f"{r.accuracy:.4f}", f"{r.macro_precision:.4f}", f"{r.macro_recall:.4f}", f"**{r.macro_f1:.4f}**", f"{r.micro_f1:.4f}", f"{r.weighted_f1:.4f}", f"{r.best_val_macro_f1:.4f}"]
            for k in keys
            for e in (1, 2)
            for r in [by[(k, e)]]
        ],
        left_cols=2,
    )

    per_class_f1 = md_table(
        ["Cause"] + [f"{names[k].replace('Frozen ', '').replace(' + FastText', '').replace(' + attention', '+attn')} E{e}" for k in keys for e in (1, 2)],
        [[short(c)] + [f"{by[(k, e)].per_class[c]['f1']:.3f}" for k in keys for e in (1, 2)] for c in classes],
    )

    def prf_block(exp: int) -> str:
        header = ["Cause"] + [f"{lab} {m}" for lab in ("BiGRU", "BiLSTM", "BERT mean", "BERT pooler") for m in ("P", "R", "F1")]
        rows = []
        for c in classes:
            row = [short(c)]
            for k in keys:
                pc = by[(k, exp)].per_class[c]
                row += [f"{pc['precision']:.3f}", f"{pc['recall']:.3f}", f"{pc['f1']:.3f}"]
            rows.append(row)
        return md_table(header, rows)

    # ranking by test macro-F1 and by validation macro-F1
    ranked_test = sorted(runs, key=lambda r: -r.macro_f1)
    ranked_val = sorted(runs, key=lambda r: -r.best_val_macro_f1)
    rank_rows = [[f"{i + 1}", r.label, f"{r.macro_f1:.4f}", f"{r.accuracy:.4f}", f"{r.best_val_macro_f1:.4f}"] for i, r in enumerate(ranked_test)]
    rank_table = md_table(["Rank (test macro-F1)", "Run", "Test macro-F1", "Test accuracy", "Best val macro-F1"], rank_rows, left_cols=2)

    best_mean = max((by[("bert_mean", e)] for e in (1, 2)), key=lambda r: r.macro_f1)
    best_val_run = ranked_val[0]
    best_test_run = ranked_test[0]

    # per-model Exp1 vs Exp2
    exp_rows = []
    for k in keys:
        a, b = by[(k, 1)], by[(k, 2)]
        exp_rows.append([names[k], f"{a.macro_f1:.4f}", f"{b.macro_f1:.4f}", f"{b.macro_f1 - a.macro_f1:+.4f}", f"{a.accuracy:.4f}", f"{b.accuracy:.4f}", f"{b.accuracy - a.accuracy:+.4f}"])
    exp_table = md_table(["Model", "Exp 1 macro-F1", "Exp 2 macro-F1", "Change", "Exp 1 accuracy", "Exp 2 accuracy", "Change"], exp_rows)

    # pooling difference
    pool_rows = []
    for e in (1, 2):
        p, m = by[("bert_pooler", e)], by[("bert_mean", e)]
        pool_rows.append([f"Exp {e}", f"{p.accuracy:.4f}", f"{m.accuracy:.4f}", f"{m.accuracy - p.accuracy:+.4f}", f"{p.macro_f1:.4f}", f"{m.macro_f1:.4f}", f"{m.macro_f1 - p.macro_f1:+.4f}"])
    pool_table = md_table(["Experiment", "pooler acc", "mean acc", "Change", "pooler macro-F1", "mean macro-F1", "Change"], pool_rows)

    # hardest classes: average F1 over the 6 non-pooler runs
    main_runs = [r for r in runs if r.model_key != "bert_pooler"]
    avg = sorted(((np.mean([r.per_class[c]["f1"] for r in main_runs]), c) for c in classes))
    hardest = ", ".join(f"{short(c)} ({v:.2f})" for v, c in avg[:3])
    easiest = ", ".join(f"{short(c)} ({v:.2f})" for v, c in avg[::-1][:2])

    # confusions for the best run
    conf_lines = "\n".join(f"- {short(t)} predicted as {short(p)}: {n} narratives ({s:.0%} of that cause)" for t, p, n, s in top_confusions(best_test_run, 4))

    # oversampling winners
    over_lines = []
    for k in keys:
        a, b = by[(k, 1)], by[(k, 2)]
        better = [short(c) for c in classes if b.per_class[c]["f1"] > a.per_class[c]["f1"]]
        over_lines.append(f"- {names[k]}: Exp 2 scored higher on {len(better)} of 8 classes ({', '.join(better) if better else 'none'}).")

    n_params = {k: by[(k, 1)].trainable_parameters for k in keys}

    lines = [
        "# Final comparison: 3 models x 2 experiments",
        "",
        "Every number below is read from a saved results file (see *Sources*) and measured on the same 458 held-out",
        "test narratives. Nothing here was retrained or estimated. Regenerate everything with",
        "`python evaluation/compare_models.py`.",
        "",
        "**Models.** BiGRU + FastText (Parva), BiLSTM + attention + FastText (Muhammad), frozen BERT-base-uncased with a",
        "linear head (Sakina). Frozen BERT was run with two pooling methods, so it appears twice: **mean pooling** is the",
        "main BERT result, and **`pooler_output`** (`[CLS]` through BERT's pooler layer, the PRD's original design) is",
        "kept alongside it so the two can be told apart. That makes 4 model rows x 2 experiments = 8 result sets.",
        "",
        "**Experiments.** Exp 1 trains on the original training split with class-weighted cross-entropy. Exp 2 trains on the",
        "training split plus validated synthetic narratives with plain cross-entropy. Validation and test sets are",
        "identical in both. (Sakina's folders call these `experiment_a` / `experiment_b`; Muhammad's do the same; Parva's",
        "call them `exp1` / `exp2`.)",
        "",
        "## 1. Master table (test set)",
        "",
        master,
        "",
        "Micro-F1 equals accuracy for single-label classification, so they match in every row. Macro-P and Macro-R are the",
        "unweighted mean of the eight per-class values, recomputed from each file's per-class block so all models use one",
        "definition. Weighted F1 weights each class by its test support.",
        "",
        "![Overall comparison](figures/final/01_overall_comparison.png)",
        "",
        "### Ranking",
        "",
        rank_table,
        "",
        f"- **Highest test macro-F1:** {best_test_run.label} ({best_test_run.macro_f1:.4f}).",
        f"- **Highest validation macro-F1:** {best_val_run.label} ({best_val_run.best_val_macro_f1:.4f}).",
        "",
        "Choosing a final model on validation score and then reporting the test score avoids picking the answer that",
        "happens to look best on the test set. When the two rankings disagree, treat the top runs as close.",
        "",
        "## 2. Does the imbalance strategy matter? (Exp 1 vs Exp 2)",
        "",
        exp_table,
        "",
        "Per-class view of the same question:",
        "",
        *over_lines,
        "",
        "![Oversampling effect](figures/final/03_oversampling_effect_per_class.png)",
        "",
        "## 3. Per-class results",
        "",
        "Test F1 by cause (E1 = Exp 1, E2 = Exp 2):",
        "",
        per_class_f1,
        "",
        "![Per-class F1 heatmap](figures/final/02_per_class_f1_heatmap.png)",
        "",
        f"Hardest causes on average across the six main runs: {hardest}. Easiest: {easiest}.",
        "",
        "<details><summary>Full precision / recall / F1 per class, Exp 1</summary>",
        "",
        prf_block(1),
        "",
        "</details>",
        "",
        "<details><summary>Full precision / recall / F1 per class, Exp 2</summary>",
        "",
        prf_block(2),
        "",
        "</details>",
        "",
        "## 4. Frozen BERT: mean pooling vs `pooler_output`",
        "",
        "Same frozen `bert-base-uncased`, same 768 -> 8 linear head (6,152 trainable parameters), same data and",
        "hyperparameters. Only the step that turns token vectors into one narrative vector differs.",
        "",
        "- **`pooler_output`:** the `[CLS]` vector passed through BERT's pooler layer. One token carries the whole summary.",
        "- **Mean pooling:** the average of every real token vector (padding ignored). Every token contributes.",
        "",
        pool_table,
        "",
        "![BERT pooling per class](figures/final/07_bert_pooling_per_class.png)",
        "",
        "With the transformer frozen, `[CLS]` and its pooler were never trained for this task, so a single token is a weak",
        "summary of a narrative whose median length is 136 words. Averaging keeps information from the whole text. This is a measured difference,",
        "not a tested explanation; confirming the reason would need repeated runs with different seeds.",
        "",
        "## 5. Error analysis",
        "",
        f"Most frequent mistakes for the highest test macro-F1 run ({best_test_run.label}):",
        "",
        conf_lines,
        "",
        "![Confusion matrices](figures/final/04_confusion_matrices.png)",
        "",
        "## 6. Training behaviour and model size",
        "",
        "![Validation curves](figures/final/05_validation_curves.png)",
        "",
        f"Trainable parameters: BiGRU {by[('bigru', 1)].trainable_parameters or 'not recorded in its results file'}, "
        f"BiLSTM + attention {n_params['bilstm']:,}, frozen BERT {n_params['bert_mean']:,}. "
        "BiGRU's results file records hyperparameters but not a parameter count, so it is left out of the size plot.",
        "",
        "![Parameters vs macro-F1](figures/final/06_params_vs_macro_f1.png)",
        "",
        "## 7. Caveats",
        "",
        "- Each run is a single seed (42) on a 458-row test set. Differences of a few hundredths in macro-F1 are within what",
        "  a different seed or split could change; the rare classes (25-31 test rows each) move the macro average a lot.",
        "- The models were trained with separate code and settings, so differences mix architecture with training",
        "  choices.",
        "- Exp 2 depends on the synthetic narratives being faithful to their label. A review sample is in",
        "  `reports/synthetic_review_sample.md`; the results are only as good as that review.",
        "- The FastText models and BERT see different tokenisation and sequence lengths (300 word tokens vs up to 512",
        "  WordPiece tokens).",
        "",
        "## Sources",
        "",
        *[f"- {names[k]}, Exp {e}: `{p.relative_to(ROOT).as_posix()}`" for k, _, paths in [(m[0], m[1], m[2]) for m in MODELS] for e, p in paths.items()],
        "",
        f"Machine-readable copy of the master table: `evaluation/master_results.csv` and `evaluation/master_results.json`.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    runs = load_all()
    for fn in (fig_overall, fig_heatmap, fig_delta, fig_confusions, fig_curves, fig_params, fig_pooling):
        fn(runs)
    write_tables(runs)
    REPORT_PATH.write_text(build_report(runs), encoding="utf-8")
    print(f"Wrote {REPORT_PATH}, {CSV_PATH}, {JSON_PATH} and figures in {FIG_DIR}")


if __name__ == "__main__":
    main()
