"""Runs the model and decides whether the result is reliable enough to show."""
from dataclasses import dataclass

from ml.classifier import DocumentClassifier
from utils.config import settings
from utils.files import count_words

classifier = DocumentClassifier(settings.model_path)


@dataclass
class ClassificationResult:
    category: str
    confidence: float
    needs_review: bool
    review_reason: str | None
    probabilities: list[dict]


def classify_text(text: str) -> ClassificationResult:
    sample = text[: settings.max_classify_chars]
    prediction = classifier.predict(sample)

    reason = None
    if count_words(text) < settings.min_words:
        reason = f"The document has fewer than {settings.min_words} words, which is too short to classify reliably."
    elif prediction["confidence"] < settings.confidence_threshold:
        reason = (
            f"Model confidence ({prediction['confidence']:.0%}) is below the "
            f"{settings.confidence_threshold:.0%} threshold."
        )
    return ClassificationResult(
        category=prediction["category"],
        confidence=prediction["confidence"],
        needs_review=reason is not None,
        review_reason=reason,
        probabilities=prediction["probabilities"],
    )
