"""Application settings, read from environment variables (see .env.example)."""
import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional at runtime
    pass

BASE_DIR = Path(__file__).resolve().parent.parent


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return default


def _get_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]


@dataclass(frozen=True)
class Settings:
    database_path: Path = Path(os.getenv("DATABASE_PATH", BASE_DIR / "data" / "documents.db"))
    model_path: Path = Path(os.getenv("MODEL_PATH", BASE_DIR / "ml" / "artifacts" / "model.joblib"))
    dataset_path: Path = Path(os.getenv("DATASET_PATH", BASE_DIR / "dataset" / "training_data.csv"))
    cors_origins: list[str] = field(default_factory=_get_origins)
    max_upload_mb: int = _get_int("MAX_UPLOAD_MB", 10)
    max_files_per_request: int = _get_int("MAX_FILES_PER_REQUEST", 20)
    # Below this confidence the app shows "Needs Manual Review".
    confidence_threshold: float = _get_float("CONFIDENCE_THRESHOLD", 0.45)
    # Documents with fewer words than this are too short to classify reliably.
    min_words: int = _get_int("MIN_WORDS", 15)
    max_stored_chars: int = _get_int("MAX_STORED_CHARS", 100_000)
    max_classify_chars: int = _get_int("MAX_CLASSIFY_CHARS", 20_000)

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


settings = Settings()
NEEDS_REVIEW_LABEL = "Needs Manual Review"
