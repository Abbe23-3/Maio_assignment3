from src.train import train_and_save
import json
def test_train_and_metrics(tmp_path):
    out = train_and_save(version="test", model_type="linear", out_dir=str(tmp_path), random_state=42)
    assert "rmse" in out
    metrics_file = tmp_path / "metrics_test.json"
    assert metrics_file.exists()
    data = json.loads(metrics_file.read_text())
    assert data["version"] == "test"