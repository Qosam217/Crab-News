"""HTML web page extraction and article body parser."""

from typing import Optional
import requests
from bs4 import BeautifulSoup
from ..config import settings
from ..processor.cleaner import clean_text
from ..utils.logger import logger


def fetch_html_page(url: str) -> Optional[str]:
    """Fetches HTML page content with configured headers and timeout."""
    headers = {"User-Agent": settings.user_agent}
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=settings.request_timeout_seconds,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.warning(f"Failed to fetch HTML page from {url}: {e}")
        return None


def extract_generic_article_body(html_content: str) -> str:
    """Extracts the main body text from HTML using common news article selectors and fallbacks."""
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav", "aside", "form"]):
        tag.decompose()

    # Try standard article tag first
    article_tag = soup.find("article")
    if article_tag:
        paragraphs = article_tag.find_all("p")
        if paragraphs:
            text = " ".join(p.get_text() for p in paragraphs)
            return clean_text(text)

    # Common Indonesian news body classes/IDs
    content_selectors = [
        ".detail__body-text",       # Detik
        ".read__content",           # Kompas
        ".detail-text",             # CNN Indonesia
        ".post-content",            # Antara
        ".detail-in",               # Tempo
        ".entry-content",
        ".article-content",
        ".content-detail",
        ".article-body",
    ]

    for selector in content_selectors:
        element = soup.select_one(selector)
        if element:
            paragraphs = element.find_all("p")
            if paragraphs:
                text = " ".join(p.get_text() for p in paragraphs)
            else:
                text = element.get_text()
            if len(text.strip()) > 50:
                return clean_text(text)

    # Fallback: aggregate all <p> tags on page
    all_p = soup.find_all("p")
    text = " ".join(p.get_text() for p in all_p)
    return clean_text(text)
