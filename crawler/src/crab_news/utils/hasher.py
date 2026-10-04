"""Hash utilities for article content deduplication."""

import hashlib
import re


def compute_content_hash(text: str) -> str:
    """Computes a standardized SHA-256 hash of normalized text for deduplication.

    Normalizes whitespace and converts text to lowercase before hashing so minor formatting
    differences don't prevent duplicate detection.
    """
    if not text:
        return ""
    # Strip whitespace and lowercase
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
