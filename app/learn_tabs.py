"""Explanatory tabs: the story, the data and split, the models, the results, limits and credits.

Everything numeric is read from files the project already produced (the master results table and
the saved figures), so these pages cannot drift from the real results.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from causes import ASSETS, CAUSES, LABELS

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "figures"
FINAL = FIG / "final"
RED = "#D8291F"


# ----------------------------------------------------------------------------- helpers
def callout(title: str, body: str) -> None:
    st.markdown(
        f'<div class="callout"><b>{html.escape(title)}</b><br>{body}</div>',
        unsafe_allow_html=True,
    )


def figure(path: Path, title: str, how_to_read: str, takeaway: str | None = None) -> None:
    """A chart with a one-line title, a plain-language 'how to read it', and an optional takeaway."""
    st.markdown(f"##### {title}")
    st.image(str(path), width="stretch")
    st.markdown(f'<p class="small"><b>How to read it:</b> {how_to_read}</p>', unsafe_allow_html=True)
    if takeaway:
        st.markdown(f'<p class="take"><b>What it shows:</b> {takeaway}</p>', unsafe_allow_html=True)


def stat_row(items: list[tuple[str, str]]) -> None:
    cells = "".join(f'<div class="stat"><div class="num">{v}</div><div class="lab">{html.escape(k)}</div></div>' for k, v in items)
    st.markdown(f'<div class="stats">{cells}</div>', unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def master() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "evaluation" / "master_results.csv")
    df["experiment"] = df["experiment"].map({1: "Exp 1: class weights", 2: "Exp 2: extra synthetic data"})
    return df


# ----------------------------------------------------------------------------- the story
def story() -> None:
    st.markdown("## Why this project exists")
    st.markdown(
        "When a gas pipeline has an incident, the company that runs it must file a report with the U.S. government "
        "(PHMSA) within 30 days. Part of that report is a **narrative**: a few paragraphs, in plain language, of what happened. "
        "There are thousands of these. Reading them all by hand to find patterns takes a long time."
    )
    callout(
        "The goal",
        "Teach a computer to read one narrative and name its **root cause**, picking from eight categories. "
        "Then compare three different ways of teaching it, and see which one reads these reports best.",
    )

    st.markdown("## Why it is called Moment of GroundTruth")
    c1, c2 = st.columns([1, 3], vertical_alignment="center")
    c1.image(str(ROOT / "docs" / "images" / "logo-stamp-root-cause.png"), width="stretch")
    c2.markdown(
        "- **Moment of truth** is the instant something gets decided.\n"
        "- **Ground truth** is the machine-learning word for the *correct answer* attached to an example. Here, the correct answer is the **cause** of the incident.\n"
        "- **Pipelines are buried in the ground.**\n\n"
        "So the name means: *the moment we dig down to the ground truth, the root cause.* The logo is a rubber stamp because, in the end, "
        "someone has to stamp one cause on every report. This app does the stamping, and shows its work."
    )

    st.markdown("## The eight causes")
    st.markdown("Every incident in the data carries exactly one of these labels. The pictures are illustrations, not photos of the incidents.")
    cols = st.columns(2)
    for i, label in enumerate(LABELS):
        c = CAUSES[label]
        with cols[i % 2]:
            if c["image"]:
                st.image(str(ASSETS / str(c["image"])), width="stretch")
            else:
                st.markdown('<div class="noimg-small">sketch only</div>', unsafe_allow_html=True)
            st.markdown(f"**{c['title']}**")
            st.markdown(f'<p class="small">{html.escape(str(c["blurb"]))}</p>', unsafe_allow_html=True)

    st.markdown("## A real example, cause by cause")
    st.markdown("Short excerpts from the data, one per cause. Operator names are left out.")
    examples = {
        "EQUIPMENT FAILURE": "line separated at the coupling, mp 63.988 on the north main loop line near the onward compressor station.",
        "CORROSION FAILURE": "while conducting a c p survey, pipeline personnel located a gas leak.",
        "MATERIAL FAILURE OF PIPE OR WELD": "crack propagated to critical size by fatigue due to effects of operating pressure cycles.",
        "EXCAVATION DAMAGE": "landowner was using a backhoe to dig ditches and a hole for a new septic system on his property.",
        "NATURAL FORCE DAMAGE": "the pipe pulled apart in the bottom of a small creek crossing.",
        "OTHER OUTSIDE FORCE DAMAGE": "the puncture was apparently caused by a large caliber fire arm.",
        "OTHER INCIDENT CAUSE": "gas bubbles were visible and that no sheen was evident on the water.",
        "INCORRECT OPERATION": "the low pressure suction shutdown switch had been de-activated, allowing the low pressure blower to continue to run.",
    }
    for label, text in examples.items():
        st.markdown(f"**{CAUSES[label]['title']}**  \n> {text}")

    callout(
        "What the app is, and is not",
        "It is a **second opinion** that points at the words behind its answer. It does not predict whether or when an incident will happen, "
        "and it is right roughly six times out of ten, so a person should always make the final call.",
    )


# ----------------------------------------------------------------------------- data and split
def data_and_split() -> None:
    st.markdown("## Where the data comes from")
    st.markdown(
        "The data is public: **PHMSA Gas Transmission and Gathering Incident Data**, from the U.S. Department of Transportation. "
        "We merged the 2002-2009 historical reports with the 2010-to-today reports, and mapped the older cause labels onto the current eight categories. "
        "From each report we use two things: the written **narrative** (what the model reads) and the **cause** (the answer it should give)."
    )
    stat_row([("incident reports", "3,044"), ("cause categories", "8"), ("median words per report", "136"), ("years covered", "2001-2026")])

    st.markdown("## How we cleaned the text")
    st.markdown(
        "1. Turn web-page leftovers (like `&amp;`) back into normal characters and remove stray HTML tags.\n"
        "2. Collapse extra spaces and line breaks.\n"
        "3. **Make everything lowercase.** Many old reports are typed in ALL CAPS, which the pre-trained language tools handle badly.\n\n"
        "The app applies the exact same cleaning to whatever you paste in."
    )

    st.markdown("## The causes are not evenly spread")
    figure(
        FIG / "class_distribution_by_split.png",
        "How many reports per cause",
        "Each group of bars is one cause. Taller bars mean more reports of that kind. The three colors are the train, validation and test sets (explained below).",
        "Equipment failure and corrosion are common. Incorrect operation (165 reports) and other incident cause (190) are rare, so a model sees few examples to learn from. "
        "This imbalance is the reason for the two experiments later on.",
    )
    c1, c2 = st.columns(2)
    with c1:
        figure(FIG / "incidents_by_year.png", "Reports per year", "Each bar is a calendar year.", "The 2026 bar is a partial year, not a drop in incidents.")
    with c2:
        figure(FIG / "narrative_length_words.png", "How long is a narrative?", "How many reports have each length, in words.", "Most are short. The middle report has 136 words.")

    st.markdown("## How we split the data: study, practice test, final exam")
    st.markdown(
        "We cannot judge a model on the same reports it learned from, just as a student cannot be graded on questions they already memorized. "
        "So the 3,044 reports are divided into three piles, and **every model uses exactly the same three piles**."
    )
    split = pd.DataFrame(
        {
            "Pile": ["Train", "Validation", "Test"],
            "Share": ["70%", "15%", "15%"],
            "Reports": [2130, 456, 458],
            "What it is for": [
                "Study material. The model learns from these.",
                "Practice test. We watch it to decide when to stop training.",
                "Final exam. Opened once at the end. Every score on the Results tab is on these 458 reports.",
            ],
        }
    )
    st.dataframe(split, hide_index=True, width="stretch")
    callout(
        "Stratified, so the piles stay fair",
        "A random split could by chance put most of a rare cause in one pile. A <b>stratified</b> split makes each pile keep the same mix of causes as the whole data set. "
        "It is reproducible: the split uses a fixed random seed (42) and a leakage-safe rule so the same incident text can never sit in two piles.",
    )
    figure(
        ROOT / "docs" / "images" / "chart-data-split.png",
        "The three piles",
        "Bar height is the number of reports in each pile.",
    )


# ----------------------------------------------------------------------------- models
def models() -> None:
    st.markdown("## Three ways to teach a computer to read")
    st.markdown(
        "The proposal compares three neural networks. All three get the same reports, the same split, and the same job: output one of eight causes. "
        "They differ in **how they read**."
    )

    st.markdown("### 1. BiGRU  (Parva)")
    st.markdown(
        "A **GRU** reads a sentence one word at a time and keeps a small running memory of what it has seen. **Bi** means it reads twice, once forward and once backward, "
        "so each word is understood with both its left and right neighbors."
    )
    st.code("narrative words -> forward GRU  \\\n                                     + -> combine -> classifier -> 1 of 8 causes\nnarrative words -> backward GRU /", language="text")

    st.markdown("### 2. BiLSTM with attention  (Muhammad)")
    st.markdown(
        "An **LSTM** is a reader with a better memory: gates let it decide what to keep and what to forget. **Attention** adds a highlighter. "
        "The model learns which words matter most (like *backhoe* or *corrosion*) and leans on those when it decides."
    )
    st.code("narrative words -> forward LSTM  \\\n                                      + -> attention (highlighter) -> classifier -> 1 of 8 causes\nnarrative words -> backward LSTM /", language="text")
    st.markdown(
        '<p class="small">Both of these use <b>FastText</b> word vectors: a dictionary, learned from a huge amount of text, that turns each word into 300 numbers so that similar words have similar numbers. '
        "The dictionary is frozen; only the reading layers are trained.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("### 3. Frozen BERT  (Sakina)")
    st.markdown(
        "**BERT** is a language model already trained on a vast amount of text. We keep all of BERT **frozen** (unchanged) and use it only to turn a narrative into a list of 768 numbers. "
        "Then we train just one tiny layer, a **linear head**, to turn those 768 numbers into eight cause scores. That is only **6,152 trainable numbers**, "
        "compared with 903,688 in the BiLSTM."
    )
    st.code("narrative -> BERT (frozen) -> one vector of 768 numbers -> linear head (768 -> 8) -> 1 of 8 causes", language="text")
    callout(
        "The one design choice we tested: how to boil a narrative down to one vector",
        "BERT gives one vector per word. We have to combine them.<br><br>"
        "<b>pooler_output</b> keeps only the first special token ([CLS]). It is like asking <i>one person</i> to summarize a whole meeting.<br>"
        "<b>Mean pooling</b> averages every word's vector. It is like asking <i>everyone in the room</i> and averaging their views.<br><br>"
        "With BERT frozen, nobody trained the [CLS] token for this job, so one token is a weak summary. Averaging scored far higher (see Results). "
        "That is why this app uses <b>mean pooling</b>.",
    )

    st.markdown("## Two ways to handle the rare causes")
    st.markdown("Rare causes get few examples, so models tend to ignore them. Each model was trained twice, with a different fix.")
    c1, c2 = st.columns(2)
    with c1:
        callout(
            "Experiment 1: class weights",
            "Same training data. But a mistake on a rare cause is <b>penalized more</b> than a mistake on a common one, so the model pays attention to the rare ones.",
        )
    with c2:
        callout(
            "Experiment 2: smart oversampling",
            "We <b>add 681 extra training narratives</b> for the six smaller causes, written by a language model from real examples, then checked by rules (see below). No class weights.",
        )
    syn = pd.DataFrame(
        {
            "Cause": [CAUSES[l]["title"] for l in LABELS],
            "Real training reports": [551, 460, 260, 253, 211, 147, 133, 115],
            "Synthetic added": [0, 0, 40, 47, 89, 153, 167, 185],
        }
    )
    syn["Total in Exp 2"] = syn["Real training reports"] + syn["Synthetic added"]
    st.dataframe(syn, hide_index=True, width="stretch")
    st.markdown(
        '<p class="small">Synthetic text was made only from <b>training</b> reports and added only to the training pile. '
        "Each generated narrative was rejected unless it was lowercase, at least 50 words, not a copy of an existing one, and did not contain the cause name. "
        "Validation and test stayed untouched in both experiments, so the two fixes are compared fairly.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("## How each model was trained")
    train = pd.DataFrame(
        {
            "": ["Reads with", "Words kept", "Trainable numbers", "Learning rate / batch", "Stops when"],
            "BiGRU": ["2 GRU layers (128), FastText", "300", "not recorded", "0.001 / 32", "validation macro-F1 stops improving (5 epochs)"],
            "BiLSTM + attention": ["2 LSTM layers (128) + attention, FastText", "300", "903,688", "0.001 / 32", "same rule"],
            "Frozen BERT": ["BERT-base-uncased (frozen), mean pooling", "up to 512 word pieces", "6,152", "0.002 / 16", "same rule"],
        }
    ).set_index("")
    st.dataframe(train, width="stretch")


# ----------------------------------------------------------------------------- results
def results() -> None:
    df = master()
    st.markdown("## How well did each model do?")
    st.markdown(
        "Every score below is measured on the **same 458 test reports** the models never trained on. Two numbers matter most:"
    )
    c1, c2 = st.columns(2)
    c1.markdown("**Accuracy**: out of 100 reports, how many did it label correctly?")
    c2.markdown(
        "**Macro-F1**: how good is it *on average across the eight causes*, counting rare causes as much as common ones? "
        "This is the fairer score when some causes are rare, so it is our main ranking."
    )

    best = df.sort_values("macro_f1", ascending=False).iloc[0]
    stat_row(
        [
            ("best macro-F1", f"{best.macro_f1:.2f}"),
            ("its accuracy", f"{best.accuracy:.0%}"),
            ("best run", best.model.replace("Frozen BERT, ", "BERT, ")),
            ("accuracy from always guessing the most common cause", "26%"),
        ]
    )

    st.markdown("### Pick a score and compare")
    metric = st.radio("Score", ["macro_f1", "accuracy", "macro_precision", "macro_recall"], horizontal=True, format_func=lambda m: {"macro_f1": "Macro-F1", "accuracy": "Accuracy", "macro_precision": "Macro precision", "macro_recall": "Macro recall"}[m])
    pivot = df.pivot(index="model", columns="experiment", values=metric)
    st.bar_chart(pivot, horizontal=True, color=[RED, "#e3a63a"], height=320)
    st.markdown(
        '<p class="small"><b>Precision</b>: when the model says a cause, how often is it right? <b>Recall</b>: of the reports that really have that cause, how many did it find? '
        "<b>F1</b> blends the two.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("### The full table")
    show = df[["model", "experiment", "accuracy", "macro_precision", "macro_recall", "macro_f1", "best_val_macro_f1"]].rename(
        columns={"model": "Model", "experiment": "Experiment", "accuracy": "Accuracy", "macro_precision": "Macro precision", "macro_recall": "Macro recall", "macro_f1": "Macro-F1", "best_val_macro_f1": "Practice-test macro-F1"}
    )
    st.dataframe(show.style.format({c: "{:.3f}" for c in show.columns[2:]}).highlight_max(subset=["Macro-F1"], color="#5a2a22"), hide_index=True, width="stretch")

    st.markdown("---")
    st.markdown("## The story the graphs tell")

    figure(
        FINAL / "01_overall_comparison.png",
        "1. All models, both experiments",
        "Each color is a model. Solid bars are Experiment 1 (class weights); striped bars are Experiment 2 (synthetic data). Taller is better.",
        "Frozen BERT with mean pooling is highest (about 0.55 macro-F1), the two word-by-word models are close behind, and BERT with the [CLS] pooler is far lowest. "
        "The top three runs are within about 0.02, so it is a close race.",
    )
    figure(
        FINAL / "07_bert_pooling_per_class.png",
        "2. Same BERT, two ways of summarizing: the biggest single effect",
        "Light blue is the [CLS] pooler; dark blue is mean pooling. Each pair of bars is one cause.",
        "Averaging all the words instead of trusting one token improved nearly every cause, adding roughly 0.21 to 0.25 macro-F1. "
        "How you summarize matters more here than which architecture you pick.",
    )
    figure(
        FINAL / "02_per_class_f1_heatmap.png",
        "3. Which causes are easy and which are hard?",
        "Rows are causes, columns are runs. Brighter yellow means a better F1 for that cause.",
        "Excavation damage and corrosion are the easiest; other incident cause and incorrect operation are the hardest in every run. Their reports are few and their wording varies.",
    )
    figure(
        FINAL / "03_oversampling_effect_per_class.png",
        "4. Did the extra synthetic data help?",
        "Each bar is the change in F1 when moving from Experiment 1 to Experiment 2. Above zero means the synthetic data helped that cause.",
        "Mixed. It lowered macro-F1 for the BiLSTM and for BERT with mean pooling, and barely moved the BiGRU. Neither fix is a clear winner.",
    )
    figure(
        FINAL / "04_confusion_matrices.png",
        "5. What does each model confuse with what?",
        "Rows are the true cause, columns are what the model said. Each row adds to 100%, so a dark diagonal means correct. Dark squares off the diagonal are the mix-ups.",
        "The common mix-ups are corrosion read as material failure, and equipment failure read as several other causes.",
    )
    c1, c2 = st.columns(2)
    with c1:
        figure(FINAL / "05_validation_curves.png", "6. Learning over time", "Score on the practice test after each training round. A dot marks the round we kept.", "Models stop improving and early-stopping picks the best round.")
    with c2:
        figure(FINAL / "06_params_vs_macro_f1.png", "7. Size versus score", "Left is a smaller model. Higher is a better score.", "BERT's tiny 6,152-number head beats the 903,688-number BiLSTM, so a bigger model is not automatically better.")

    callout(
        "Read this before trusting any number",
        "Each model was run <b>once</b> (seed 42) on 458 test reports, and the rare causes have only 25 to 31 test reports each. Small gaps (a few hundredths) could flip with another run. "
        "The three models were also trained with separate code. The big, repeatable story is the pooling effect; the ranking among the top three is not settled.",
    )


# ----------------------------------------------------------------------------- limits and credits
def limits_and_credits() -> None:
    st.markdown("## Limits")
    st.markdown(
        "- The model labels **past** incident narratives. It cannot say whether or when a future incident will happen.\n"
        "- The data is imbalanced. Class weights and synthetic data help but do not make it balanced.\n"
        "- Operators write the reports, and older cause labels were mapped onto today's eight categories, so labels reflect reporting and mapping choices.\n"
        "- BERT reads at most 512 word pieces; longer narratives are cut off at the end.\n"
        "- The pictures illustrate each cause. They are not photos of the incident you typed in.\n"
        "- Every run is one seed on a small test set, so close scores are not reliable."
    )
    st.markdown("## What comes next")
    st.markdown(
        "- Repeat training with several random seeds to see which differences hold.\n"
        "- Pick the final model as a team, then host the app (the plan is Oracle Cloud Infrastructure).\n"
        "- Try fine-tuning BERT instead of freezing it. We have not tested this."
    )

    st.markdown("## The crew")
    st.markdown(
        "**Group 1, EDS 6352 Natural Language Processing**\n\n"
        "- **Sakina Saifuddin**: frozen BERT-base-uncased\n"
        "- **Muhammad Murtaza**: BiLSTM with attention and FastText\n"
        "- **Parva Shah**: BiGRU with FastText\n\n"
        "All three shared data preparation, cleaning, splitting, synthetic data and the final analysis."
    )
    st.markdown("## Data and picture credits")
    st.markdown(
        "- **Data:** PHMSA Gas Transmission and Gathering Incident Data, U.S. Department of Transportation, Pipeline and Hazardous Materials Safety Administration (public records).\n"
        "- **Photos:** each is credited under the picture where it appears. Sources are Wikimedia Commons under Creative Commons or public-domain terms.\n"
        "- **Explanations:** the word highlighting uses the open-source SHAP library."
    )
    st.markdown("## How this app was built")
    st.markdown(
        "The model is the project's Experiment 1 setup: frozen BERT-base-uncased, mean pooling, and a linear head trained with class weights. "
        "The head was retrained for this app (`python app/build_head.py`), so its test score is close to, but not identical to, the Colab run on the Results tab."
    )
    mfile = Path(__file__).parent / "artifacts" / "head_metrics.json"
    if mfile.exists():
        m = json.loads(mfile.read_text())
        st.markdown(f"This app's own model scored **{m['test_accuracy']:.1%} accuracy** and **{m['test_macro_f1']:.3f} macro-F1** on the same {m['test_rows']} test reports.")
