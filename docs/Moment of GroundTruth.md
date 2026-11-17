**EDS 6352**Natural Language Processing · Fall 2026 · Team 1

# Moment of GroundTruth

Classifying gas transmission and gathering pipeline incident causes using BiGRU, BiLSTM with attention, and BERT-base.

- **Sakina Saifuddin**Frozen BERT
- **Muhammad Murtaza**BiLSTM + attention
- **Parva Shah**BiGRU

Red rubber stamp reading Moment of GroundTruth, Root Cause Analysis

**Why it matters**NTSB investigations

## Pipelines fail where *nobody can see*

San Bruno, California · 2010

8deaths

58injured

38homes destroyed

Defective seam weld and a pressure increase before the rupture.

Carlsbad, New Mexico · 2000

12deaths

Severe internal corrosion.

Operators file a written report within **30 days**. The cause is somewhere in the text.

Corrosion pit in the wall of a buried steel gas pipeline, before and after blasting

Corrosion pit in a buried gas pipeline. Illustration only, not either incident above. Photo: Cafe Nervosa / D. Mawhinney, CC BY-SA 3.0, Wikimedia Commons.

**The data**PHMSA gas transmission and gathering incidents

## 3,044 reports, *eight* possible causes

3,044narratives, all usable

136median words

2001–2026report years

Source: U.S. DOT, PHMSA, Form F 7100.2. The 2010–present file has 623 fields; we kept six. The 2002–2009 historical file is merged in and older cause labels are mapped to today's eight. The model reads the narrative only.

Proposal draft: 3,027 · Final file: 3,044

**The labels**Drag, click a card, or use the arrows

## Each cause, in the *operators' own words*

1 / 8

**Experiment design**Same split for every model

## One split. *Two ways* to handle imbalance.

**2,130**train 70%

**456**val

**458**test

Stratified, seed 42. Validation and test sets are identical in both experiments.

Cleaning comes first: extra whitespace and HTML artifacts removed, all text lowercased.

BiGRU + FastText BiLSTM + attention + FastText Frozen BERT-base

Training rows per cause

**Model 1**BiGRU + FastText

## Reads the narrative *both directions*

Embeddings

FastText, 300-d, frozen

Recurrent

2 layers · 128 hidden per direction

Training

Adam · lr 1e-3 · batch 32 · dropout 0.3

Stopping

patience 5 · grad clip 5 · seed 42

Input

up to 300 tokens

Oversampling lifted accuracy **7.6 points** but macro-F1 by only **0.007**. Incorrect-operation recall fell from **0.32 to 0.12**.

**Model 2**BiLSTM + attention + FastText

## Learns *which words* carry the cause

Embeddings

FastText, 300-d, frozen

Recurrent

2 layers · 128 hidden per direction

Trainable

903,688 weights

Training

Adam · lr 1e-3 · batch 32 · dropout 0.3

Same setup as BiGRU

fair RNN comparison

Best RNN. Highest corrosion F1 of any run: **0.729**, with **0.805** precision. Oversampling cost it **0.067** macro-F1.

**Model 3**bert-base-uncased, frozen

## Keep BERT frozen. *Train one small head.*

Narrative, up to **512** tokens

**12 layers**, 12 heads, 768-d. All weights frozen.

One 768-number vector per narrative

Linear head 768 → 8. **6,152** trainable weights, against 903,688 in the BiLSTM.

Training

AdamW · lr 2e-3 · batch 16

Stopping

patience 5 on val macro-F1

DRAG TO ROTATE · HOVER A LAYER

**Model 3**Class-weighted loss, test set

## One design choice moved macro-F1 by *0.25*

0.553macro-F1

60.3%accuracy

Same frozen BERT, same head, same data. Only the step that builds the narrative vector differs: one \[CLS\] token, or the average of every token.

Per-cause F1 | marks the other method

**Results**458 held-out test narratives

## A close race: top three within *0.022*

Exp 1 · class weights\
Exp 2 · oversampling

Macro-F1 gives each of the 8 causes equal weight. Micro-F1 equals accuracy in single-label classification, so we report accuracy.

Highest validation macro-F1 was BiGRU Exp 2 (0.586). The test ranking differs, so treat the top runs as close.

DRAG TO ROTATE

**Per-cause results**Test F1 · click a row for precision and recall

## Easy causes are *easy*. Vague ones are not.

**Errors**Each row sums to 100% of that true cause

## Where the models *confuse* causes

Predicted cause →

Hover a cell for the count behind it.

**Live demo**Streamlit app · frozen BERT, mean pooling

## From pasted narrative to *stamped cause*

1. Paste a narrative, or pick one of eight real test reportsTitle: Moment-of-GroundTruth
2. Predicted cause, confidence, and a bar for each of the 8 causes
3. A photo of that cause, and SHAP shading on the words that pushed the answerPrediction about 0.1 s · SHAP 15 to 40 s

streamlit run app/app.py

Hosting plan from the proposal: Oracle Cloud Infrastructure; VM setup is in the repository. App head retrained locally: 57.9% accuracy, 0.522 macro-F1 (Colab run: 0.553).

**Drop an app screenshot here**\
or click to choose one

**Summary**Team 1

## Every incident has a moment of *truth*

Thank you. Questions?

Data: U.S. DOT PHMSA public incident reports. Photos: Wikimedia Commons (CC BY-SA 2.0 to 4.0) and NTSB (public domain); per-photo credits are on the cause cards and in the project repository.

0.553best test macro-F1 · frozen BERT, mean pooling

60.3%test accuracy, same run

+0.25macro-F1 from mean pooling over \[CLS\]

0:00TARGET 12:00 · LIMIT 13:00