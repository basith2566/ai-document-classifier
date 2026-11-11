"""Small helpers for validating uploaded files."""
from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def safe_name(filename: str) -> str:
    """Keep only the base name (never trust paths sent by the browser)."""
    return Path(filename.replace("\\", "/")).name or "unnamed"


def count_words(text: str) -> int:
    return len(text.split())
