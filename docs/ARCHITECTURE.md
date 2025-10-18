# Project Architecture

## System Overview

This is a **Machine Learning API service** for diabetes progression prediction, packaged as a containerized microservice with automated CI/CD.

```
┌─────────────────────────────────────────────────────────────────┐
│                     DIABETES TRIAGE SYSTEM                      │
│                                                                 │
│  Training Phase                    Serving Phase                │
│  ───────────────                   ─────────────                │
│                                                                 │
│  ┌──────────────┐                 ┌──────────────┐            │
│  │ Diabetes     │                 │   FastAPI    │            │
│  │ Dataset      │                 │   Server     │            │
│  │ (sklearn)    │                 │              │            │
│  └──────┬───────┘                 │  /health     │            │
│         │                         │  /predict    │            │
│         ▼                         └───────┬──────┘            │
│  ┌──────────────┐                        │                    │
│  │ Feature      │                        │                    │
│  │ Engineering  │                        ▼                    │
│  │ (Scaler)     │                 ┌──────────────┐            │
│  └──────┬───────┘                 │ Load Model   │            │
│         │                         │ (joblib)     │            │
│         ▼                         └───────┬──────┘            │
│  ┌──────────────┐                        │                    │
│  │ ML Algorithm │                        ▼                    │
│  │ Linear/Ridge │                 ┌──────────────┐            │
│  │ /RF          │                 │ Predict +    │            │
│  └──────┬───────┘                 │ Risk Score   │            │
│         │                         └───────┬──────┘            │
│         ▼                                 │                    │
│  ┌──────────────┐                        ▼                    │
│  │ Save Model   │                 ┌──────────────┐            │
│  │ (.joblib)    │                 │ JSON         │            │
│  │ + metrics    │                 │ Response     │            │
│  └──────────────┘                 └──────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
Maio_assignment3/
│
├── .github/                    # GitHub-specific configuration
│   └── workflows/              # CI/CD automation
│       ├── ci.yml              # Continuous Integration workflow
│       └── release.yml         # Release & deployment workflow
│
├── app/                        # FastAPI application code
│   ├── __init__.py             # Package marker
│   └── main.py                 # API endpoints (/health, /predict)
│
├── src/                        # Source code for ML training
│   ├── __init__.py             # Package marker
│   ├── model.py                # Model save/load utilities
│   └── train.py                # Training script (CLI)
│
├── tests/                      # Test suite
│   ├── __init__.py             # Package marker
│   ├── test_api.py             # API endpoint tests
│   └── test_train.py           # Training pipeline tests
│
├── models/                     # Trained models and metadata
│   ├── model_v0.1.joblib       # Linear regression model
│   ├── metrics_v0.1.json       # v0.1 performance metrics
│   ├── model_v0.2.joblib       # Ridge regression model
│   └── metrics_v0.2.json       # v0.2 performance metrics
│
├── docs/                       # Documentation (NEW - organized docs)
│   ├── ARCHITECTURE.md         # This file - system design
│   └── PIPELINE_GUIDE.md       # CI/CD pipeline explanation
│
├── Dockerfile                  # Container image definition
├── docker-compose.yml          # Multi-container orchestration
├── requirements.txt            # Python dependencies
├── README.md                   # Quick start guide
├── CHANGELOG.md                # Version history
└── .flake8                     # Code style configuration (if exists)
```

---

## Component Details

### 1. Training Pipeline (`src/`)

#### `src/train.py`
**Purpose**: Command-line tool to train ML models

**Key Functions**:
- `train_and_save()`: Main training logic
  - Loads sklearn diabetes dataset
  - Splits data (80/20 train/test)
  - Trains model (Linear, Ridge, or RF)
  - Evaluates with RMSE
  - Saves model + metadata

**CLI Arguments**:
```bash
--version       # Model version (e.g., v0.1, v0.2)
--model         # Algorithm: linear, ridge, or rf
--out_dir       # Output directory (default: models/)
--test_size     # Test split ratio (default: 0.2)
--random_state  # Reproducibility seed (default: 42)
```

**Outputs**:
- `models/model_<version>.joblib` - Serialized scikit-learn pipeline
- `models/metrics_<version>.json` - Metadata (RMSE, version, data stats)

**Example**:
```bash
python -m src.train --version v0.2 --model ridge --random_state 42
```

#### `src/model.py`
**Purpose**: Utility functions for model persistence

**Functions**:
- `save_model(pipe, path)` - Serialize pipeline to disk
- `load_model(path)` - Deserialize pipeline from disk

**Why separate file?**
- Reusable by both training and serving code
- Clear separation of concerns
- Easy to test independently

---

