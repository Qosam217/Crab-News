"""CNN Indonesia Adapter with Pagination & Date Range Support."""

from datetime import date, datetime, timedelta
import time
from typing import List, Optional
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
from .base import BaseSource
from ..extractor.article import ExtractedArticle
from ..extractor.date_parser import parse_indonesian_date, extract_article_metadata_date
from ..extractor.html import fetch_html_page
from ..extractor.rss import fetch_and_parse_rss
from ..utils.hasher import compute_content_hash
from ..processor.cleaner import clean_text
from ..config import settings
from ..utils.logger import logger

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")


class CNNIndonesiaSource(BaseSource):
    """Source adapter for CNN Indonesia (cnnindonesia.com) via index pagination."""

    INDEX_URL_TEMPLATE = "https://www.cnnindonesia.com/indeks/2?page={page}"
    INDEX_DATE_URL_TEMPLATE = "https://www.cnnindonesia.com/indeks/2?page={page}&date={date}"

    def discover_articles(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30,
    ) -> List[dict]:
        """Discovers candidate articles from CNN Indonesia index with pagination and date filter."""
        candidates: List[dict] = []
        seen_urls = set()

        logger.info(
            f"[{self.source.name}] Discovering articles via index pagination (limit={limit}, range={start_date} to {end_date})"
        )

        if start_date or end_date:
            candidates = self._discover_with_date_range(start_date, end_date, limit, seen_urls)
        else:
            candidates = self._discover_latest(limit, seen_urls)

        # Fallback to RSS if pagination yielded nothing
        if not candidates and not start_date and not end_date and self.source.rss_url:
            logger.warning(f"[{self.source.name}] Index pagination yielded 0 articles, falling back to RSS.")
            return fetch_and_parse_rss(self.source.rss_url)[:limit]

        logger.info(f"[{self.source.name}] Discovered total {len(candidates)} candidates.")
        return candidates

    def _discover_with_date_range(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        limit: int,
        seen_urls: set,
    ) -> List[dict]:
        candidates: List[dict] = []
        now_date = datetime.now(JAKARTA_TZ).date()
        effective_end = end_date or now_date
        effective_start = start_date or (effective_end - timedelta(days=7))

        current_day = effective_end
        while current_day >= effective_start and len(candidates) < limit:
            date_str = current_day.strftime("%Y/%m/%d")
            page = 1
            max_pages_per_day = 30

            while page <= max_pages_per_day and len(candidates) < limit:
                page_url = self.INDEX_DATE_URL_TEMPLATE.format(page=page, date=date_str)
                logger.debug(f"[{self.source.name}] Fetching date {date_str} page {page}: {page_url}")

                html = fetch_html_page(page_url)
                if not html:
                    logger.warning(f"[{self.source.name}] Failed to fetch page {page} for date {date_str}")
                    break

                soup = BeautifulSoup(html, "html.parser")
                articles = soup.select("article")
                if not articles:
                    break

                found_on_page = 0
                for item in articles:
                    link_tag = item.select_one("a[href]")
                    if not link_tag:
                        continue

                    url = link_tag.get("href", "").strip()
                    if not url or url in seen_urls:
                        continue

                    title_tag = item.select_one("h2") or item.select_one("img[alt]")
                    title = ""
                    if title_tag:
                        title = title_tag.get("alt") if title_tag.name == "img" else title_tag.get_text(strip=True)
                    if not title:
                        title = link_tag.get_text(strip=True)

                    if not title:
                        continue

                    date_span = item.select_one("span.text-cnn_black_light3, .text-xs, time")
                    raw_date = str(date_span) if date_span else ""
                    published_at = parse_indonesian_date(raw_date)
                    if not published_at:
                        published_at = datetime(
                            current_day.year, current_day.month, current_day.day, 12, 0, 0, tzinfo=JAKARTA_TZ
                        )

                    seen_urls.add(url)
                    found_on_page += 1
                    candidates.append({
                        "url": url,
                        "title": title,
                        "published_at": published_at,
                    })

                    if len(candidates) >= limit:
                        break

                page += 1
                if len(candidates) < limit and found_on_page > 0:
                    time.sleep(settings.rate_limit_delay_seconds)

            current_day -= timedelta(days=1)

        return candidates

    def _discover_latest(self, limit: int, seen_urls: set) -> List[dict]:
        candidates: List[dict] = []
        page = 1
        max_pages = 50

        while page <= max_pages and len(candidates) < limit:
            page_url = self.INDEX_URL_TEMPLATE.format(page=page)
            logger.debug(f"[{self.source.name}] Fetching page {page}: {page_url}")

            html = fetch_html_page(page_url)
            if not html:
                logger.warning(f"[{self.source.name}] Failed to fetch page {page}")
                break

            soup = BeautifulSoup(html, "html.parser")
            articles = soup.select("article")
            if not articles:
                logger.info(f"[{self.source.name}] No articles found on page {page}, stopping pagination.")
                break

            found_on_page = 0
            for item in articles:
                link_tag = item.select_one("a[href]")
                if not link_tag:
                    continue

                url = link_tag.get("href", "").strip()
                if not url or url in seen_urls:
                    continue

                title_tag = item.select_one("h2") or item.select_one("img[alt]")
                title = ""
                if title_tag:
                    title = title_tag.get("alt") if title_tag.name == "img" else title_tag.get_text(strip=True)
                if not title:
                    title = link_tag.get_text(strip=True)

                if not title:
                    continue

                date_span = item.select_one("span.text-cnn_black_light3, .text-xs, time")
                raw_date = str(date_span) if date_span else ""
                published_at = parse_indonesian_date(raw_date)

                seen_urls.add(url)
                found_on_page += 1
                candidates.append({
                    "url": url,
                    "title": title,
                    "published_at": published_at,
                })

                if len(candidates) >= limit:
                    break

            page += 1
            if len(candidates) < limit and found_on_page > 0:
                time.sleep(settings.rate_limit_delay_seconds)

        return candidates

    def extract_article(self, item: dict) -> Optional[ExtractedArticle]:
        """Extracts article content and metadata from discovered item dict and web page."""
        url = item.get("url", "")
        title = item.get("title", "")
        published_at = item.get("published_at")
        author = item.get("author")

        html = self.fetch_article_html(url)
        content = ""
        if html:
            # Extract high-precision publish date from HTML metadata (meta tags / JSON-LD)
            meta_date = extract_article_metadata_date(html)
            if meta_date:
                published_at = meta_date
            content = self.extract_content_from_html(html)

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
        soup = BeautifulSoup(html, "html.parser")
        container = soup.select_one(".detail-text") or soup.select_one("#detikdetailtext")
        if container:
            paragraphs = container.find_all("p")
            text = " ".join(p.get_text() for p in paragraphs)
            return clean_text(text)
        return super().extract_content_from_html(html)
