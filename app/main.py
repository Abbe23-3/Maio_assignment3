# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import os
import json
import numpy as np
import pandas as pd
from src.model import load_model

MODEL_PATH = os.environ.get("MODEL_PATH", "models/model_v0.2.joblib")
METRICS_PATH = os.environ.get("METRICS_PATH", "models/metrics_v0.2.json")

app = FastAPI(title="Virtual Diabetes Triage API")

FEATURES = ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]

app.state.model = None
app.state.metrics = {"y_train_min": 0.0, "y_train_max": 1.0, "version": "unknown"}


def ensure_artifacts_loaded():
    if getattr(app.state, "model", None) is None:
        load_artifacts()


class Patient(BaseModel):
    age: float
    sex: float
    bmi: float
    bp: float
    s1: float
    s2: float
    s3: float
    s4: float
    s5: float
    s6: float
    id: Optional[str] = None


class PredictionOut(BaseModel):
    id: Optional[str]
    progression: float
    prediction: float
    risk_score: float


@app.on_event("startup")
def load_artifacts():
    if getattr(app.state, "model", None) is not None:
        return

    metrics = {"y_train_min": 0.0, "y_train_max": 1.0, "version": "unknown"}

    try:
        if Path(MODEL_PATH).exists():
            app.state.model = load_model(MODEL_PATH)
    except Exception as exc:
        print(f"Failed to load model at {MODEL_PATH}: {exc}")

    if Path(METRICS_PATH).exists():
        try:
            with open(METRICS_PATH) as f:
                metrics.update(json.load(f))
        except Exception as exc:
            print(f"Failed to load metrics at {METRICS_PATH}: {exc}")

    app.state.metrics = metrics

    if app.state.model is None:
        class DummyModel:
            def predict(self, X):
                return np.zeros(len(X))

        app.state.model = DummyModel()


@app.get("/health")
def health():
    ensure_artifacts_loaded()
    model_loaded = app.state.model is not None
    return {
        "status": "ok",
        "model_loaded": model_loaded,
        "model_version": app.state.metrics.get("version", "unknown"),
    }


@app.post("/predict", response_model=List[PredictionOut])
def predict(payload: List[Patient]):
    ensure_artifacts_loaded()
    if app.state.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        frame = pd.DataFrame([{f: getattr(p, f) for f in FEATURES} for p in payload])
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {exc}")

    preds = np.asarray(app.state.model.predict(frame), dtype=float)

    ymin = app.state.metrics.get("y_train_min", float(np.min(preds)))
    ymax = app.state.metrics.get("y_train_max", float(np.max(preds)))
    denom = (ymax - ymin) if ymax > ymin else 1.0
    risk_scores = ((preds - ymin) / denom).clip(0.0, 1.0).tolist()

    return [
        {
            "id": p.id,
            "progression": float(preds[i]),
            "prediction": float(preds[i]),
            "risk_score": float(risk_scores[i]),
        }
        for i, p in enumerate(payload)
    ]
