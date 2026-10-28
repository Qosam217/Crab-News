"""JawaPos News Adapter with GraphQL Index Pagination & Date Range Support."""

from datetime import date, datetime, timedelta
import json
import time
from typing import List, Optional
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup
from .base import BaseSource
from ..extractor.date_parser import parse_indonesian_date
from ..extractor.html import fetch_html_page
from ..processor.cleaner import clean_text
from ..config import settings
from ..utils.logger import logger

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")


class JawaPosSource(BaseSource):
    """Source adapter for JawaPos (jawapos.com) using its GraphQL API for index & date filtering."""

    GRAPHQL_URL = "https://api.jawapos.com/api-jp-graphql"

    SEARCH_QUERY = """
    query SearchArticles($filter: SearchArticleFilter, $first: Int, $page: Int) {
      searchArticle(filter: $filter, first: $first, page: $page) {
        paginatorInfo {
          hasMorePages
        }
        data {
          id
          article_id
          title
          slug
          published_at
          authors {
            name
          }
          category {
            name
            slug
          }
        }
      }
    }
    """

    def discover_articles(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30,
    ) -> List[dict]:
        """Discovers candidate articles from JawaPos GraphQL API with date filtering and pagination."""
        candidates: List[dict] = []
        seen_urls = set()

        logger.info(
            f"[{self.source.name}] Discovering articles via GraphQL API (limit={limit}, range={start_date} to {end_date})"
        )

        now_date = datetime.now(JAKARTA_TZ).date()
        effective_end = end_date or now_date
        effective_start = start_date or (effective_end - timedelta(days=7))

        current_day = effective_end
        while current_day >= effective_start and len(candidates) < limit:
            date_str = current_day.strftime("%Y-%m-%d")
            page = 1
            max_pages_per_day = 20

            logger.debug(f"[{self.source.name}] Querying date {date_str}...")

            while page <= max_pages_per_day and len(candidates) < limit:
                payload = {
                    "query": self.SEARCH_QUERY,
                    "variables": {
                        "filter": {
                            "publisherId": "1",
                            "dateStart": f"{date_str} 00:00:00",
                            "dateEnd": f"{date_str} 23:59:59",
                        },
                        "first": 20,
                        "page": page,
                    },
                }

                headers = {
                    "User-Agent": settings.user_agent,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }

                try:
                    response = requests.post(
                        self.GRAPHQL_URL,
                        json=payload,
                        headers=headers,
                        timeout=settings.request_timeout_seconds,
                    )
                    response.raise_for_status()
                    res_json = response.json()
                except Exception as e:
                    logger.warning(
                        f"[{self.source.name}] Failed GraphQL query for date {date_str} page {page}: {e}"
                    )
                    break

                search_res = res_json.get("data", {}).get("searchArticle", {})
                articles = search_res.get("data", [])
                paginator = search_res.get("paginatorInfo", {})
                has_more = paginator.get("hasMorePages", False)

                if not articles:
                    logger.debug(f"[{self.source.name}] No articles returned for date {date_str} page {page}.")
                    break

                found_on_page = 0
                for item in articles:
                    slug = item.get("slug")
                    art_id = item.get("article_id") or item.get("id")
                    title = item.get("title", "").strip()
                    if not slug or not art_id or not title:
                        continue

                    cat_data = item.get("category") or {}
                    cat_slug = cat_data.get("slug") or "berita"
                    url = f"https://www.jawapos.com/{cat_slug}/{art_id}/{slug}"

                    if url in seen_urls:
                        continue

                    published_str = item.get("published_at")
                    published_at = parse_indonesian_date(published_str)

                    # Author name if present
                    author_name = None
                    authors = item.get("authors") or []
                    if authors and isinstance(authors, list):
                        first_author = authors[0]
                        if isinstance(first_author, dict):
                            author_name = first_author.get("name")

                    seen_urls.add(url)
                    found_on_page += 1
                    candidates.append({
                        "url": url,
                        "title": title,
                        "published_at": published_at,
                        "author": author_name,
                    })

                    if len(candidates) >= limit:
                        break

                logger.debug(
                    f"[{self.source.name}] Date {date_str} page {page}: collected {found_on_page} articles."
                )

                if not has_more or len(candidates) >= limit:
                    break

                page += 1
                time.sleep(settings.rate_limit_delay_seconds)

            current_day -= timedelta(days=1)
            if current_day >= effective_start and len(candidates) < limit:
                time.sleep(settings.rate_limit_delay_seconds)

        logger.info(f"[{self.source.name}] Discovered total {len(candidates)} candidates.")
        return candidates

    def extract_content_from_html(self, html: str) -> str:
        """Extracts article content from JawaPos HTML or Next.js __NEXT_DATA__."""
        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")

        # 1. Try extracting full text from Next.js __NEXT_DATA__
        next_data_script = soup.find("script", id="__NEXT_DATA__")
        if next_data_script and next_data_script.string:
            try:
                data = json.loads(next_data_script.string)
                page_props = data.get("props", {}).get("pageProps", {})
                article_data = page_props.get("article") or page_props.get("initialArticle") or {}
                raw_content = article_data.get("content", "")
                if raw_content:
                    content_soup = BeautifulSoup(raw_content, "html.parser")
                    text = content_soup.get_text(separator=" ")
                    cleaned = clean_text(text)
                    if len(cleaned) > 50:
                        return cleaned
            except Exception as e:
                logger.debug(f"[{self.source.name}] Error parsing __NEXT_DATA__: {e}")

        # 2. Fallback: standard CSS selectors for JawaPos article content
        container = (
            soup.select_one(".content-detail")
            or soup.select_one(".detail-content")
            or soup.select_one(".article-content")
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
