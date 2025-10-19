# Project Architecture

This service delivers diabetes progression predictions through a containerised FastAPI application backed by scikit-learn models.

```
┌───────────────────────────── Training ─────────────────────────────┐
│   sklearn.load_diabetes() → split → Pipeline (Scaler + Model)      │
│        │                                                           │
│        └─> src/train.py saves model_*.joblib + metrics_*.json ──┐   │
└────────────────────────────────────────────────────────────────┘   │
                                                                     ▼
┌────────────────────────────── Serving ─────────────────────────────┐
│ FastAPI (app/main.py)                                              │
│  • /health → returns status, model_loaded and model_version        │
│  • /predict → validates payload, builds DataFrame, runs model      │
│    → returns progression + normalised risk_score                   │
│                                                                     │
│ Artifacts loaded on startup (or lazily) via src.model.load_model    │
└────────────────────────────────────────────────────────────────────┘
```

## Directory Overview

- `app/` – FastAPI application and request/response schemas.
- `src/` – Training pipeline (`train.py`) and persistence helpers (`model.py`).
- `models/` – Versioned artifacts created by the training script.
- `tests/` – Pytest suite covering API and training behaviour.
- `docs/` – Documentation bundle (architecture, pipeline guide, quick start, org tips).
- `Dockerfile` – Builds a self-contained image with the default v0.2 model baked in.
- `.github/workflows/` – CI (push/PR) and Release (tag) automation.

## Data Flow

1. **Training** (`python -m src.train`):
   - Loads the open diabetes dataset.
   - Splits into train/test using deterministic seeds.
  - Fits one of `linear`, `ridge` (via RidgeCV), or `rf` (parallel RandomForest).
   - Saves the fitted pipeline to `models/model_<version>.joblib`.
   - Writes metadata (`rmse`, `y_train_min/max`, etc.) to `models/metrics_<version>.json`.

2. **Serving** (`uvicorn app.main:app` or Docker image):
   - Loads artifacts defined by `MODEL_PATH`/`METRICS_PATH` env vars.
   - Falls back to a deterministic zero-output dummy if artifacts are missing (useful in tests).
   - `/predict` converts validated payloads into a Pandas DataFrame, runs the pipeline and computes a risk score between 0 and 1 using stored min/max.

3. **Deployment**:
   - CI ensures training/tests/Docker build smoke tests pass on every push.
   - Release workflow (triggered via `git tag v*`) retrains the chosen model, builds & pushes a versioned GHCR image, smoke tests the container, and publishes a GitHub Release with artifacts + metrics.
