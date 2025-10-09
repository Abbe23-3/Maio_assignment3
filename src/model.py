import joblib
from pathlib import Path

def save_model(pipe, out_path: str):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, out_path)

def load_model(path: str):
    return joblib.load(path)