### 2. API Service (`app/`)

#### `app/main.py`
**Purpose**: FastAPI REST API for model inference

**Lifecycle Management**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load model once (not on every request)
    app.state.model = load_model(MODEL_PATH)
    app.state.metrics = json.load(METRICS_PATH)
    yield
    # Shutdown: cleanup (currently none needed)
```

**Endpoints**:

##### `GET /health`
- **Purpose**: Service health check
- **Response**: `{"status": "ok", "model_version": "v0.2"}`
- **Use case**: Load balancer health probes, monitoring

##### `POST /predict`
- **Purpose**: Batch prediction of disease progression
- **Input**: List of Patient objects (10 features each)
- **Processing**:
  1. Validate input with Pydantic
  2. Convert to DataFrame
  3. Run model.predict()
  4. Normalize to risk score [0, 1]
  5. Return progression + risk_score
- **Output**: List of predictions with risk scores

**Data Models** (Pydantic):
```python
class Patient(BaseModel):
    age, sex, bmi, bp: float      # Clinical features
    s1, s2, s3, s4, s5, s6: float  # Serum measurements
    id: Optional[str]              # Patient identifier

class PredictionOut(BaseModel):
    id: Optional[str]
    progression: float              # Raw model output
    risk_score: float              # Normalized [0,1]
```

**Environment Variables**:
- `MODEL_PATH`: Path to .joblib file (default: models/model_v0.2.joblib)
- `METRICS_PATH`: Path to metrics JSON (default: models/metrics_v0.2.json)

---

### 3. Testing (`tests/`)

#### `tests/test_api.py`
**Tests**:
- `/health` endpoint returns 200 OK
- `/predict` endpoint accepts valid input
- `/predict` validates patient data schema
- Response structure matches expected format
- Error handling (invalid inputs)

#### `tests/test_train.py`
**Tests**:
- Model training completes without errors
- Model files are created
- Metrics JSON is valid
- RMSE is reasonable
- Model can be loaded and used for prediction

**Running Tests**:
```bash
pytest                  # Run all tests
pytest -v               # Verbose output
pytest tests/test_api.py  # Run specific file
```

---

### 4. Containerization

#### `Dockerfile`
**Multi-stage build** (if optimized) or single-stage:

```dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY app/ /app/app/
COPY src/ /app/src/
COPY models/ /app/models/

WORKDIR /app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Key Features**:
- Slim base image (reduces size)
- Dependencies installed first (layer caching)
- Health check for container orchestration
- Non-root user (security - could be added)

#### `docker-compose.yml`
**Purpose**: Local development and testing

**Services**:
- `api`: Main service (v0.2 by default)
- `api-v0.1`: Optional v0.1 service (commented out)

**Features**:
- Health checks
- Auto-restart
- Network isolation
- Environment variable configuration

**Usage**:
```bash
docker-compose up -d        # Start in background
docker-compose logs -f api  # View logs
docker-compose down         # Stop and remove
```

---

### 5. CI/CD Workflows (`.github/workflows/`)

#### `ci.yml` - Continuous Integration
**Triggers**: Every push and pull request

**Jobs**:
1. **lint-test**:
   - Code quality (flake8)
   - Unit tests (pytest)

2. **train-upload-and-smoketest**:
   - Train baseline model
   - Build Docker image
   - Run container smoke tests
   - Upload model artifacts

**Why separate jobs?**
- Fail fast (lint errors caught early)
- Parallel execution (faster CI)
- Clear separation of concerns

#### `release.yml` - Release & Deployment
**Triggers**: Tag push (e.g., `git push origin v0.2`)

**Steps**:
1. Extract version from tag
2. Train version-specific model
3. Build Docker image
4. Push to GitHub Container Registry (GHCR)
5. Run smoke tests
6. Create GitHub Release
7. Upload artifacts

**Artifacts**:
- Docker image: `ghcr.io/<user>/<repo>:v0.2`
- Model files attached to GitHub Release
- CHANGELOG included in release notes

---

## Data Flow

### Training Flow
```
sklearn.datasets.load_diabetes()
         ↓
Split (80% train, 20% test)
         ↓
StandardScaler.fit_transform(X_train)
         ↓
Model.fit(X_train_scaled, y_train)
         ↓
Model.predict(X_test_scaled)
         ↓
Calculate RMSE
         ↓
joblib.dump(pipeline)  →  models/model_v0.2.joblib
json.dump(metrics)     →  models/metrics_v0.2.json
```

