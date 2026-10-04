"""CNN Indonesia Adapter."""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseSource
from ..extractor.rss import fetch_and_parse_rss
from ..processor.cleaner import clean_text


class CNNIndonesiaSource(BaseSource):
    """Source adapter for CNN Indonesia (cnnindonesia.com)."""

    def discover_articles(self) -> List[dict]:
        rss_url = self.source.rss_url or "https://www.cnnindonesia.com/nasional/rss"
        return fetch_and_parse_rss(rss_url)

    def extract_content_from_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        container = soup.select_one(".detail-text") or soup.select_one("#detikdetailtext")
        if container:
            paragraphs = container.find_all("p")
            text = " ".join(p.get_text() for p in paragraphs)
            return clean_text(text)
        return super().extract_content_from_html(html)
