# CI/CD Pipeline Guide

## Table of Contents
1. [Overview](#overview)
2. [Project Architecture](#project-architecture)
3. [CI Pipeline (Continuous Integration)](#ci-pipeline)
4. [Release Pipeline (Continuous Deployment)](#release-pipeline)
5. [Workflow Diagrams](#workflow-diagrams)
6. [Step-by-Step Walkthrough](#step-by-step-walkthrough)

---

## Overview

This project uses **GitHub Actions** to automate testing, training, building, and deployment of a machine learning API service. There are two main workflows:

1. **CI Workflow** (`.github/workflows/ci.yml`) - Runs on every push/PR
2. **Release Workflow** (`.github/workflows/release.yml`) - Runs when you create a version tag

---

## Project Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LOCAL DEVELOPMENT                        │
│                                                             │
│  1. Write code (train.py, main.py)                         │
│  2. Train models locally                                    │
│  3. Test API locally                                        │
│  4. Commit and push to GitHub                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ├── Push to branch
                   │
       ┌───────────▼────────────┐
       │   CI PIPELINE          │
       │   (.github/workflows/  │
       │    ci.yml)             │
       │                        │
       │  • Lint code           │
       │  • Run tests           │
       │  • Train model         │
       │  • Build Docker        │
       │  • Smoke tests         │
       └────────────────────────┘
                   │
                   │ All checks pass ✓
                   │
       ┌───────────▼────────────┐
       │  CREATE TAG (v0.1)     │
       │  git tag v0.1          │
       │  git push origin v0.1  │
       └────────────────────────┘
                   │
       ┌───────────▼────────────┐
       │  RELEASE PIPELINE      │
       │  (.github/workflows/   │
       │   release.yml)         │
       │                        │
       │  • Train model         │
       │  • Build Docker image  │
       │  • Push to GHCR        │
       │  • Run smoke tests     │
       │  • Create GitHub       │
       │    Release             │
       │  • Upload artifacts    │
       └────────┬───────────────┘
                │
    ┌───────────▼────────────────────┐
    │  PUBLISHED TO GHCR             │
    │  ghcr.io/user/project:v0.1     │
    │                                │
    │  Anyone can:                   │
    │  docker pull ghcr.io/...       │
    │  docker run -p 8080:8080 ...   │
    └────────────────────────────────┘
```

---

## CI Pipeline

### When Does It Run?
- **Every push** to any branch
- **Every pull request** opened or updated

### What Does It Do?

#### Job 1: `lint-test`
```yaml
Steps:
1. Checkout code from GitHub
2. Set up Python 3.11
3. Install dependencies (pip install -r requirements.txt)
4. Run flake8 linter (checks code style)
5. Run pytest (runs all tests in tests/ directory)
```

**Purpose**: Ensure code quality and that all tests pass before proceeding.

#### Job 2: `train-upload-and-smoketest`
```yaml
Depends on: lint-test (only runs if lint-test succeeds)

Steps:
1. Checkout code
2. Set up Python 3.11
3. Install dependencies
4. Train baseline model (v0.1 linear regression)
5. Display metrics from models/metrics_v0.1.json
6. Upload model artifact to GitHub Actions artifacts
7. Build Docker image with tag "triage:<commit-sha>"
8. Run Docker container on port 8080
9. Wait 3 seconds for startup
10. Test /health endpoint (must return 200 OK)
11. Test /predict endpoint with sample payload (must return 200 OK)
```

**Purpose**: Verify that:
- Model training works
- Docker image builds successfully
- API endpoints respond correctly
- End-to-end workflow functions

### How to View CI Results

1. Go to your GitHub repository
2. Click **"Actions"** tab
3. Click on the most recent workflow run
4. Expand each job to see detailed logs

---

## Release Pipeline

### When Does It Run?
- **Only when you push a version tag** like `v0.1`, `v0.2`, etc.

### How to Trigger a Release

```bash
# Create a tag
git tag v0.2

# Push the tag to GitHub
git push origin v0.2
```

**This automatically triggers the release workflow!**

### What Does It Do?

#### Job: `build-and-release`

```yaml
Permissions:
  - contents: write (create GitHub releases)
  - packages: write (push to GitHub Container Registry)

Steps:
1. Checkout code
2. Set up Python 3.11
3. Install dependencies
4. Extract version from tag (e.g., "v0.2" from "refs/tags/v0.2")
5. Train the appropriate model:
   - If v0.1 → Linear Regression
   - If v0.2 → Ridge Regression with GridSearchCV
6. Display metrics
7. Log in to GitHub Container Registry (GHCR) using GITHUB_TOKEN
8. Build Docker image with tag "ghcr.io/username/repo:v0.2"
9. Push Docker image to GHCR
10. Run smoke tests on the container:
    - Test /health endpoint
    - Verify model_version in response
    - Test /predict endpoint
    - Verify progression and risk_score in response
11. Upload model artifacts (model_v0.2.joblib, metrics_v0.2.json)
12. Create GitHub Release with:
    - Tag name (v0.2)
    - Release notes from CHANGELOG.md
    - Model artifacts attached
```

### What Gets Published?

1. **Docker Image to GHCR**:
   - `ghcr.io/<your-username>/maio_assignment3:v0.2`
   - Anyone can pull and run this image

2. **GitHub Release**:
   - Visible on your repository's "Releases" page
   - Includes downloadable model files
   - Shows changelog content

3. **Artifacts**:
   - `model_v0.2.joblib` (trained model)
   - `metrics_v0.2.json` (performance metrics)

---

## Workflow Diagrams

### CI Workflow Flow

```
Push/PR → Checkout Code → Setup Python → Install Deps
                                            ↓
                                      Run Flake8
                                            ↓
                                       Run Tests
                                            ↓
                                    ✓ All Pass? ✗
                                         ↓
                                   Train Model
                                         ↓
                                   Build Docker
                                         ↓
                                   Run Container
                                         ↓
                               Test /health & /predict
                                         ↓
                                    ✓ Success ✗
```

### Release Workflow Flow

```
git push origin v0.2 → Extract Version (v0.2)
                             ↓
                  Train Ridge Model (v0.2)
                             ↓
                  Login to GHCR (GitHub Container Registry)
                             ↓
        Build Docker Image: ghcr.io/user/repo:v0.2
                             ↓
                  Push Image to GHCR
                             ↓
                  Pull & Run Container
                             ↓
           Test /health & /predict endpoints
                             ↓
                  Upload Model Artifacts
                             ↓
          Create GitHub Release with CHANGELOG
                             ↓
                    ✓ Published! ✗
```

---

## Step-by-Step Walkthrough

### Scenario: Making Changes and Releasing v0.3

#### Step 1: Local Development
```bash
# Make code changes
vim src/train.py

# Train new model locally
python -m src.train --version v0.3 --model rf --out_dir models

# Test locally
export MODEL_PATH=models/model_v0.3.joblib
export METRICS_PATH=models/metrics_v0.3.json
uvicorn app.main:app --port 8080
```

#### Step 2: Commit and Push
```bash
git add .
git commit -m "Add Random Forest model (v0.3)"
git push origin Devoloping_yati
```

**→ CI Pipeline automatically runs:**
- Lints your code
- Runs tests
- Trains model
- Tests Docker build

#### Step 3: Check CI Results
1. Go to GitHub → Actions tab
2. Wait for green checkmark ✓
3. Fix any failures if red ✗

#### Step 4: Update CHANGELOG
```bash
# Edit CHANGELOG.md with v0.3 changes
vim CHANGELOG.md
git add CHANGELOG.md
git commit -m "Update CHANGELOG for v0.3"
git push origin Devoloping_yati
```

#### Step 5: Create Release Tag
```bash
git tag v0.3
git push origin v0.3
```

**→ Release Pipeline automatically runs:**
- Trains the model
- Builds Docker image
- Pushes to GHCR
- Creates GitHub Release

#### Step 6: Verify Release
```bash
# Pull the published image
docker pull ghcr.io/<your-username>/maio_assignment3:v0.3

# Run it
docker run -p 8080:8080 ghcr.io/<your-username>/maio_assignment3:v0.3

# Test it
curl http://localhost:8080/health
```

---

## Key Files in the Pipeline

### `.github/workflows/ci.yml`
- **Purpose**: Continuous Integration
- **Triggers**: push, pull_request
- **Jobs**: lint-test, train-upload-and-smoketest

### `.github/workflows/release.yml`
- **Purpose**: Continuous Deployment
- **Triggers**: push tags (v*)
- **Jobs**: build-and-release

### `src/train.py`
- **Purpose**: Train ML models
- **Used by**: Both CI and Release pipelines
- **Outputs**: models/*.joblib, models/metrics_*.json

### `app/main.py`
- **Purpose**: FastAPI application
- **Used by**: Docker container
- **Endpoints**: /health, /predict

### `Dockerfile`
- **Purpose**: Package app + model into container
- **Used by**: Both pipelines to build images

### `requirements.txt`
- **Purpose**: Python dependencies
- **Used by**: All stages (local, CI, Docker)

### `CHANGELOG.md`
- **Purpose**: Document version changes
- **Used by**: Release workflow (included in GitHub Release notes)

---

## Understanding GitHub Container Registry (GHCR)

### What is GHCR?
GitHub Container Registry is a free Docker image hosting service provided by GitHub.

### How Images Are Published

1. **Login** (automated in workflow):
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

2. **Build** with GHCR naming convention:
```bash
docker build -t ghcr.io/username/repo:v0.2 .
```

3. **Push** to GHCR:
```bash
docker push ghcr.io/username/repo:v0.2
```

### Where to Find Your Images
- Go to: https://github.com/USERNAME?tab=packages
- Or: https://github.com/users/USERNAME/packages/container/REPO_NAME

### Making Images Public
By default, GHCR images are **private**. To make them public:
1. Go to the package page
2. Click "Package settings"
3. Scroll to "Danger zone"
4. Click "Change visibility" → Public

---

## Common Pipeline Tasks

### View CI/CD Logs
```bash
# Go to GitHub repo → Actions tab
# Click on workflow run
# Click on job name
# Expand step to see logs
```

### Re-run Failed Workflow
1. Go to Actions tab
2. Click on failed workflow
3. Click "Re-run all jobs" button

### Cancel Running Workflow
1. Go to Actions tab
2. Click on running workflow
3. Click "Cancel workflow" button

### Download Artifacts
1. Go to Actions tab
2. Click on completed workflow
3. Scroll to "Artifacts" section
4. Click to download


## Troubleshooting

### CI Fails on Linting
```bash
# Run locally to see errors
flake8 .

# Fix errors, then
git add .
git commit -m "Fix linting errors"
git push
```

### CI Fails on Tests
```bash
# Run locally
pytest -v

# Fix failing tests, then push
```

### Docker Build Fails
```bash
# Test locally
docker build -t test .

# Check Dockerfile for issues
# Common issues: wrong file paths, missing dependencies
```

### GHCR Push Permission Denied
- Check that workflow has `packages: write` permission
- Verify GITHUB_TOKEN is working
- Check repository settings → Actions → General → Workflow permissions

### Release Not Creating
- Ensure tag format matches pattern: `v*` (e.g., v0.1, v1.0)
- Check Actions tab for error logs
- Verify `contents: write` permission is set

---

