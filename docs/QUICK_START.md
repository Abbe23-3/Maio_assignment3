# Quick Start

1. **Clone & Setup**
   ```bash
   git clone https://github.com/Abbe23-3/Maio_assignment3
   cd Maio_assignment3
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Train Models**
   ```bash
   python -m src.train --version v0.1 --model linear --random_state 42
   python -m src.train --version v0.2 --model ridge --random_state 42
   ```

3. **Run API**
   ```bash
   export MODEL_PATH=models/model_v0.2.joblib
   export METRICS_PATH=models/metrics_v0.2.json
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

4. **Test Endpoints**
   ```bash
   curl http://127.0.0.1:8080/health
   curl -X POST http://127.0.0.1:8080/predict \
     -H "Content-Type: application/json" \
     -d '[{"age":0,"sex":0,"bmi":0,"bp":0,"s1":0,"s2":0,"s3":0,"s4":0,"s5":0,"s6":0,"id":"demo"}]'
   ```

5. **Docker Option**
   ```bash
   docker compose up --build -d
   curl http://127.0.0.1:8080/health
   docker compose down
   ```

6. **CI/CD Reference**
   - Read `docs/PIPELINE_GUIDE.md` for workflow details.
   - See `CHANGELOG.md` for versioned metrics.
