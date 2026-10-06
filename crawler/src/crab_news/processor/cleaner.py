"""Text cleaner and normalizer for article content."""

import html
import re
from bs4 import BeautifulSoup


def strip_html(raw_html: str) -> str:
    """Strips HTML tags, scripts, styles, and unescapes HTML entities."""
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")
    # Remove script, style, and comments
    for element in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav"]):
        element.decompose()

    text = soup.get_text(separator=" ")
    text = html.unescape(text)
    # Collapse multiple whitespaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_text(text: str) -> str:
    """Normalizes text by removing URLs, emails, special characters, and excess whitespace."""
    if not text:
        return ""

    # Strip HTML first if present
    if "<" in text and ">" in text:
        text = strip_html(text)

    # Remove URLs (http, https, www)
    text = re.sub(r"https?://\S+|www\.\S+", "", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+", "", text)

    # Remove non-alphanumeric except hyphen and space (keep Indonesian characters)
    text = re.sub(r"[^a-zA-Z0-9\s\-]", " ", text)

    # Collapse multiple hyphens or standalone hyphens
    text = re.sub(r"\s+-\s+", " ", text)
    text = re.sub(r"-{2,}", " ", text)

    # Collapse multiple whitespaces into a single space
    text = re.sub(r"\s+", " ", text).strip()

    return text
