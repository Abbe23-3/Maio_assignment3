# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import os
import json
from src.model import load_model
import numpy as np

MODEL_PATH = os.environ.get("MODEL_PATH", "models/model_v0.2.joblib")
METRICS_PATH = os.environ.get("METRICS_PATH", "models/metrics_v0.2.json")

app = FastAPI(title="Virtual Diabetes Triage API")

# dataset feature names
FEATURES = ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]


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
    risk_score: float


@app.on_event("startup")
def load_artifacts():
    if not Path(MODEL_PATH).exists():
        raise RuntimeError(f"Model not found at {MODEL_PATH}")
    app.state.model = load_model(MODEL_PATH)
    if Path(METRICS_PATH).exists():
        with open(METRICS_PATH) as f:
            app.state.metrics = json.load(f)
    else:
        app.state.metrics = {"y_train_min": 0.0, "y_train_max": 1.0}


@app.post("/predict", response_model=List[PredictionOut])
def predict(payload: List[Patient]):
    try:
        X = np.array([[getattr(p, f) for f in FEATURES] for p in payload])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")

    model = app.state.model
    preds = model.predict(X)
    # normalize to [0,1] using training min/max (for risk score)
    ymin = app.state.metrics.get("y_train_min", float(np.min(preds)))
    ymax = app.state.metrics.get("y_train_max", float(np.max(preds)))
    denom = (ymax - ymin) if ymax > ymin else 1.0
    risk_scores = ((preds - ymin) / denom).tolist()
    out = []
    for i, p in enumerate(payload):
        out.append(
            {
                "id": p.id,
                "progression": float(preds[i]),
                "risk_score": float(max(0.0, min(1.0, risk_scores[i]))),
            }
        )
    return out


@app.get("/health")
def health():
    return {"status": "ok"}
