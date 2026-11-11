"""Text cleaning used for BOTH training and prediction (so they always match)."""
import re

_URL = re.compile(r"https?://\S+|www\.\S+")
_EMAIL = re.compile(r"\S+@\S+\.\S+")
_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
_NON_WORD = re.compile(r"[^a-z\s]")
_SPACES = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Lowercase, replace URLs/emails/numbers with tokens, drop punctuation.

    Replacing numbers with a token keeps the useful signal ("this document
    contains lots of numbers", typical for invoices) without memorising values.
    """
    text = (text or "").lower()
    text = _URL.sub(" urltoken ", text)
    text = _EMAIL.sub(" emailtoken ", text)
    text = _NUMBER.sub(" numtoken ", text)
    text = _NON_WORD.sub(" ", text)
    return _SPACES.sub(" ", text).strip()
