"""Indonesian date and timestamp parsing utility."""

import json
import re
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")

MONTH_MAP = {
    "januari": 1, "jan": 1,
    "februari": 2, "feb": 2,
    "maret": 3, "mar": 3,
    "april": 4, "apr": 4,
    "mei": 5, "may": 5,
    "juni": 6, "jun": 6,
    "juli": 7, "jul": 7,
    "agustus": 8, "agt": 8, "agu": 8, "agust": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "oktober": 10, "okt": 10, "oct": 10,
    "november": 11, "nov": 11,
    "desember": 12, "des": 12, "dec": 12,
}

INDONESIAN_DAYS = (
    "senin", "selasa", "rabu", "kamis", "jumat", "jum'at", "sabtu", "minggu"
)


def parse_date_from_url(url: str) -> Optional[datetime]:
    """Attempts to extract publication datetime from known Indonesian news URL patterns.
    
    Supports:
    - Kompas: /read/YYYY/MM/DD/HHMMSS (e.g. /read/2026/10/18/153534278/)
    - Generic date pattern: /YYYY/MM/DD/
    
    Note:
    - CNN Indonesia / Detik URLs (/YYYYMMDDHHMMSS-) are intentionally excluded because
      the timestamp in the slug reflects CMS draft / planning creation time rather than
      the actual publication time.
    """
    if not url:
        return None

    # Kompas pattern: /read/YYYY/MM/DD/HHMMSS
    kompas_match = re.search(r"/read/(\d{4})/(\d{2})/(\d{2})/(\d{2})(\d{2})(\d{2})?", url)
    if kompas_match:
        try:
            groups = kompas_match.groups()
            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
            hour = int(groups[3])
            minute = int(groups[4])
            second = int(groups[5]) if groups[5] is not None else 0
            return datetime(year, month, day, hour, minute, second, tzinfo=JAKARTA_TZ)
        except ValueError:
            pass

    # Generic date pattern in URL: /YYYY/MM/DD/
    generic_match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
    if generic_match:
        try:
            year, month, day = map(int, generic_match.groups())
            return datetime(year, month, day, 0, 0, 0, tzinfo=JAKARTA_TZ)
        except ValueError:
            pass

    return None


def parse_indonesian_date(
    text: Optional[str],
    reference_time: Optional[datetime] = None,
) -> Optional[datetime]:
    """Parses various Indonesian date formats into a timezone-aware datetime (Asia/Jakarta).
    
    Supports:
    - Unix timestamp string: "1792309638"
    - Relative time: "5 menit lalu", "2 jam yang lalu", "1 hari lalu", "2 minggu yang lalu", "kemarin"
    - Absolute format: "Minggu, 18 Okt 2026 14:47 WIB", "18 Oktober 2026", "18/10/2026, 15:35 WIB"
    """
    if not text:
        return None

    cleaned = text.strip()
    if not cleaned:
        return None

    ref = reference_time or datetime.now(JAKARTA_TZ)

    # 1. Unix epoch string
    if cleaned.isdigit() and len(cleaned) >= 10:
        try:
            ts = int(cleaned)
            return datetime.fromtimestamp(ts, tz=JAKARTA_TZ)
        except (ValueError, OverflowError):
            pass

    # Clean comment tags (e.g. server render timestamps)
    cleaned = re.sub(r"<!--.*?-->", "", cleaned)
    cleaned = cleaned.replace("", "").strip()

    lower = cleaned.lower()

    # 2. Relative time expressions
    # Menit lalu
    minute_match = re.search(r"(\d+)\s*menit\s*(?:yang\s*)?lalu", lower)
    if minute_match:
        minutes = int(minute_match.group(1))
        return ref - timedelta(minutes=minutes)

    # Jam lalu
    hour_match = re.search(r"(\d+)\s*jam\s*(?:yang\s*)?lalu", lower)
    if hour_match:
        hours = int(hour_match.group(1))
        return ref - timedelta(hours=hours)

    # Hari lalu / Kemarin
    day_match = re.search(r"(\d+)\s*hari\s*(?:yang\s*)?lalu", lower)
    if day_match:
        days = int(day_match.group(1))
        return ref - timedelta(days=days)

    if "kemarin" in lower:
        return ref - timedelta(days=1)

    # Minggu / Pekan lalu
    week_match = re.search(r"(\d+)\s*(?:minggu|pekan)\s*(?:yang\s*)?lalu", lower)
    if week_match:
        weeks = int(week_match.group(1))
        return ref - timedelta(weeks=weeks)

    # Detik lalu
    sec_match = re.search(r"(\d+)\s*detik\s*(?:yang\s*)?lalu", lower)
    if sec_match:
        seconds = int(sec_match.group(1))
        return ref - timedelta(seconds=seconds)

    # 4. Remove Indonesian day prefix (e.g. "Minggu, 18 Okt 2026")
    for day_name in INDONESIAN_DAYS:
        if lower.startswith(day_name):
            cleaned = re.sub(rf"^{day_name}[\s,]+", "", cleaned, flags=re.IGNORECASE).strip()
            lower = cleaned.lower()
            break

    # Strip timezone suffix (WIB, WITA, WIT)
    cleaned = re.sub(r"\s+(?:WIB|WITA|WIT)$", "", cleaned, flags=re.IGNORECASE).strip()

    # 5. Format: DD/MM/YYYY or DD-MM-YYYY [HH:MM[:SS]]
    slash_match = re.search(
        r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})(?:[,\s]+(\d{1,2}):(\d{2})(?::(\d{2}))?)?",
        cleaned,
    )
    if slash_match:
        try:
            day = int(slash_match.group(1))
            month = int(slash_match.group(2))
            year = int(slash_match.group(3))
            hour = int(slash_match.group(4)) if slash_match.group(4) else 0
            minute = int(slash_match.group(5)) if slash_match.group(5) else 0
            second = int(slash_match.group(6)) if slash_match.group(6) else 0
            return datetime(year, month, day, hour, minute, second, tzinfo=JAKARTA_TZ)
        except ValueError:
            pass

    # 6. Format: DD Month_Name YYYY [HH:MM[:SS]] (e.g. "18 Oktober 2026" or "18 Okt 2026 14:47")
    word_month_match = re.search(
        r"(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})(?:[,\s]+(\d{1,2}):(\d{2})(?::(\d{2}))?)?",
        cleaned,
    )
    if word_month_match:
        day_str, month_str, year_str, hour_str, min_str, sec_str = word_month_match.groups()
        month_num = MONTH_MAP.get(month_str.lower())
        if month_num:
            try:
                day = int(day_str)
                year = int(year_str)
                hour = int(hour_str) if hour_str else 0
                minute = int(min_str) if min_str else 0
                second = int(sec_str) if sec_str else 0
                return datetime(year, month_num, day, hour, minute, second, tzinfo=JAKARTA_TZ)
            except ValueError:
                pass

    # 7. ISO format fallback
    try:
        iso_dt = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
        if iso_dt.tzinfo is None:
            iso_dt = iso_dt.replace(tzinfo=JAKARTA_TZ)
        else:
            iso_dt = iso_dt.astimezone(JAKARTA_TZ)
        return iso_dt
    except (ValueError, TypeError):
        pass

    return None


