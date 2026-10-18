"""Tempo News Adapter with Pagination & Date Range Support (with Cloudflare fallback)."""

from datetime import date, datetime
import time
from typing import List, Optional
from bs4 import BeautifulSoup
from .base import BaseSource
from ..extractor.date_parser import parse_indonesian_date, parse_date_from_url
from ..extractor.html import fetch_html_page
from ..extractor.rss import fetch_and_parse_rss
from ..processor.cleaner import clean_text
from ..config import settings
from ..utils.logger import logger


class TempoSource(BaseSource):
    """Source adapter for Tempo (tempo.co) via index pagination and RSS fallback."""

    INDEX_URL_TEMPLATE = "https://www.tempo.co/indeks?page={page}"
    FALLBACK_RSS_FEEDS = [
        "https://rss.tempo.co/nasional",
        "https://rss.tempo.co/bisnis",
    ]

    def discover_articles(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30,
    ) -> List[dict]:
        """Discovers candidate articles from Tempo index pagination with RSS fallback."""
        candidates: List[dict] = []
        seen_urls = set()
        page = 1
        max_pages = 50
        stop_pagination = False
        html_blocked = False

        logger.info(
            f"[{self.source.name}] Discovering articles via index pagination (limit={limit}, range={start_date} to {end_date})"
        )

        while page <= max_pages and not stop_pagination and len(candidates) < limit:
            page_url = self.INDEX_URL_TEMPLATE.format(page=page)
            logger.debug(f"[{self.source.name}] Fetching page {page}: {page_url}")

            html = fetch_html_page(page_url)
            if not html:
                # If page 1 fails completely (Cloudflare bot challenge / 403), switch to RSS fallback
                if page == 1:
                    logger.warning(
                        f"[{self.source.name}] Index web page blocked or unreachable, switching to RSS fallback."
                    )
                    html_blocked = True
                break

            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select(".card-box, .wrapper-card, .list-berita, article")
            if not cards:
                if page == 1:
                    logger.warning(
                        f"[{self.source.name}] No article cards found on index page 1, switching to RSS fallback."
                    )
                    html_blocked = True
                break

            found_on_page = 0
            for card in cards:
                link_tag = (
                    card.select_one("a[href*='tempo.co/read/']")
                    or card.select_one("a[href*='/read/']")
                    or card.select_one("a")
                )
                if not link_tag:
                    continue

                url = link_tag.get("href", "").strip()
                if not url or url in seen_urls:
                    continue

                title_tag = (
                    card.select_one(".title a")
                    or card.select_one("h2")
                    or card.select_one("h3")
                )
                title = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
                if not title:
                    continue

                # Date parsing
                published_at = parse_date_from_url(url)
                if not published_at:
                    date_el = card.select_one(".date, span.text-neutral-500, time")
                    raw_date = date_el.get_text(strip=True) if date_el else ""
                    published_at = parse_indonesian_date(raw_date)

                # Date range and early stopping check
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
                    summary_tag = card.select_one("p, .desc")
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

        # Fallback to RSS feeds if HTML index was blocked or yielded 0 articles
        if (html_blocked or not candidates) and (self.source.rss_url or self.FALLBACK_RSS_FEEDS):
            logger.info(f"[{self.source.name}] Discovering articles from RSS feeds fallback...")
            rss_feeds = [self.source.rss_url] if self.source.rss_url else self.FALLBACK_RSS_FEEDS
            rss_candidates: List[dict] = []
            
            for feed_url in rss_feeds:
                if not feed_url:
                    continue
                items = fetch_and_parse_rss(feed_url)
                for item in items:
                    url = item.get("url", "")
                    if not url or url in seen_urls:
                        continue
                    pub = item.get("published_at")
                    in_range, _ = self.check_date_range(pub, start_date, end_date)
                    if in_range:
                        seen_urls.add(url)
                        rss_candidates.append(item)
                        if len(rss_candidates) >= limit:
                            break
                if len(rss_candidates) >= limit:
                    break

            if rss_candidates:
                logger.info(f"[{self.source.name}] Recovered {len(rss_candidates)} candidates from RSS fallback.")
                return rss_candidates[:limit]

        logger.info(f"[{self.source.name}] Discovered total {len(candidates)} candidates.")
        return candidates

    def extract_content_from_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        container = (
            soup.select_one(".detail-in")
            or soup.select_one("#isi")
            or soup.select_one(".detail-konten")
            or soup.select_one("article")
        )
        if container:
            paragraphs = container.find_all("p")
            text = " ".join(p.get_text() for p in paragraphs)
            return clean_text(text)
        return super().extract_content_from_html(html)
