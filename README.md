# Virtual Diabetes Clinic Triage

ML service for predicting diabetes progression and prioritizing patient follow-ups.

## Overview

This project implements an MLOps pipeline for diabetes progression prediction. The service uses machine learning to generate continuous risk scores that help healthcare teams prioritize patient follow-ups in virtual clinic settings.

## Quick Start

### Local Development

```bash
# 1. Install dependencies
python3 -m pip install -r requirements-dev.txt
python3 -m pip install -e .

# 2. Train the latest (v0.2) model
python3 scripts/train.py

#    Optional: retrain the baseline (v0.1) model
python3 scripts/train.py --config config/config_v0.1.yaml

# 3. Start the API
python3 scripts/predict.py
```

### Docker Deployment (single command)

```bash
docker-compose up --build
```

The API listens on `http://localhost:8000`.

## API Endpoints

### Health Check
```bash
GET /health
```
Response:
```json
{
  "status": "ok",
  "model_version": "diabetes_triage_v0.2"
}
```

### Single Prediction
```bash
POST /predict
```
Request body:
```json
{
  "age": 0.02, "sex": -0.044, "bmi": 0.06, "bp": -0.03,
  "s1": -0.02, "s2": 0.03, "s3": -0.02, "s4": 0.02,
  "s5": 0.02, "s6": -0.001
}
```
Response:
```json
{
  "prediction": 152.13
}
```

### Batch Predictions
```bash
POST /predict/batch
```

### Interactive Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
├── .github/workflows/    # CI/CD pipelines
├── src/diabetes_triage/  # Main package
│   ├── api/             # FastAPI service
│   ├── data/            # Data loading
│   ├── models/          # ML models
│   ├── training/        # Training pipeline
│   └── utils/           # Configuration
├── tests/               # Test suite
├── models/              # Trained model artifacts
├── config/              # Configuration files
└── scripts/             # Entry point scripts
```

## Model Information

### Current Version (v0.2)
- **Algorithm**: Ridge Regression with L2 regularization (alpha=10.0)
- **Test RMSE**: 53.626
- **R² Score**: 0.457
- **Improvement over v0.1**: 0.42% RMSE reduction

### Baseline Version (v0.1)
- **Algorithm**: LinearRegression with StandardScaler
- **Test RMSE**: 53.853
- **R² Score**: 0.453

### Dataset
- **Source**: sklearn diabetes regression dataset
- **Features**: 10 normalized physiological measurements
- **Training Set**: 353 samples
- **Test Set**: 89 samples (20% split)
- **Random Seed**: 42 (reproducibility)

## Development

### Running Tests
```bash
pytest tests/ -v --cov=src
```

### Code Quality
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Configuration

Edit `config/config.yaml` to modify model parameters, API settings, and file paths.  
- The default file is pinned to the v0.2 Ridge regression model.  
- A baseline configuration lives at `config/config_v0.1.yaml`; copy it over `config/config.yaml` if you want the API to load the LinearRegression baseline instead.

## CI/CD Pipeline

GitHub Actions automatically:
1. Runs tests and linting on PR/push
2. Trains models on main branch
3. Builds and pushes Docker images
4. Runs security scans
5. Creates versioned releases on tags

## Version History

- **v0.2.0**: Ridge regression with L2 regularization
- **v0.1.0**: Baseline LinearRegression model
