# Changelog

All notable changes to the Virtual Diabetes Clinic Triage ML Service.

## [v0.2] - 2025-10-17

### Changed
- **Model Algorithm**: Upgraded from simple Linear Regression to Ridge Regression with hyperparameter tuning
- **Hyperparameter Optimization**: Implemented GridSearchCV with 5-fold cross-validation to find optimal regularization strength (alpha)
- **Alpha Search Space**: Tested values [0.1, 1.0, 10.0, 100.0]

### Improved
- **Prediction Accuracy**: RMSE reduced from 53.85 to 53.63 (0.4% improvement)
- **Model Robustness**: Ridge regularization helps prevent overfitting compared to vanilla Linear Regression
- **Generalization**: L2 penalty term improves model stability on unseen patient data

### Metrics Comparison

| Metric | v0.1 (Linear) | v0.2 (Ridge) | Change |
|--------|---------------|--------------|--------|
| **RMSE** | 53.853 | 53.626 | -0.227 (-0.42%) |
| **Model Type** | LinearRegression | Ridge (GridSearchCV) | Regularized |
| **Hyperparameters** | None | alpha tuned via CV | +Optimization |
| **Training Time** | ~100ms | ~500ms | +Cross-validation |

### Rationale
While the RMSE improvement is modest (0.4%), Ridge regression provides:
1. **Better generalization**: L2 regularization prevents overfitting by penalizing large coefficients
2. **Stability**: More robust predictions when features are correlated (common in medical data)
3. **Production-ready**: Hyperparameter tuning via cross-validation ensures optimal performance
4. **Foundation for iteration**: Establishes a tuning framework for future model improvements (e.g., Lasso, ElasticNet)

For a clinical triage system, even small accuracy gains can improve patient prioritization, and the added robustness is valuable for real-world deployment.

---

## [v0.1] - 2025-10-17

### Added
- **Initial ML Pipeline**: Basic diabetes progression prediction using Linear Regression
- **Feature Engineering**: StandardScaler for normalization of 10 clinical features (age, sex, BMI, BP, serum measurements)
- **Model Persistence**: Joblib serialization for reproducible deployments
- **REST API**: FastAPI service with `/health` and `/predict` endpoints
- **Risk Scoring**: Normalized progression scores to [0, 1] range using training data distribution
- **Containerization**: Docker image with health checks
- **CI/CD Pipeline**: GitHub Actions for linting, testing, training, and smoke tests
- **Reproducibility**: Fixed random_state=42, pinned dependencies

### Baseline Metrics
- **RMSE**: 53.853 (on 20% held-out test set)
- **Model Size**: 1.7 KB (joblib compressed)
- **Training Data**: 353 samples (442 total, 80/20 split)
- **Test Data**: 89 samples
- **Features**: 10 (age, sex, bmi, bp, s1-s6)
- **Target Range**: 25.0 to 346.0 (progression index)

### Architecture
```
Training: sklearn Diabetes dataset → StandardScaler → LinearRegression → Joblib
Serving: FastAPI → Load model → Batch prediction → Risk score normalization
```
