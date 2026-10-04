"""Base Source Adapter Interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
import time
from ..database.models import SourceModel
from ..extractor.article import ExtractedArticle
from ..extractor.rss import fetch_and_parse_rss
from ..extractor.html import fetch_html_page, extract_generic_article_body
from ..processor.cleaner import clean_text
from ..utils.hasher import compute_content_hash
from ..utils.logger import logger
from ..config import settings


class BaseSource(ABC):
    """Abstract base class for all news source adapters."""

    def __init__(self, source_model: SourceModel):
        self.source = source_model

    @abstractmethod
    def discover_articles(self) -> List[dict]:
        """Discovers candidate articles from RSS feed or index page.

        Returns a list of dicts with at least: {"url": str, "title": str, "published_at": datetime, ...}
        """
        pass

    def fetch_article_html(self, url: str) -> Optional[str]:
        """Fetches raw HTML content of an article page."""
        return fetch_html_page(url)

    def extract_article(self, item: dict) -> Optional[ExtractedArticle]:
        """Extracts article content and metadata from discovered item dict and web page."""
        url = item.get("url", "")
        title = item.get("title", "")
        published_at = item.get("published_at")
        author = item.get("author")

        # Fetch full page HTML to extract full article text
        html = self.fetch_article_html(url)
        content = ""
        if html:
            content = self.extract_content_from_html(html)

        # Fallback to summary from RSS if HTML extraction returned empty
        if not content and "summary" in item:
            content = clean_text(item["summary"])

        if not content:
            logger.warning(f"Failed to extract content for article: {url}")
            return None

        content_hash = compute_content_hash(f"{title} {content}")

        return ExtractedArticle(
            url=url,
            title=title,
            content=content,
            author=author,
            published_at=published_at,
            source_id=str(self.source.id) if self.source.id else None,
            content_hash=content_hash,
        )

    def extract_content_from_html(self, html: str) -> str:
        """Default HTML content extraction fallback. Subclasses can override with specific selectors."""
        return extract_generic_article_body(html)