def extract_article_metadata_date(html: str) -> Optional[datetime]:
    """Extracts publication datetime from article HTML meta tags and JSON-LD structured data.
    
    Supports:
    - Detik / CNN specific meta tags: meta[name='publishdate'], meta[name='createdate'], meta[name='dtk:publishdate']
    - Detik Unix ms meta tag: meta[name='dtk:publishdateunix']
    - Standard OpenGraph / HTML5: meta[property='article:published_time'], meta[name='pubdate']
    - Schema.org JSON-LD: script[type='application/ld+json'] (datePublished)
    - Detail date UI elements: div.detail__date, time, etc.
    """
    if not html:
        return None

    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        return None

    # 1. Detik / CNN specific text meta tags (e.g. '2026/10/18 17:30:00')
    for tag_name in ["publishdate", "createdate", "dtk:publishdate"]:
        tag = soup.find("meta", attrs={"name": tag_name})
        if tag and tag.get("content"):
            val = tag["content"].strip()
            parsed = parse_indonesian_date(val)
            if parsed:
                return parsed
            try:
                dt = datetime.strptime(val, "%Y/%m/%d %H:%M:%S")
                return dt.replace(tzinfo=JAKARTA_TZ)
            except ValueError:
                pass

    # 2. Unix timestamp meta tag (e.g. Detik dtk:publishdateunix: '1792319400000')
    unix_tag = soup.find("meta", attrs={"name": "dtk:publishdateunix"})
    if unix_tag and unix_tag.get("content"):
        val = unix_tag["content"].strip()
        if val.isdigit():
            ts = int(val) / 1000.0 if len(val) >= 13 else int(val)
            try:
                return datetime.fromtimestamp(ts, tz=JAKARTA_TZ)
            except (ValueError, OverflowError):
                pass

    # 3. Standard OpenGraph / HTML5 article published time
    for prop in ["article:published_time", "og:published_time", "pubdate"]:
        tag = soup.find("meta", attrs={"property": prop}) or soup.find("meta", attrs={"name": prop})
        if tag and tag.get("content"):
            val = tag["content"].strip()
            try:
                iso_dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                if iso_dt.tzinfo is None:
                    return iso_dt.replace(tzinfo=JAKARTA_TZ)
                return iso_dt.astimezone(JAKARTA_TZ)
            except (ValueError, TypeError):
                pass

    # 4. Schema.org JSON-LD datePublished
    for s in soup.find_all("script", type="application/ld+json"):
        if s.string:
            try:
                data = json.loads(s.string)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict):
                        # Support nested @graph
                        sub_items = item.get("@graph", [item])
                        for sub in sub_items:
                            if isinstance(sub, dict) and "datePublished" in sub:
                                val = str(sub["datePublished"]).strip()
                                iso_dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                                if iso_dt.tzinfo is None:
                                    return iso_dt.replace(tzinfo=JAKARTA_TZ)
                                return iso_dt.astimezone(JAKARTA_TZ)
            except Exception:
                pass

    # 5. UI elements in page: .detail__date, time
    date_el = soup.select_one(".detail__date, time, .date")
    if date_el:
        parsed = parse_indonesian_date(date_el.get_text(strip=True))
        if parsed:
            return parsed

    return None

