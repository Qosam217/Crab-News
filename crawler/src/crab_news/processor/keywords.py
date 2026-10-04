"""Article keyword frequency extraction."""

from collections import Counter
from typing import Dict, List
from .tokenizer import tokenize


def extract_keywords_from_text(text: str, top_n: int = 50) -> Dict[str, int]:
    """Extracts top word frequencies from an article text string.

    Args:
        text: Article title and content.
        top_n: Maximum number of distinct words to retain.

    Returns:
        Dictionary mapping words to their frequency in this article.
    """
    tokens = tokenize(text)
    if not tokens:
        return {}

    counter = Counter(tokens)
    return dict(counter.most_common(top_n))


def extract_article_keywords(title: str, content: str, title_weight: int = 3) -> Dict[str, int]:
    """Extracts keyword counts from title and content with weighted importance for title."""
    title_tokens = tokenize(title)
    content_tokens = tokenize(content)

    counter: Counter = Counter()

    # Weight title tokens more heavily as they represent the article topic
    for token in title_tokens:
        counter[token] += title_weight

    for token in content_tokens:
        counter[token] += 1

    return dict(counter)
