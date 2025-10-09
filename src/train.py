import argparse
import json
from pathlib import Path
from math import sqrt
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from .model import save_model

def train_and_save(version="v0.1", model_type="linear", out_dir="models", test_size=0.2, random_state=42):
    data = load_diabetes(as_frame=True)
    X = data.frame.drop(columns=["target"])
    y = data.frame["target"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    if model_type == "linear":
        pipe = Pipeline([("scaler", StandardScaler()), ("lr", LinearRegression())])
        pipe.fit(X_train, y_train)
    elif model_type == "ridge":
        pipe = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(random_state=random_state))])
        gs = GridSearchCV(pipe, {"ridge__alpha":[0.1,1.0,10.0,100.0]}, cv=5)
        gs.fit(X_train, y_train)
        pipe = gs.best_estimator_
    elif model_type == "rf":
        rf = RandomForestRegressor(n_estimators=200, random_state=random_state)
        pipe = Pipeline([("scaler", StandardScaler()), ("rf", rf)])
        pipe.fit(X_train, y_train)
    else:
        raise ValueError("model_type must be one of ['linear','ridge','rf']")

    preds = pipe.predict(X_test)
    rmse = float(sqrt(mean_squared_error(y_test, preds)))

    # Save model and a small metadata file including train distribution for normalization/risk scoring
    model_path = f"{out_dir}/model_{version}.joblib"
    save_model(pipe, model_path)

    meta = {
        "version": version,
        "model_type": model_type,
        "rmse": rmse,
        "random_state": random_state,
        "y_train_min": float(y_train.min()),
        "y_train_max": float(y_train.max())
    }
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    with open(f"{out_dir}/metrics_{version}.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Saved model to: {model_path}")
    print(json.dumps(meta, indent=2))
    return meta

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="v0.1")
    parser.add_argument("--model", choices=["linear", "ridge", "rf"], default="linear")
    parser.add_argument("--out_dir", default="models")
    parser.add_argument("--test_size", type=float, default=0.2)
    parser.add_argument("--random_state", type=int, default=42)
    args = parser.parse_args()
    train_and_save(version=args.version, model_type=args.model, out_dir=args.out_dir,
                   test_size=args.test_size, random_state=args.random_state)