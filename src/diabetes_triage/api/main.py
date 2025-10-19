import logging
import joblib
import pandas as pd
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

from .schemas import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse
)
from ..utils.config import load_config, get_model_path
from ..data.loader import validate_input_features

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instance and startup time
model = None
config = None
startup_time = time.time()

app = FastAPI(
    title="Virtual Diabetes Clinic - Triage API",
    description="""
    ## Overview
    ML service for predicting diabetes progression and prioritizing patient follow-ups in virtual clinic settings.

    ## How It Works
    1. **Input**: Patient health metrics (normalized physiological measurements)
    2. **Processing**: ML model predicts disease progression score
    3. **Output**: Risk score and level with clinical recommendations

    ## Risk Classification
    - **Low Risk** (<100): Routine follow-up
    - **Medium Risk** (100-200): Schedule follow-up within 3 months
    - **High Risk** (>200): Urgent follow-up needed

    ## Use Cases
    - Prioritize patients for virtual clinic appointments
    - Triage dashboard for healthcare teams
    - Automated risk assessment workflows

    ## Features
    - Single patient predictions
    - Batch processing for multiple patients
    - Real-time risk classification
    - Clinical recommendations
    """,
    version="0.2.0",
    contact={
        "name": "MLOps Team",
        "url": "https://github.com/yourusername/Maio_MLOps",
    },
    license_info={
        "name": "MIT",
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_model():
    """Load the trained model at startup."""
    global model, config
    try:
        config = load_config()
        model_path = get_model_path(config["model"]["name"], config["paths"]["models_dir"])
        
        if not model_path.exists():
            logger.error(f"Model file not found: {model_path}")
            return False
            
        model = joblib.load(model_path)
        logger.info(f"Model loaded successfully from {model_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False


def classify_risk(progression_score: float) -> tuple[str, str]:
    """Classify risk level based on progression score.

    Returns:
        tuple: (risk_level, recommendation)
    """
    if progression_score < 100:
        return "low", "Routine follow-up - next scheduled appointment"
    elif progression_score < 200:
        return "medium", "Schedule follow-up within 3 months"
    else:
        return "high", "Urgent follow-up needed within 2 weeks"


@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    success = load_model()
    if not success:
        logger.warning("Failed to load model during startup")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with HTML landing page."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Virtual Diabetes Clinic - Triage API</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 40px 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 1200px;
                width: 100%;
                padding: 50px;
                margin: 0 auto;
            }
            h1 {
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-align: center;
            }
            h2 {
                color: #334155;
                margin: 30px 0 15px 0;
            }
            .subtitle {
                color: #666;
                text-align: center;
                margin-bottom: 40px;
                font-size: 1.1em;
            }
            .status {
                background: #f0fdf4;
                border-left: 4px solid #22c55e;
                padding: 20px;
                margin-bottom: 30px;
                border-radius: 8px;
            }
            .status.unhealthy {
                background: #fef2f2;
                border-left-color: #ef4444;
            }
            .risk-levels {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 30px 0;
            }
            .risk-card {
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }
            .risk-low { background: #dcfce7; border: 2px solid #22c55e; }
            .risk-medium { background: #fef3c7; border: 2px solid #f59e0b; }
            .risk-high { background: #fee2e2; border: 2px solid #ef4444; }
            .risk-card h3 { margin-bottom: 5px; }
            .risk-card p { font-size: 0.9em; color: #374151; }

            .prediction-section {
                background: #f8fafc;
                padding: 30px;
                border-radius: 15px;
                margin: 30px 0;
                border: 2px solid #e2e8f0;
            }
            .form-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .form-group {
                display: flex;
                flex-direction: column;
            }
            .form-group label {
                font-weight: 600;
                color: #334155;
                margin-bottom: 8px;
                font-size: 0.9em;
            }
            .form-group input {
                padding: 12px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 1em;
                transition: all 0.3s;
            }
            .form-group input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .btn {
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s;
                display: inline-block;
                cursor: pointer;
                border: none;
                font-size: 1em;
            }
            .btn-predict {
                background: #667eea;
                color: white;
                width: 100%;
                margin-top: 20px;
            }
            .btn-predict:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            .btn-predict:disabled {
                background: #94a3b8;
                cursor: not-allowed;
                transform: none;
            }
            .btn-example {
                background: #f1f5f9;
                color: #334155;
                padding: 10px 20px;
                margin-top: 10px;
                display: inline-block;
                margin-right: 10px;
                font-size: 0.9em;
            }
            .btn-example:hover {
                background: #e2e8f0;
            }
            .result-section {
                margin-top: 30px;
                padding: 30px;
                border-radius: 15px;
                display: none;
            }
            .result-section.show {
                display: block;
                animation: slideDown 0.5s ease;
            }
            @keyframes slideDown {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .result-section.low {
                background: #dcfce7;
                border: 3px solid #22c55e;
            }
            .result-section.medium {
                background: #fef3c7;
                border: 3px solid #f59e0b;
            }
            .result-section.high {
                background: #fee2e2;
                border: 3px solid #ef4444;
            }
            .result-score {
                font-size: 3em;
                font-weight: bold;
                text-align: center;
                margin: 20px 0;
            }
            .result-label {
                text-align: center;
                font-size: 1.5em;
                font-weight: 600;
                margin-bottom: 10px;
            }
            .result-recommendation {
                text-align: center;
                font-size: 1.1em;
                margin-top: 15px;
                padding: 15px;
                background: white;
                border-radius: 8px;
            }
            .loading {
                text-align: center;
                padding: 20px;
                display: none;
            }
            .loading.show {
                display: block;
            }
            .spinner {
                border: 4px solid #f3f4f6;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .info-box {
                background: #eff6ff;
                border-left: 4px solid #3b82f6;
                padding: 15px;
                margin: 15px 0;
                border-radius: 8px;
                font-size: 0.9em;
            }
            .cta-buttons {
                display: flex;
                gap: 15px;
                margin-top: 40px;
                flex-wrap: wrap;
                justify-content: center;
            }
            .btn-primary {
                background: #667eea;
                color: white;
            }
            .btn-primary:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            .btn-secondary {
                background: white;
                color: #667eea;
                border: 2px solid #667eea;
            }
            .btn-secondary:hover {
                background: #667eea;
                color: white;
            }
            .version {
                text-align: center;
                color: #94a3b8;
                margin-top: 30px;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Virtual Diabetes Clinic</h1>
            <p class="subtitle">ML-Powered Patient Triage & Risk Assessment</p>

            <div class="status" id="status">
                <strong>Checking service status...</strong>
            </div>

            <!-- Interactive Prediction Form -->
            <div class="prediction-section">
                <h2>Try Risk Prediction</h2>
                <p style="color: #64748b; margin-bottom: 20px;">Enter patient health metrics (normalized values) to get an instant risk assessment.</p>

                <div class="info-box">
                    <strong>Note:</strong> All values are normalized (typically between -0.2 and 0.2). Use the example buttons below to load sample patient data.
                </div>

                <div>
                    <button class="btn-example" onclick="loadExample('high')">Load High Risk Example</button>
                    <button class="btn-example" onclick="loadExample('medium')">Load Medium Risk Example</button>
                    <button class="btn-example" onclick="loadExample('low')">Load Low Risk Example</button>
                </div>

                <form id="predictionForm">
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="age">Age (normalized)</label>
                            <input type="number" step="0.000001" id="age" name="age" placeholder="0.038076" required>
                        </div>
                        <div class="form-group">
                            <label for="sex">Sex (normalized)</label>
                            <input type="number" step="0.000001" id="sex" name="sex" placeholder="0.050680" required>
                        </div>
                        <div class="form-group">
                            <label for="bmi">BMI (normalized)</label>
                            <input type="number" step="0.000001" id="bmi" name="bmi" placeholder="0.061696" required>
                        </div>
                        <div class="form-group">
                            <label for="bp">Blood Pressure</label>
                            <input type="number" step="0.000001" id="bp" name="bp" placeholder="0.021872" required>
                        </div>
                        <div class="form-group">
                            <label for="s1">Cholesterol (S1)</label>
                            <input type="number" step="0.000001" id="s1" name="s1" placeholder="-0.044223" required>
                        </div>
                        <div class="form-group">
                            <label for="s2">LDL (S2)</label>
                            <input type="number" step="0.000001" id="s2" name="s2" placeholder="-0.034821" required>
                        </div>
                        <div class="form-group">
                            <label for="s3">HDL (S3)</label>
                            <input type="number" step="0.000001" id="s3" name="s3" placeholder="-0.043401" required>
                        </div>
                        <div class="form-group">
                            <label for="s4">Cholesterol/HDL (S4)</label>
                            <input type="number" step="0.000001" id="s4" name="s4" placeholder="-0.002592" required>
                        </div>
                        <div class="form-group">
                            <label for="s5">Triglycerides (S5)</label>
                            <input type="number" step="0.000001" id="s5" name="s5" placeholder="0.019908" required>
                        </div>
                        <div class="form-group">
                            <label for="s6">Blood Sugar (S6)</label>
                            <input type="number" step="0.000001" id="s6" name="s6" placeholder="-0.017646" required>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-predict" id="predictBtn">
                        Get Risk Prediction
                    </button>
                </form>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p style="margin-top: 15px; color: #64748b;">Analyzing patient data...</p>
                </div>

                <div class="result-section" id="result">
                    <div class="result-label" id="resultLabel"></div>
                    <div class="result-score" id="resultScore"></div>
                    <div class="result-recommendation" id="resultRecommendation"></div>
                </div>
            </div>

            <h2>Risk Classification Guide</h2>
            <div class="risk-levels">
                <div class="risk-card risk-low">
                    <h3>Low Risk</h3>
                    <p>&lt; 100</p>
                    <p style="margin-top: 8px;">Routine follow-up</p>
                </div>
                <div class="risk-card risk-medium">
                    <h3>Medium Risk</h3>
                    <p>100 - 200</p>
                    <p style="margin-top: 8px;">Follow-up in 3 months</p>
                </div>
                <div class="risk-card risk-high">
                    <h3>High Risk</h3>
                    <p>&gt; 200</p>
                    <p style="margin-top: 8px;">Urgent follow-up needed</p>
                </div>
            </div>

            <div class="cta-buttons">
                <a href="/docs" class="btn btn-primary">API Documentation</a>
                <a href="/health" class="btn btn-secondary">Health Check</a>
            </div>

            <p class="version">API v0.2.0 | Powered by FastAPI & scikit-learn</p>
        </div>

        <script>
            const examples = {
                high: {
                    age: 0.038076, sex: 0.050680, bmi: 0.061696,
                    bp: 0.021872, s1: -0.044223, s2: -0.034821,
                    s3: -0.043401, s4: -0.002592, s5: 0.019908, s6: -0.017646
                },
                medium: {
                    age: 0.001, sex: 0.045, bmi: -0.020,
                    bp: 0.015, s1: 0.010, s2: 0.005,
                    s3: 0.008, s4: 0.001, s5: 0.005, s6: 0.003
                },
                low: {
                    age: -0.045, sex: -0.044, bmi: -0.070,
                    bp: -0.030, s1: 0.050, s2: 0.040,
                    s3: 0.060, s4: 0.010, s5: -0.025, s6: 0.020
                }
            };

            function loadExample(type) {
                const data = examples[type];
                Object.keys(data).forEach(key => {
                    document.getElementById(key).value = data[key];
                });
                document.getElementById('result').classList.remove('show');
            }

            // Check health status on page load
            fetch('/health')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('status');
                    if (data.status === 'healthy' && data.model_loaded) {
                        statusDiv.innerHTML = '<strong>Service Status: Healthy</strong><br>Model loaded and ready for predictions';
                        statusDiv.className = 'status';
                    } else {
                        statusDiv.innerHTML = '<strong>Service Status: Degraded</strong><br>Model not loaded or service unavailable';
                        statusDiv.className = 'status unhealthy';
                    }
                })
                .catch(error => {
                    const statusDiv = document.getElementById('status');
                    statusDiv.innerHTML = '<strong>Service Status: Unavailable</strong><br>Could not connect to API';
                    statusDiv.className = 'status unhealthy';
                });

            // Handle form submission
            document.getElementById('predictionForm').addEventListener('submit', async (e) => {
                e.preventDefault();

                const formData = new FormData(e.target);
                const data = {};
                formData.forEach((value, key) => {
                    data[key] = parseFloat(value);
                });

                // Show loading, hide result
                document.getElementById('loading').classList.add('show');
                document.getElementById('result').classList.remove('show');
                document.getElementById('predictBtn').disabled = true;

                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });

                    if (!response.ok) {
                        throw new Error('Prediction failed');
                    }

                    const result = await response.json();

                    // Hide loading
                    document.getElementById('loading').classList.remove('show');

                    // Show result
                    const resultDiv = document.getElementById('result');
                    resultDiv.className = 'result-section show ' + result.risk_level;

                    document.getElementById('resultLabel').innerHTML =
                        result.risk_level.toUpperCase() + ' RISK';
                    document.getElementById('resultScore').textContent =
                        'Score: ' + result.progression_score.toFixed(2);
                    document.getElementById('resultRecommendation').innerHTML =
                        '<strong>Recommendation:</strong><br>' + result.recommendation;

                    // Scroll to result
                    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

                } catch (error) {
                    alert('Error making prediction. Please try again.');
                    document.getElementById('loading').classList.remove('show');
                } finally {
                    document.getElementById('predictBtn').disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok" if model is not None else "error",
        model_version=config["model"]["name"] if config else "unknown"
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Predict diabetes progression for a single patient.

    Returns a continuous risk score that can be used to prioritize follow-ups.
    Higher scores indicate greater deterioration risk.

    **Risk Levels:**
    - Low (<100): Routine follow-up
    - Medium (100-200): Follow-up within 3 months
    - High (>200): Urgent follow-up needed
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Convert request to DataFrame
        input_dict = {k: v for k, v in request.dict().items() if k != 'model_config'}
        input_data = pd.DataFrame([input_dict])

        # Validate input features
        if not validate_input_features(input_data):
            raise HTTPException(status_code=400, detail="Invalid input features")

        # Make prediction
        prediction = float(model.predict(input_data)[0])

        return PredictionResponse(
            prediction=prediction
        )

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(request: BatchPredictionRequest):
    """
    Predict diabetes progression for multiple patients.

    Useful for processing multiple patients at once for triage dashboard.
    Results are automatically sorted by risk score (highest first) for prioritization.

    **Returns:**
    - Predictions sorted by risk (high to low)
    - Summary statistics of risk levels
    - Total patient count
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Convert requests to DataFrame
        input_data = pd.DataFrame([
            {k: v for k, v in patient.dict().items() if k != 'model_config'}
            for patient in request.patients
        ])

        # Validate input features
        if not validate_input_features(input_data):
            raise HTTPException(status_code=400, detail="Invalid input features")

        # Make predictions
        prediction_scores = model.predict(input_data)

        # Create response list
        predictions = [
            PredictionResponse(prediction=float(score))
            for score in prediction_scores
        ]

        # Sort by score (highest first) for triage prioritization
        predictions.sort(key=lambda x: x.prediction, reverse=True)

        return BatchPredictionResponse(
            predictions=predictions,
            total_patients=len(predictions)
        )

    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


def main():
    """Main entry point for the API server."""
    try:
        config = load_config()
        uvicorn.run(
            "diabetes_triage.api.main:app",
            host=config["api"]["host"],
            port=config["api"]["port"],
            reload=False
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    main()
