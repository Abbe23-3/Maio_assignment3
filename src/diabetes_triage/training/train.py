import json
import joblib
import logging
from pathlib import Path
from datetime import datetime

from ..data.loader import load_diabetes_data
from ..models.regression import DiabetesProgressionModel, RidgeProgressionModel
from ..utils.config import load_config, get_model_path


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def train_model(config_path: str = "config/config.yaml") -> dict:
    """
    Train the diabetes progression model.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Training results and metrics
    """
    logger = setup_logging()
    logger.info("Starting model training...")
    
    # Load configuration
    config = load_config(config_path)
    
    # Create models directory if it doesn't exist
    models_dir = Path(config["paths"]["models_dir"])
    models_dir.mkdir(exist_ok=True)
    
    # Load data
    logger.info("Loading diabetes dataset...")
    X_train, X_test, y_train, y_test = load_diabetes_data(
        test_size=config["model"]["test_size"],
        random_state=config["model"]["random_state"]
    )
    
    logger.info(f"Training set size: {len(X_train)}")
    logger.info(f"Test set size: {len(X_test)}")
    
    # Initialize and train model based on type
    logger.info("Training model...")
    model_type = config["model"]["type"]

    if model_type == "ridge_regression":
        alpha = config["model"].get("ridge_alpha", 1.0)
        model = RidgeProgressionModel(alpha=alpha)
    else:
        model = DiabetesProgressionModel()

    model.train(X_train, y_train)
    
    # Evaluate model
    logger.info("Evaluating model...")
    metrics = model.evaluate(X_test, y_test)
    logger.info(f"Test RMSE: {metrics['rmse']:.3f}")
    
    # Save model
    model_path = get_model_path(config["model"]["name"], config["paths"]["models_dir"])
    logger.info(f"Saving model to {model_path}")
    joblib.dump(model, model_path)
    
    # Save training metadata
    training_info = {
        "model_name": config["model"]["name"],
        "model_type": config["model"]["type"],
        "training_date": datetime.now().isoformat(),
        "metrics": metrics,
        "config": config
    }
    
    metadata_path = models_dir / f"{config['model']['name']}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(training_info, f, indent=2)
    
    logger.info("Training completed successfully!")
    return training_info


def main(config_path: str = "config/config.yaml"):
    """Main entry point for training script."""
    try:
        results = train_model(config_path=config_path)
        print(f"Training completed. RMSE: {results['metrics']['rmse']:.3f}")
    except Exception as e:
        print(f"Training failed: {e}")
        raise


if __name__ == "__main__":
    main()
