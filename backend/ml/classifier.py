"""Loads the trained model from disk and runs real inference."""
import logging
from pathlib import Path

import joblib
import numpy as np

logger = logging.getLogger(__name__)


class ModelNotReadyError(RuntimeError):
    """Raised when classification is requested but no model is loaded."""


class DocumentClassifier:
    def __init__(self, model_path: Path):
        self.model_path = model_path
        self.pipeline = None
        self.labels: list[str] = []
        self.metrics: dict = {}

    @property
    def is_ready(self) -> bool:
        return self.pipeline is not None

    def load(self) -> bool:
        if not self.model_path.exists():
            logger.warning("No model file at %s. Run: python -m ml.train", self.model_path)
            return False
        try:
            bundle = joblib.load(self.model_path)
            self.pipeline = bundle["pipeline"]
            self.labels = list(bundle["labels"])
            self.metrics = bundle.get("metrics", {})
            logger.info("Model loaded with categories: %s", self.labels)
            return True
        except Exception:  # e.g. scikit-learn version mismatch
            logger.exception("Could not load model. Re-train it with: python -m ml.train")
            self.pipeline = None
            return False

    def predict(self, text: str) -> dict:
        if not self.is_ready:
            raise ModelNotReadyError("The model is not available. Train it with: python -m ml.train")
        probabilities = self.pipeline.predict_proba([text])[0]
        order = np.argsort(probabilities)[::-1]
        ranked = [
            {"category": str(self.pipeline.classes_[i]), "probability": round(float(probabilities[i]), 4)}
            for i in order
        ]
        return {"category": ranked[0]["category"], "confidence": ranked[0]["probability"], "probabilities": ranked}
