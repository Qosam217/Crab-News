"""Indonesian date and timestamp parsing utility."""

import re
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")

MONTH_MAP = {
    "januari": 1, "jan": 1,
    "februari": 2, "feb": 2,
    "maret": 3, "mar": 3,
    "april": 4, "apr": 4,
    "mei": 5,
    "juni": 6, "jun": 6,
    "juli": 7, "jul": 7,
    "agustus": 8, "agt": 8, "agu": 8, "agust": 8,
    "september": 9, "sep": 9, "sept": 9,
    "oktober": 10, "okt": 10,
    "november": 11, "nov": 11,
    "desember": 12, "des": 12,
}

INDONESIAN_DAYS = (
    "senin", "selasa", "rabu", "kamis", "jumat", "jum'at", "sabtu", "minggu"
)


def parse_date_from_url(url: str) -> Optional[datetime]:
    """Attempts to extract publication datetime from known Indonesian news URL patterns.
    
    Supports:
    - CNN Indonesia: /YYYYMMDDHHMMSS- (e.g. /20261018141338-14-1416721/)
    - Kompas: /read/YYYY/MM/DD/HHMMSS (e.g. /read/2026/10/18/153534278/)
    """
    if not url:
        return None

    # CNN Indonesia pattern: /YYYYMMDDHHMMSS-
    cnn_match = re.search(r"/(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})-", url)
    if cnn_match:
        try:
            year, month, day, hour, minute, second = map(int, cnn_match.groups())
            return datetime(year, month, day, hour, minute, second, tzinfo=JAKARTA_TZ)
        except ValueError:
            pass

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
    - Relative time: "5 menit lalu", "2 jam yang lalu", "1 hari lalu", "kemarin"
    - Absolute format: "Minggu, 18 Okt 2026 14:47 WIB", "18 Oktober 2026", "18/10/2026, 15:35 WIB"
    - HTML comment timestamp: "<!--2026-10-18 17:36:38-->"
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

    # 2. Extract HTML comment timestamp if present (e.g. CNN Indonesia <!--2026-10-18 17:36:38-->)
    comment_match = re.search(r"<!--\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*-->", cleaned)
    if comment_match:
        try:
            dt = datetime.fromisoformat(comment_match.group(1))
            return dt.replace(tzinfo=JAKARTA_TZ)
        except ValueError:
            pass

    # Clean characters
    cleaned = re.sub(r"<!--.*?-->", "", cleaned)
    cleaned = cleaned.replace("", "").strip()

    lower = cleaned.lower()

    # 3. Relative time expressions
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
