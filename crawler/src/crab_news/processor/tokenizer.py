"""Word tokenizer with filtering for Indonesian text."""

import re
from typing import List
from .cleaner import clean_text
from .stopwords import is_stopword


def tokenize(text: str, min_length: int = 3, filter_stopwords: bool = True) -> List[str]:
    """Tokenizes text into cleaned lowercase words.

    Args:
        text: The raw text string.
        min_length: Minimum word length to retain (defaults to 3).
        filter_stopwords: Whether to remove Indonesian stopwords.

    Returns:
        List of valid word tokens.
    """
    if not text:
        return []

    cleaned = clean_text(text)
    # Extract words containing only alphabetical characters and valid Indonesian hyphenated words (e.g. undang-undang)
    raw_tokens = re.findall(r"\b[a-zA-Z]+(?:-[a-zA-Z]+)?\b", cleaned.lower())

    tokens = []
    for token in raw_tokens:
        # Strip trailing/leading hyphens
        token = token.strip("-")

        # Skip short words and single characters
        if len(token) < min_length:
            continue

        # Skip stopwords if enabled
        if filter_stopwords and is_stopword(token):
            continue

        tokens.append(token)

    return tokens
