"""RSS Feed extraction and parsing utilities."""

from datetime import datetime
import time
from typing import List, Dict, Any, Optional
import feedparser
import requests
from ..config import settings
from ..utils.logger import logger
from ..utils.url_helper import normalize_url


def parse_feed_date(entry: Dict[str, Any]) -> Optional[datetime]:
    """Parses published date from RSS feed entry to a Python datetime object."""
    # Check published_parsed or updated_parsed
    time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if time_struct:
        try:
            return datetime.fromtimestamp(time.mktime(time_struct))
        except Exception:
            pass

    return None


def fetch_and_parse_rss(rss_url: str) -> List[Dict[str, Any]]:
    """Fetches an RSS feed using custom user-agent headers and returns parsed entries."""
    if not rss_url:
        return []

    headers = {"User-Agent": settings.user_agent}
    try:
        response = requests.get(
            rss_url,
            headers=headers,
            timeout=settings.request_timeout_seconds,
        )
        response.raise_for_status()

        feed = feedparser.parse(response.content)
        entries = []
        for entry in feed.entries:
            link = getattr(entry, "link", "")
            title = getattr(entry, "title", "")
            summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            author = getattr(entry, "author", None)
            pub_date = parse_feed_date(entry)

            if link and title:
                entries.append({
                    "url": normalize_url(link),
                    "title": title.strip(),
                    "summary": summary.strip(),
                    "author": author.strip() if author else None,
                    "published_at": pub_date,
                    "raw_entry": entry,
                })
        return entries
    except Exception as e:
        logger.error(f"Failed to fetch/parse RSS from {rss_url}: {e}")
        return []
