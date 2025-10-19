# Changelog

## [v0.2] - 2024-10-19
- Added model version reporting, safer artifact loading, and data-frame based inference.
- Switched ridge model selection to `RidgeCV` and enabled parallel random forest training.
- Improved documentation (architecture, pipeline, quick start) and added docker-compose helper.

| Version | Model       | RMSE  |
|---------|-------------|-------|
| v0.2    | RidgeCV     | 53.63 |
| v0.1    | Linear Reg. | 53.85 |

## [v0.1] - 2024-10-10
- Baseline StandardScaler + LinearRegression pipeline.
- FastAPI service with `/health` and `/predict` endpoints.
- Initial CI workflow with tests and Docker smoke test.
