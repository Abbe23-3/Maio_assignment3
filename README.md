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
On macOS / Linux
```bash
python -m venv .venv
source .venv/bin/activate
```
On Windows (CMD)
```bash
python -m venv .venv
.venv\Scripts\activate
```
## 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## 3. Train Models
Baseline (v0.1)
```bash
python -m src.train --version v0.1 --model linear --out_dir models --random_state 42
cat models/metrics_v0.1.json  # Windows: type models\metrics_v0.1.json
```

Improved (v0.2)
```bash
python -m src.train --version v0.2 --model ridge --out_dir models --random_state 42
cat models/metrics_v0.2.json
```

## 4. Run the API Locally
On macOS / Linux
```bash
export MODEL_PATH=models/model_v0.2.joblib
export METRICS_PATH=models/metrics_v0.2.json
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Windows (CMD)
```bash
set MODEL_PATH=models\model_v0.2.joblib
set METRICS_PATH=models\metrics_v0.2.json
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## 5. Test the API

Health check:
```bash
curl http://127.0.0.1:8080/health
# {"status":"ok","model_loaded":true,"model_version":"v0.2"}
```

Prediction:
```bash
curl -X POST "http://127.0.0.1:8080/predict" \
  -H "Content-Type: application/json" \
  -d "[{\"age\":0,\"sex\":0,\"bmi\":0,\"bp\":0,\"s1\":0,\"s2\":0,\"s3\":0,\"s4\":0,\"s5\":0,\"s6\":0,\"id\":\"p1\"}]"
# [{"id":"p1","progression":151.35,"prediction":151.35,"risk_score":0.39}]
```

## 6. Build and Run with Docker
```bash
docker build -t maio_assignment3:local .
docker run -p 8080:8080 maio_assignment3:local
```

Using docker-compose:
```bash
docker compose up --build -d
curl http://127.0.0.1:8080/health
docker compose down
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
└── .github/workflows/
    ├── ci.yml
    └── release.yml
```

## 7. Continuous Integration (CI)
- `ci.yml` runs lint/tests, trains v0.1 & v0.2, uploads artifacts, and smoke-tests the v0.2 Docker image.
- `release.yml` runs on tags `v*`, retrains the appropriate model, builds & pushes `ghcr.io/<user>/maio_assignment3:<tag>`, smoke-tests the pushed image, and publishes a GitHub Release with artifacts + metrics.

## 8. Documentation
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/PIPELINE_GUIDE.md`](docs/PIPELINE_GUIDE.md)
- [`docs/QUICK_START.md`](docs/QUICK_START.md)
- [`docs/ORGANIZATION_RECOMMENDATIONS.md`](docs/ORGANIZATION_RECOMMENDATIONS.md)

## 9. Release Flow
```bash
# Ensure main is green, then create a tag
git tag v0.2
git push origin v0.2

# Release workflow will train, build & push ghcr.io/<your-user>/maio_assignment3:v0.2
# and publish a GitHub Release with release notes + artifacts.
```
