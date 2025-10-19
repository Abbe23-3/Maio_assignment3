# CI/CD Pipeline Guide

This project ships with two GitHub Actions workflows that together guarantee testing, reproducible training, container validation, and release automation.

## Workflows

### 1. `ci.yml` – Continuous Integration
Triggers on every push and pull request.

Jobs:
1. **lint-test**
   - Checkout repo.
   - `actions/setup-python` (3.11).
   - Install dependencies via `pip install -r requirements.txt`.
   - Run `flake8` and `pytest`.

2. **train-and-smoke** (matrix: `v0.1` linear, `v0.2` ridge)
   - Repeats checkout + dependency install.
   - Trains the matrix-defined version.
   - Uploads both model and metrics as build artifacts.
   - Builds the Docker image for `v0.2` and runs a container smoke test hitting `/health` and `/predict`.

Artifacts produced:
- `model-v0.1/` and `model-v0.2/` containing the joblib + metrics JSON files to support reproducibility.

### 2. `release.yml` – Versioned Releases
Triggers on `git push` of tags matching `v*`.

Steps:
1. Setup identical Python env & install requirements.
2. Determine version/model mapping (e.g. `v0.1` → linear, others default to ridge).
3. Retrain with deterministic seeds and print metrics.
4. Authenticate to GHCR using repo `GITHUB_TOKEN`.
5. Build Docker image tagged `ghcr.io/<owner>/<repo>:<version>` and push.
6. Smoke test the freshly pushed image in a transient container.
7. Generate release notes from `CHANGELOG.md` + metrics via `scripts/generate_release_notes.py`.
8. Upload artifacts (`model_<version>.joblib`, `metrics_<version>.json`).
9. Publish a GitHub Release including release notes and artifacts.

## Local Verification Checklist

- `PYTHONPATH=. pytest`
- `flake8`
- `python -m src.train --version v0.2 --model ridge`
- `docker build -t maio_assignment3:local .`
- `docker run -p 8080:8080 maio_assignment3:local` + curl health/predict.

## Release Process

1. Ensure CI is green on the target commit.
2. Tag with the desired version: `git tag v0.2`.
3. Push the tag: `git push origin v0.2`.
4. Verify the release workflow turns green and a GitHub Release + GHCR image appear.

## Secrets & Permissions

- Release workflow relies on the built-in `${{ secrets.GITHUB_TOKEN }}` (no extra secrets required).
- The workflow needs `contents: write` and `packages: write` to publish releases and push to GHCR (granted in YAML).
