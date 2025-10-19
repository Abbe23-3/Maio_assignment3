from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Any


class BaseModel(ABC):
    """Base class for diabetes triage models."""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.is_trained = False
    
    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Train the model."""
        pass
    
    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        pass
    
    def preprocess(self, X: pd.DataFrame) -> pd.DataFrame:
        """Preprocess input data."""
        if not self.is_trained or self.scaler is None:
            raise ValueError("Model not trained")

        return pd.DataFrame(
            self.scaler.transform(X),
            columns=X.columns,
            index=X.index
        )