### Inference Flow
```
HTTP POST /predict
         ↓
Pydantic validation (Patient schema)
         ↓
Convert to DataFrame [n_patients × 10_features]
         ↓
pipeline.predict(X)  [loaded at startup]
         ↓
Normalize to risk_score = (pred - y_min) / (y_max - y_min)
         ↓
JSON response [{"id": "...", "progression": 154.3, "risk_score": 0.42}]
```

---

## Model Pipeline (scikit-learn)

Each saved model is a **Pipeline** object:

```python
Pipeline([
    ('scaler', StandardScaler()),    # Step 1: Normalize features
    ('model', LinearRegression())    # Step 2: Predict
])
```

**Why Pipeline?**
- Ensures scaling is applied during inference
- Prevents data leakage (scaler fitted only on train)
- Single object to save/load
- Cleaner code

**Model Versions**:
- **v0.1**: LinearRegression (no hyperparameters)
- **v0.2**: Ridge(alpha=X) where X is tuned via GridSearchCV
- **v0.3** (future): RandomForestRegressor with tuned parameters

---

## Environment Variables

### Development
```bash
export MODEL_PATH=models/model_v0.2.joblib
export METRICS_PATH=models/metrics_v0.2.json
```

### Docker
Set in `docker-compose.yml` or pass to `docker run`:
```bash
docker run -e MODEL_PATH=/app/models/model_v0.2.joblib \
           -e METRICS_PATH=/app/models/metrics_v0.2.json \
           -p 8080:8080 maio_assignment3
```

### Production (Kubernetes/Cloud)
ConfigMaps or environment injection:
```yaml
env:
  - name: MODEL_PATH
    value: /app/models/model_v0.2.joblib
```

---

## Scaling & Production Considerations

### Current State
- Single-threaded FastAPI (okay for low traffic)
- Model loaded once at startup (good)
- Synchronous predictions (blocking)

### Improvements for Production

#### 1. Horizontal Scaling
```yaml
# docker-compose.yml
services:
  api:
    deploy:
      replicas: 3  # Run 3 instances
```

Add load balancer (nginx, Traefik, etc.)

#### 2. Async Predictions
```python
# app/main.py
@app.post("/predict")
async def predict(payload: List[Patient]):
    # Run prediction in thread pool
    loop = asyncio.get_event_loop()
    predictions = await loop.run_in_executor(None, model.predict, X)
    ...
```

#### 3. Model Versioning
Support multiple models simultaneously:
```
GET /v1/predict  → model_v0.1
GET /v2/predict  → model_v0.2
```

#### 4. Monitoring
Add Prometheus metrics:
```python
from prometheus_client import Counter, Histogram

prediction_count = Counter('predictions_total', 'Total predictions')
prediction_latency = Histogram('prediction_seconds', 'Prediction latency')

@app.post("/predict")
def predict(...):
    prediction_count.inc()
    with prediction_latency.time():
        # ... prediction logic
```

#### 5. Caching
Cache predictions for identical inputs (useful if patients re-checked):
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_prediction(features_tuple):
    return model.predict([features_tuple])
```



## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **ML Framework** | scikit-learn 1.5.2 | Model training & inference |
| **API Framework** | FastAPI 0.101.0 | REST API endpoints |
| **ASGI Server** | Uvicorn 0.22.0 | Production ASGI server |
| **Validation** | Pydantic 1.10.12 | Request/response schemas |
| **Serialization** | Joblib 1.3.2 | Model persistence |
| **Data Processing** | Pandas 2.2.3, NumPy 1.26.4 | Data manipulation |
| **Testing** | Pytest 7.4.0 | Unit & integration tests |
| **HTTP Client** | httpx 0.27.0 | Testing API calls |
| **Containerization** | Docker | Package as image |
| **Orchestration** | Docker Compose | Local multi-container |
| **CI/CD** | GitHub Actions | Automation |
| **Registry** | GHCR | Docker image hosting |


## Glossary

**Pipeline**: scikit-learn object that chains transformers + estimator
**RMSE**: Root Mean Squared Error (lower is better)
**GHCR**: GitHub Container Registry (Docker image hosting)
**Smoke test**: Basic test to verify system isn't "on fire"
**Lifespan**: FastAPI feature for startup/shutdown hooks
**Pydantic**: Data validation using Python type hints
**Joblib**: Efficient serialization for Python objects (especially numpy arrays)

---


### Common Commands
```bash
# Train model
python -m src.train --version v0.2 --model ridge

# Run API locally
uvicorn app.main:app --reload

# Run tests
pytest -v

# Build Docker
docker build -t triage:local .

# Run container
docker run -p 8080:8080 triage:local

# Test endpoint
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '[{"age":0,"sex":0,"bmi":0,"bp":0,"s1":0,"s2":0,"s3":0,"s4":0,"s5":0,"s6":0}]'
```

