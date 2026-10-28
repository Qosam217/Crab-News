"""IDN Times News Adapter with Index Pagination & Date Range Support."""

from datetime import date, datetime, timedelta
import json
import time
from typing import List, Optional
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
from .base import BaseSource
from ..extractor.date_parser import parse_indonesian_date
from ..extractor.html import fetch_html_page
from ..processor.cleaner import clean_text
from ..config import settings
from ..utils.logger import logger

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")


class IDNTimesSource(BaseSource):
    """Source adapter for IDN Times (idntimes.com) via index pagination and date filter."""

    INDEX_URL_TEMPLATE = "https://www.idntimes.com/index?category=all&date={date}&page={page}"

    def discover_articles(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30,
    ) -> List[dict]:
        """Discovers candidate articles from IDN Times index by paginating per-date."""
        candidates: List[dict] = []
        seen_urls = set()

        logger.info(
            f"[{self.source.name}] Discovering articles via index pagination (limit={limit}, range={start_date} to {end_date})"
        )

        now_date = datetime.now(JAKARTA_TZ).date()
        effective_end = end_date or now_date
        effective_start = start_date or (effective_end - timedelta(days=7))

        current_day = effective_end
        while current_day >= effective_start and len(candidates) < limit:
            date_str = current_day.strftime("%Y-%m-%d")
            page = 1
            max_pages_per_day = 30

            logger.debug(f"[{self.source.name}] Fetching date {date_str}...")

            while page <= max_pages_per_day and len(candidates) < limit:
                page_url = self.INDEX_URL_TEMPLATE.format(date=date_str, page=page)
                logger.debug(f"[{self.source.name}] Fetching page {page}: {page_url}")

                html = fetch_html_page(page_url)
                if not html:
                    logger.warning(f"[{self.source.name}] Failed to fetch page {page} for date {date_str}")
                    break

                soup = BeautifulSoup(html, "html.parser")
                cards = soup.find_all("article")
                if not cards:
                    logger.debug(f"[{self.source.name}] No articles found on page {page} for {date_str}, ending date pagination.")
                    break

                found_on_page = 0
                for card in cards:
                    a_tag = card.find("a", href=True)
                    if not a_tag:
                        continue

                    url = a_tag.get("href", "").strip()
                    if not url or "idntimes.com" not in url or url in seen_urls:
                        continue

                    # Avoid non-article category links
                    if not any(cat in url for cat in ["/news/", "/business/", "/tech/", "/hype/", "/life/", "/health/", "/sport/", "/travel/", "/men/", "/science/", "/opinion/"]):
                        continue

                    title_tag = card.find(["h2", "h3", "h4", "h1"]) or a_tag
                    title = title_tag.get_text(strip=True) if title_tag else ""
                    if not title:
                        continue

                    # Extract date from card span/time or fallback to current_day
                    published_at = None
                    for span in card.find_all(["span", "time"]):
                        txt = span.get_text(strip=True)
                        if txt:
                            parsed = parse_indonesian_date(txt)
                            if parsed:
                                published_at = parsed
                                break

                    if not published_at:
                        published_at = datetime.combine(current_day, datetime.min.time(), tzinfo=JAKARTA_TZ)

                    seen_urls.add(url)
                    found_on_page += 1
                    candidates.append({
                        "url": url,
                        "title": title,
                        "published_at": published_at,
                    })

                    if len(candidates) >= limit:
                        break

                logger.debug(f"[{self.source.name}] Date {date_str} page {page}: collected {found_on_page} articles.")

                if found_on_page == 0:
                    break

                page += 1
                time.sleep(settings.rate_limit_delay_seconds)

            current_day -= timedelta(days=1)
            if current_day >= effective_start and len(candidates) < limit:
                time.sleep(settings.rate_limit_delay_seconds)

        logger.info(f"[{self.source.name}] Discovered total {len(candidates)} candidates.")
        return candidates

    def extract_content_from_html(self, html: str) -> str:
        """Extracts article content from IDN Times HTML using Schema.org JSON-LD or CSS selectors."""
        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")

        # 1. Try Schema.org JSON-LD structured data
        for s in soup.find_all("script", type="application/ld+json"):
            if s.string:
                try:
                    data = json.loads(s.string)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if isinstance(item, dict):
                            sub_items = item.get("@graph", [item])
                            for sub in sub_items:
                                if isinstance(sub, dict) and sub.get("@type") in ["NewsArticle", "Article"]:
                                    article_body = sub.get("articleBody")
                                    if article_body:
                                        cleaned = clean_text(article_body)
                                        if len(cleaned) > 50:
                                            return cleaned
                except Exception as e:
                    logger.debug(f"[{self.source.name}] Error reading JSON-LD: {e}")

        # 2. Fallback: CSS container selectors
        container = (
            soup.select_one(".content")
            or soup.select_one(".article-content")
            or soup.select_one("#article-content")
            or soup.select_one("article")
        )
        if container:
            paragraphs = container.find_all("p")
            if paragraphs:
                text = " ".join(p.get_text() for p in paragraphs)
                cleaned = clean_text(text)
                if len(cleaned) > 50:
                    return cleaned

        return super().extract_content_from_html(html)
