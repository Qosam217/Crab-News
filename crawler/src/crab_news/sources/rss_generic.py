"""Generic RSS news source adapter."""

from datetime import date
from typing import List, Optional
from .base import BaseSource
from ..extractor.rss import fetch_and_parse_rss


class GenericRSSSource(BaseSource):
    """Generic adapter for standard RSS 2.0 / Atom news feeds."""

    def discover_articles(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30,
    ) -> List[dict]:
        if not self.source.rss_url:
            return []
        items = fetch_and_parse_rss(self.source.rss_url)
        if start_date or end_date:
            filtered = []
            for item in items:
                pub = item.get("published_at")
                in_range, _ = self.check_date_range(pub, start_date, end_date)
                if in_range:
                    filtered.append(item)
            return filtered[:limit]
        return items[:limit]

