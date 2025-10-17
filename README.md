# Virtual Diabetes Clinic Triage — ML Service

This project simulates a **virtual diabetes clinic triage system**.  
It predicts short-term disease progression (using the open scikit-learn *Diabetes* dataset) and exposes a REST API for nurses to prioritize patient follow-ups.

---

## Repository Setup

```bash
git clone https://github.com/Abbe23-3/Maio_assignment3
cd Maio_assignment3
```

## 1. Create and Activate Virtual Environment

**On macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**On Windows (CMD):**
```bash
python -m venv .venv
.venv\Scripts\activate
```
## 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## 3. Train Models

**Train v0.1 (Linear Regression):**
```bash
python -m src.train --version v0.1 --model linear --out_dir models --random_state 42
```

**Train v0.2 (Ridge Regression):**
```bash
python -m src.train --version v0.2 --model ridge --out_dir models --random_state 42
```

**Check metrics:**
```bash
# macOS/Linux
cat models/metrics_v0.1.json
cat models/metrics_v0.2.json

# Windows (CMD)
type models\metrics_v0.1.json
type models\metrics_v0.2.json
```

## 4. Run the API Locally

**On macOS / Linux:**
```bash
export MODEL_PATH=models/model_v0.2.joblib
export METRICS_PATH=models/metrics_v0.2.json
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

**On Windows (CMD):**
```bash
set MODEL_PATH=models\model_v0.2.joblib
set METRICS_PATH=models\metrics_v0.2.json
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

##  5. Test the /predict Endpoint

Once the server is running:
```bash
curl -X POST "http://127.0.0.1:8080/predict" -H "Content-Type: application/json" -d "[{\"age\":0,\"sex\":0,\"bmi\":0,\"bp\":0,\"s1\":0,\"s2\":0,\"s3\":0,\"s4\":0,\"s5\":0,\"s6\":0,\"id\":\"p1\"}]"
```

Example Output:

```bash
[
  {
    "id": "p1",
    "progression": 151.34880031817556,
    "risk_score": 0.3936099698385532
  }
]
```

##  6. Build and Run with Docker
```bash
docker build -t maio_assignment3:local . && docker run -p 8080:8080 maio_assignment3:local
```

Test in another terminal:
```bash
curl -X GET http://127.0.0.1:8080/health
```

or:

```bash
curl -X POST "http://127.0.0.1:8080/predict" -H "Content-Type: application/json" -d "[{\"age\":0,\"sex\":0,\"bmi\":0,\"bp\":0,\"s1\":0,\"s2\":0,\"s3\":0,\"s4\":0,\"s5\":0,\"s6\":0,\"id\":\"p1\"}]"
```

##  Project Structure
```bash
Maio_assignment3/
│
├── app/                  # FastAPI app (main.py)
├── src/                  # Training scripts (train.py)
├── models/               # Saved models + metrics
├── tests/                # Unit tests
├── Dockerfile
├── requirements.txt
├── README.md
└── .github/workflows/ci.yml
```

## 7. Using Pre-built Docker Images from GitHub Container Registry

Pre-built Docker images are automatically published to GHCR when you create a release tag.

**Pull and run v0.1:**
```bash
docker pull ghcr.io/<your-username>/maio_assignment3:v0.1
docker run -p 8080:8080 ghcr.io/<your-username>/maio_assignment3:v0.1
```

**Pull and run v0.2:**
```bash
docker pull ghcr.io/<your-username>/maio_assignment3:v0.2
docker run -p 8080:8080 ghcr.io/<your-username>/maio_assignment3:v0.2
```

**Test the endpoints:**
```bash
# Health check (includes model version)
curl http://localhost:8080/health

# Expected response: {"status":"ok","model_version":"v0.2"}

# Prediction
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d '[{"age":0.02,"sex":-0.044,"bmi":0.06,"bp":-0.03,"s1":-0.02,"s2":0.03,"s3":-0.02,"s4":0.02,"s5":0.02,"s6":-0.001,"id":"patient-001"}]'
```

## 8. API Documentation

### GET /health

Returns service health status and model version.

**Response:**
```json
{
  "status": "ok",
  "model_version": "v0.2"
}
```

### POST /predict

Accepts a batch of patient data and returns progression predictions with risk scores.

**Request body (array of Patient objects):**
```json
[
  {
    "id": "patient-001",
    "age": 0.02,
    "sex": -0.044,
    "bmi": 0.06,
    "bp": -0.03,
    "s1": -0.02,
    "s2": 0.03,
    "s3": -0.02,
    "s4": 0.02,
    "s5": 0.02,
    "s6": -0.001
  }
]
```

**Response:**
```json
[
  {
    "id": "patient-001",
    "progression": 154.32,
    "risk_score": 0.42
  }
]
```

**Field descriptions:**
- `id` (optional): Patient identifier for tracking
- `age`, `sex`, `bmi`, `bp`: Normalized clinical features
- `s1`-`s6`: Normalized serum measurements
- `progression`: Raw model prediction (disease progression index)
- `risk_score`: Normalized score in [0, 1] range for triage prioritization

## 9. Continuous Integration & Deployment

### CI Pipeline (on push/PR)
GitHub Actions automatically:
- Lints code with flake8
- Runs unit tests with pytest
- Trains baseline model and uploads artifacts
- Builds Docker image and runs smoke tests

### Release Pipeline (on tag push)
When you push a version tag (e.g., `v0.1`, `v0.2`), the release workflow:
1. Trains the appropriate model for that version
2. Builds Docker image
3. Pushes image to GitHub Container Registry (GHCR)
4. Runs container smoke tests
5. Creates GitHub Release with model artifacts and CHANGELOG

**To create a release:**
```bash
git tag v0.2
git push origin v0.2
```

This will trigger the release workflow and publish to GHCR at:
- `ghcr.io/<your-username>/maio_assignment3:v0.2`

## 10. Model Comparison (v0.1 vs v0.2)

| Metric | v0.1 (Linear) | v0.2 (Ridge) | Improvement |
|--------|---------------|--------------|-------------|
| RMSE | 53.85 | 53.63 | -0.42% |
| Model Type | LinearRegression | Ridge (GridSearchCV) | Regularized |
| Hyperparameters | None | α tuned via 5-fold CV | Optimized |

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and rationale.
