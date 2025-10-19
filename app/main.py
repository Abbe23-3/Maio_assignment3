# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import os
import json
import numpy as np
from src.model import load_model

MODEL_PATH = os.environ.get("MODEL_PATH", "models/model_v0.2.joblib")
METRICS_PATH = os.environ.get("METRICS_PATH", "models/metrics_v0.2.json")

app = FastAPI(title="Virtual Diabetes Triage API")

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
    app.state.model = None
    app.state.metrics = {"y_train_min": 0.0, "y_train_max": 1.0}

    if Path(MODEL_PATH).exists():
        app.state.model = load_model(MODEL_PATH)
    if Path(METRICS_PATH).exists():
        try:
            with open(METRICS_PATH) as f:
                app.state.metrics = json.load(f)
        except Exception:
            pass


@app.get("/health")
def health():
    """Check API health and that model is loaded"""
    model_loaded = app.state.model is not None
    return {"status": "ok", "model_loaded": model_loaded}


@app.post("/predict", response_model=List[PredictionOut])
def predict(payload: List[Patient]):
    if app.state.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        X = np.array([[getattr(p, f) for f in FEATURES] for p in payload])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")

    model = app.state.model
    preds = model.predict(X)

    ymin = app.state.metrics.get("y_train_min", float(np.min(preds)))
    ymax = app.state.metrics.get("y_train_max", float(np.max(preds)))
    denom = (ymax - ymin) if ymax > ymin else 1.0
    risk_scores = ((preds - ymin) / denom).tolist()

    return [
        {
            "id": p.id,
            "progression": float(preds[i]),
            "risk_score": float(max(0.0, min(1.0, risk_scores[i]))),
        }
        for i, p in enumerate(payload)
    ]
