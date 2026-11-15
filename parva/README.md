# Parva workspace

Keep Parva's project work in this folder. Use the `parva` branch for changes and open a pull request to `main` when ready.

## BiGRU + FastText (Exp 1 class-weighted, Exp 2 oversampling)

Run from the repository root. All hyperparameters are in `parva/bigru/bigru_config.py`
(matched to Muhammad's BiLSTM config). Exp 1 reads `data/experiment1/`, Exp 2 reads `data/experiment2/`.

```bash
python -m pip install -r parva/requirements.txt
parva/.venv/bin/python parva/bigru/bigru_train_exp1.py    # class-weighted loss
parva/.venv/bin/python parva/bigru/bigru_train_exp2.py    # plain loss + synthetic data
# optional wiring check (random embeddings, 1 epoch, *_smoke files):
parva/.venv/bin/python parva/bigru/bigru_train_exp1.py --smoke-test
```

Outputs in `parva/bigru/`: `bigru_best_exp{1,2}.pt`, `bigru_exp{1,2}_results.json`,
`bigru_exp{1,2}_confusion_matrix.png`. FastText model: `parva/cache/model.bin`
(`facebook/fasttext-en-vectors` on Hugging Face); embedding matrices are cached per experiment in `parva/cache/`.
