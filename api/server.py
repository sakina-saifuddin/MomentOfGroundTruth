"""Prediction API for the presentation website.

Serves the same model as the Streamlit app (frozen BERT, mean pooling, trained linear head)
as JSON, so a static page on Netlify can call it live.

Run from the repository root::

    uvicorn api.server:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT))

from causes import CAUSES, LABELS  # noqa: E402
from explain import Classifier  # noqa: E402

EXAMPLE_ROWS = [438, 83, 72, 365, 130, 12, 434, 118]  # one test-split narrative per cause (same as the app)

app = FastAPI(title="Moment of GroundTruth API", docs_url=None, redoc_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])

model: Classifier | None = None
heavy = threading.Semaphore(1)  # SHAP re-scores the text hundreds of times: one at a time


@app.on_event("startup")
def _load() -> None:
    global model
    model = Classifier()
    model.predict("warm up")


class Narrative(BaseModel):
    text: str = Field(min_length=1, max_length=8000)


class ExplainReq(Narrative):
    evals: int = Field(default=150, ge=50, le=400)


@app.get("/api/health")
def health() -> dict:
    return {"ok": model is not None, "labels": LABELS}


@app.get("/api/examples")
def examples() -> list[dict]:
    df = pd.read_csv(ROOT / "data" / "experiment1" / "test.csv")
    return [{"name": f"Example {i + 1}", "text": df.loc[r, "narrative_clean"], "truth": df.loc[r, "CAUSE"]} for i, r in enumerate(EXAMPLE_ROWS)]


@app.post("/api/predict")
def predict(req: Narrative) -> dict:
    if model is None:
        raise HTTPException(503, "model still loading")
    cleaned, probs = model.predict(req.text)
    top = int(probs.argmax())
    return {
        "cleaned": cleaned,
        "labels": LABELS,
        "titles": [CAUSES[l]["title"] for l in LABELS],
        "probs": [round(float(p), 4) for p in probs],
        "top": top,
    }


@app.post("/api/explain")
def explain(req: ExplainReq) -> dict:
    if model is None:
        raise HTTPException(503, "model still loading")
    cleaned, probs = model.predict(req.text)
    top = int(probs.argmax())
    if not heavy.acquire(timeout=1):
        raise HTTPException(429, "another explanation is running, try again in a few seconds")
    try:
        pairs = model.explain(cleaned, top, max_evals=req.evals)
    finally:
        heavy.release()
    return {"top": top, "words": [[w, round(v, 4)] for w, v in pairs if w.strip()]}
