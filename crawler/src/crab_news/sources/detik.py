"""Detik News Adapter."""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseSource
from ..extractor.rss import fetch_and_parse_rss
from ..processor.cleaner import clean_text


class DetikSource(BaseSource):
    """Source adapter for Detik (detik.com)."""

    def discover_articles(self) -> List[dict]:
        rss_url = self.source.rss_url or "https://rss.detik.com/index.php/detikcom"
        return fetch_and_parse_rss(rss_url)

    def extract_content_from_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        container = soup.select_one(".detail__body-text") or soup.select_one(".itp_bodycontent")
        if container:
            paragraphs = container.find_all("p")
            text = " ".join(p.get_text() for p in paragraphs)
            return clean_text(text)
        return super().extract_content_from_html(html)
