from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_predict_schema():
    sample = {
        "age": 0.0380759064334241,
        "sex": 0.0506801187398187,
        "bmi": 0.0616962065186836,
        "bp": 0.0218723549949558,
        "s1": -0.0442234984244464,
        "s2": -0.0348207628376986,
        "s3": -0.0434008456520269,
        "s4": -0.00259226199818282,
        "s5": 0.0199084208761004,
        "s6": -0.0176461251598052,
        "id": "test1",
    }
    r = client.post("/predict", json=[sample])
    assert r.status_code == 200
    res = r.json()
    assert isinstance(res, list) and len(res) == 1
    assert "progression" in res[0] and "risk_score" in res[0]
