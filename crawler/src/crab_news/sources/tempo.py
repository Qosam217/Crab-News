from datetime import date
from typing import List, Optional
from bs4 import BeautifulSoup
from .base import BaseSource
from ..extractor.rss import fetch_and_parse_rss
from ..processor.cleaner import clean_text


class TempoSource(BaseSource):
    """Source adapter for Tempo (tempo.co)."""

    def discover_articles(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30,
    ) -> List[dict]:
        rss_url = self.source.rss_url or "https://rss.tempo.co/nasional"
        items = fetch_and_parse_rss(rss_url)
        if start_date or end_date:
            filtered = []
            for item in items:
                pub = item.get("published_at")
                in_range, _ = self.check_date_range(pub, start_date, end_date)
                if in_range:
                    filtered.append(item)
            return filtered[:limit]
        return items[:limit]


    def extract_content_from_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        container = soup.select_one(".detail-in") or soup.select_one("#isi") or soup.select_one("article")
        if container:
            paragraphs = container.find_all("p")
            text = " ".join(p.get_text() for p in paragraphs)
            return clean_text(text)
        return super().extract_content_from_html(html)
