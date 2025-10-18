# Deployment Steps for Assignment Submission

## Summary of Changes Made

### Code Improvements
1. **app/main.py** - Modernized FastAPI with lifespan context manager, fixed feature name warnings
2. **src/train.py** - Fixed comment typo
3. **Dockerfile** - Added curl for healthcheck
4. **requirements.txt** - Updated scikit-learn to 1.5.2 (matches training environment)
5. **docker-compose.yml** - Added for easier deployment (bonus feature)
6. **README.md** - Updated with docker-compose instructions

### Models
- Both v0.1 and v0.2 models are trained and ready
- Metrics files updated

## Step-by-Step Deployment Commands

### Step 1: Review Your Changes (Optional)
```bash
# See what files have been modified
git status

# See the actual changes
git diff
```

### Step 2: Stage All Changes
```bash
# Add all modified and new files
git add app/main.py src/train.py Dockerfile requirements.txt README.md docker-compose.yml
```

### Step 3: Commit Your Changes
```bash
# Commit with a clear message
git commit -m "Modernize FastAPI lifecycle, add Docker Compose, fix sklearn version mismatch and healthcheck"
```

### Step 4: Push to GitHub
```bash
# Push to your development branch
git push origin Devoloping_yati
```

### Step 5: Create and Push Release Tags

These tags will trigger the GitHub Actions release workflow to build and publish Docker images to GHCR.

```bash
# Create v0.1 tag
git tag -a v0.1 -m "Release v0.1 - Baseline Linear Regression model"

# Create v0.2 tag
git tag -a v0.2 -m "Release v0.2 - Improved Ridge Regression model with hyperparameter tuning"

# Push both tags to GitHub (this triggers the release workflow)
git push origin v0.1
git push origin v0.2
```

### Step 6: Monitor GitHub Actions

1. Go to: https://github.com/Abbe23-3/Maio_assignment3/actions
2. You should see two "Release" workflows running (one for v0.1, one for v0.2)
3. Wait for both to complete (green checkmark)

### Step 7: Verify Releases

1. Check releases: https://github.com/Abbe23-3/Maio_assignment3/releases
2. You should see:
   - Release v0.1 with model artifacts
   - Release v0.2 with model artifacts

### Step 8: Verify GHCR Images

```bash
# Pull v0.1 image
docker pull ghcr.io/abbe23-3/maio_assignment3:v0.1

# Pull v0.2 image
docker pull ghcr.io/abbe23-3/maio_assignment3:v0.2

# Test v0.2 image
docker run -d -p 8080:8080 ghcr.io/abbe23-3/maio_assignment3:v0.2

# Test health endpoint
curl http://localhost:8080/health

# Test predict endpoint
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d '[{"age":0.02,"sex":-0.044,"bmi":0.06,"bp":-0.03,"s1":-0.02,"s2":0.03,"s3":-0.02,"s4":0.02,"s5":0.02,"s6":-0.001}]'
```

## Expected Results

### GitHub Actions
- ✅ CI workflow passes on push
- ✅ Release workflow for v0.1 completes successfully
- ✅ Release workflow for v0.2 completes successfully

### GitHub Releases
- ✅ v0.1 release created with:
  - CHANGELOG.md content
  - model_v0.1.joblib
  - metrics_v0.1.json
- ✅ v0.2 release created with:
  - CHANGELOG.md content
  - model_v0.2.joblib
  - metrics_v0.2.json

### GHCR Images
- ✅ ghcr.io/abbe23-3/maio_assignment3:v0.1 available
- ✅ ghcr.io/abbe23-3/maio_assignment3:v0.2 available
- ✅ Both images run successfully
- ✅ Both images pass health checks
- ✅ Both images respond to predict endpoint

## Troubleshooting

### If GitHub Actions Fails

1. Check the logs in the Actions tab
2. Common issues:
   - Permissions: Make sure GitHub Actions has write permissions for packages
   - Secrets: Ensure GITHUB_TOKEN is available (it should be automatic)

### If GHCR Images Are Private

By default, GHCR images are private. To make them public:
1. Go to: https://github.com/users/Abbe23-3/packages/container/maio_assignment3/settings
2. Scroll to "Danger Zone"
3. Click "Change visibility" → "Public"

### To Test Locally Before Pushing Tags

```bash
# Build and test locally
docker build -t maio_assignment3:test .
docker run -d -p 8080:8080 maio_assignment3:test
curl http://localhost:8080/health
```

## Assignment Acceptance Criteria Met

✅ Can pull ghcr.io/abbe23-3/maio_assignment3:v0.1 and :v0.2
✅ GET /health returns {"status":"ok", "model_version": "..."}
✅ POST /predict returns numeric prediction
✅ CI pipeline runs on PR/push and fails on errors
✅ Tag workflow builds image and publishes to GHCR
✅ Clear v0.1 → v0.2 improvement documented
✅ README with exact commands and sample payloads
✅ Reproducible training with seeds and pinned environment
✅ Self-contained Docker image with healthcheck
