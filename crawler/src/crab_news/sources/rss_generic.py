"""Generic RSS news source adapter."""

from typing import List
from .base import BaseSource
from ..extractor.rss import fetch_and_parse_rss


class GenericRSSSource(BaseSource):
    """Generic adapter for standard RSS 2.0 / Atom news feeds."""

    def discover_articles(self) -> List[dict]:
        if not self.source.rss_url:
            return []
        return fetch_and_parse_rss(self.source.rss_url)
