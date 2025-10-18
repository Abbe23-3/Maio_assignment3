# Quick Start Guide


### 1. Clone and Setup 
```bash
# Clone repository
git clone https://github.com/Abbe23-3/Maio_assignment3
cd Maio_assignment3

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Train a Model 
```bash
# Train v0.2 (Ridge regression)
python -m src.train --version v0.2 --model ridge --random_state 42

# Output: models/model_v0.2.joblib and models/metrics_v0.2.json
```

### 3. Run the API 
```bash
# Set which model to use
export MODEL_PATH=models/model_v0.2.joblib
export METRICS_PATH=models/metrics_v0.2.json

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8080

# Server running at: http://localhost:8080
```

### 4. Test 
```bash
# In another terminal

# Health check
curl http://localhost:8080/health
# Response: {"status":"ok","model_version":"v0.2"}

# Prediction
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '[{"age":0,"sex":0,"bmi":0,"bp":0,"s1":0,"s2":0,"s3":0,"s4":0,"s5":0,"s6":0,"id":"p1"}]'
# Response: [{"id":"p1","progression":151.34,"risk_score":0.39}]
```

### 5. Using Docker 
```bash
# Build and run with Docker Compose
docker-compose up -d

# Test
curl http://localhost:8080/health

# Stop
docker-compose down
```

---

## Common Tasks

### Run Tests
```bash
pytest
```

### Lint Code
```bash
flake8 .
```

### Train All Models
```bash
python -m src.train --version v0.1 --model linear --random_state 42
python -m src.train --version v0.2 --model ridge --random_state 42
```

### Create a Release
```bash
# After pushing your changes to GitHub
git tag v0.2
git push origin v0.2

# This triggers the release pipeline automatically!
```

---

## File Tour

### Most Important Files
- **`app/main.py`** - The API server (FastAPI)
- **`src/train.py`** - Training script
- **`README.md`** - Detailed usage instructions
- **`CHANGELOG.md`** - What changed in each version

### Configuration Files
- **`requirements.txt`** - Python dependencies
- **`Dockerfile`** - How to build the container
- **`docker-compose.yml`** - How to run locally
- **`.github/workflows/`** - CI/CD automation

### Documentation (you are here!)
- **`docs/PIPELINE_GUIDE.md`** - How CI/CD works
- **`docs/ARCHITECTURE.md`** - How everything fits together
- **`docs/ORGANIZATION_RECOMMENDATIONS.md`** - How to improve the project
- **`docs/QUICK_START.md`** - This file!

---

## Need More Help?

1. **How does the CI/CD pipeline work?** → Read [`docs/PIPELINE_GUIDE.md`](PIPELINE_GUIDE.md)
2. **How is the system architected?** → Read [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)
3. **How can I improve the project?** → Read [`docs/ORGANIZATION_RECOMMENDATIONS.md`](ORGANIZATION_RECOMMENDATIONS.md)
4. **Detailed usage examples?** → Read [`README.md`](../README.md)

---

## Troubleshooting

### "Module not found" errors
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Port 8080 already in use
```bash
# Use a different port
uvicorn app.main:app --port 8081

# Or kill the existing process
lsof -ti:8080 | xargs kill
```

### Docker build fails
```bash
# Clean Docker cache
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

### Tests fail
```bash
# Make sure models are trained
python -m src.train --version v0.1 --model linear
python -m src.train --version v0.2 --model ridge

# Run tests with verbose output
pytest -v
```

---

## What's Next?

After getting comfortable with the basics:

1. **Explore the code**: Read through `app/main.py` and `src/train.py`
2. **Try different models**: Use `--model rf` for Random Forest
3. **Make changes**: Edit the code and see CI/CD in action
4. **Read the architecture**: Understand the full system design
5. **Contribute**: Implement some of the recommendations!

**Happy coding! 🚀**
