"""Antara News Adapter with Pagination & Date Range Support."""

from datetime import date, datetime
import time
from typing import List, Optional
from bs4 import BeautifulSoup
from .base import BaseSource
from ..extractor.date_parser import parse_indonesian_date
from ..extractor.html import fetch_html_page
from ..extractor.rss import fetch_and_parse_rss
from ..processor.cleaner import clean_text
from ..config import settings
from ..utils.logger import logger


class AntaraSource(BaseSource):
    """Source adapter for Antara News (antaranews.com) via index pagination."""

    INDEX_URL_TEMPLATE = "https://www.antaranews.com/terkini/{page}"

    def discover_articles(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30,
    ) -> List[dict]:
        """Discovers candidate articles from Antara terkini index with pagination and date filter."""
        candidates: List[dict] = []
        seen_urls = set()
        page = 1
        max_pages = 50
        stop_pagination = False

        logger.info(
            f"[{self.source.name}] Discovering articles via index pagination (limit={limit}, range={start_date} to {end_date})"
        )

        while page <= max_pages and not stop_pagination and len(candidates) < limit:
            page_url = self.INDEX_URL_TEMPLATE.format(page=page)
            logger.debug(f"[{self.source.name}] Fetching page {page}: {page_url}")

            html = fetch_html_page(page_url)
            if not html:
                logger.warning(f"[{self.source.name}] Failed to fetch page {page}")
                break

            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select(".card__post")
            if not cards:
                logger.info(f"[{self.source.name}] No articles found on page {page}, stopping pagination.")
                break

            found_on_page = 0
            for card in cards:
                # Find link and title
                link_tag = (
                    card.select_one(".post_title a")
                    or card.select_one("a[href*='/berita/']")
                )
                if not link_tag:
                    continue

                url = link_tag.get("href", "").strip()
                if not url or url in seen_urls:
                    continue

                title = (
                    link_tag.get("title")
                    or link_tag.get_text(strip=True)
                    or ""
                ).strip()

                # Find date element
                date_span = card.select_one(".card__post__author-info span") or card.select_one(".text-secondary")
                date_str = date_span.get_text(strip=True) if date_span else ""
                published_at = parse_indonesian_date(date_str)

                # Check date range and early stopping
                in_range, is_older = self.check_date_range(published_at, start_date, end_date)

                if is_older:
                    logger.info(
                        f"[{self.source.name}] Reached article older than start_date ({published_at}): early stopping pagination."
                    )
                    stop_pagination = True
                    break

                if in_range:
                    seen_urls.add(url)
                    found_on_page += 1

                    # Summary snippet
                    summary_tag = card.select_one(".card__post__content p") or card.select_one("p")
                    summary = summary_tag.get_text(strip=True) if summary_tag else ""

                    candidates.append({
                        "url": url,
                        "title": title,
                        "published_at": published_at,
                        "summary": summary,
                    })

                    if len(candidates) >= limit:
                        break

            logger.debug(f"[{self.source.name}] Page {page}: collected {found_on_page} candidate articles.")
            page += 1
            if not stop_pagination and len(candidates) < limit:
                time.sleep(settings.rate_limit_delay_seconds)

        # Fallback to RSS if pagination returned 0 candidates and no explicit date range was requested
        if not candidates and not start_date and not end_date and self.source.rss_url:
            logger.warning(f"[{self.source.name}] Index pagination yielded 0 articles, falling back to RSS feed.")
            return fetch_and_parse_rss(self.source.rss_url)[:limit]

        logger.info(f"[{self.source.name}] Discovered total {len(candidates)} candidates across {page - 1} pages.")
        return candidates

    def extract_content_from_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        container = soup.select_one(".post-content") or soup.select_one("article")
        if container:
            paragraphs = container.find_all("p")
            text = " ".join(p.get_text() for p in paragraphs)
            return clean_text(text)
        return super().extract_content_from_html(html)
