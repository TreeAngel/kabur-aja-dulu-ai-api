"""
Text cleaner utility — normalizes raw CV text before processing.
"""
import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Normalize and clean raw text:
    - Unicode normalization (NFKC)
    - Lowercase
    - Remove special characters except alphanumeric, space, and dot
    - Collapse whitespace
    """
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+\.\S+", " ", text)

    # Keep only letters, digits, spaces, and common punctuation
    text = re.sub(r"[^a-z0-9\s\+\#\.]", " ", text)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text
