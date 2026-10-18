from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
from crab_news.extractor.date_parser import (
    parse_indonesian_date,
    parse_date_from_url,
    extract_article_metadata_date,
)

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")


def test_parse_date_from_url():
    # CNN Indonesia is intentionally excluded from URL parsing because slug digits represent draft planning date
    cnn_url = "https://www.cnnindonesia.com/ekonomi/20260904144401-97-1400064/ac-dan-kulkas-lagi-banting-harga"
    assert parse_date_from_url(cnn_url) is None

    kompas_url = "https://regional.kompas.com/read/2026/10/18/153534278/viral-balita-menangis"
    dt_k = parse_date_from_url(kompas_url)
    assert dt_k is not None
    assert dt_k.year == 2026
    assert dt_k.month == 10
    assert dt_k.day == 18
    assert dt_k.hour == 15
    assert dt_k.minute == 35
    assert dt_k.second == 34

    generic_url = "https://example.com/news/2026/10/18/headline"
    dt_g = parse_date_from_url(generic_url)
    assert dt_g is not None
    assert dt_g.year == 2026
    assert dt_g.month == 10
    assert dt_g.day == 18


def test_parse_relative_date():
    ref = datetime(2026, 10, 18, 15, 0, 0, tzinfo=JAKARTA_TZ)
    
    dt = parse_indonesian_date("10 menit lalu", reference_time=ref)
    assert dt == ref - timedelta(minutes=10)

    dt2 = parse_indonesian_date("2 jam yang lalu", reference_time=ref)
    assert dt2 == ref - timedelta(hours=2)

    dt3 = parse_indonesian_date("kemarin", reference_time=ref)
    assert dt3.date() == date(2026, 10, 17)

    dt4 = parse_indonesian_date("1 minggu yang lalu", reference_time=ref)
    assert dt4 == ref - timedelta(weeks=1)

    dt5 = parse_indonesian_date("2 pekan yang lalu", reference_time=ref)
    assert dt5 == ref - timedelta(weeks=2)


def test_parse_absolute_date():
    dt = parse_indonesian_date("Minggu, 18 Okt 2026 14:47 WIB")
    assert dt is not None
    assert dt.year == 2026
    assert dt.month == 10
    assert dt.day == 18
    assert dt.hour == 14
    assert dt.minute == 47

    dt2 = parse_indonesian_date("18 Oktober 2026")
    assert dt2 is not None
    assert dt2.year == 2026
    assert dt2.month == 10
    assert dt2.day == 18

    dt3 = parse_indonesian_date("18/10/2026, 15:35 WIB")
    assert dt3 is not None
    assert dt3.year == 2026
    assert dt3.month == 10
    assert dt3.day == 18
    assert dt3.hour == 15
    assert dt3.minute == 35


def test_parse_unix_timestamp():
    dt = parse_indonesian_date("1792309638")
    assert dt is not None
    assert dt.tzinfo == JAKARTA_TZ


def test_extract_article_metadata_date():
    # 1. Detik / CNN publishdate meta tag
    html_meta = '<html><head><meta name="publishdate" content="2026/10/18 17:30:00"></head></html>'
    dt1 = extract_article_metadata_date(html_meta)
    assert dt1 is not None
    assert dt1.year == 2026
    assert dt1.month == 10
    assert dt1.day == 18
    assert dt1.hour == 17
    assert dt1.minute == 30

    # 2. Detik dtk:publishdateunix (ms timestamp)
    html_unix = '<html><head><meta name="dtk:publishdateunix" content="1792319400000"></head></html>'
    dt2 = extract_article_metadata_date(html_unix)
    assert dt2 is not None
    assert dt2.year == 2026
    assert dt2.month == 10
    assert dt2.day == 18

    # 3. JSON-LD datePublished
    html_jsonld = '''
    <html><head>
    <script type="application/ld+json">
    {"@context": "https://schema.org", "@type": "NewsArticle", "datePublished": "2026-10-18T17:30:00+07:00"}
    </script>
    </head></html>
    '''
    dt3 = extract_article_metadata_date(html_jsonld)
    assert dt3 is not None
    assert dt3.year == 2026
    assert dt3.month == 10
    assert dt3.day == 18
    assert dt3.hour == 17
    assert dt3.minute == 30

    # 4. Detail date UI element
    html_ui = '<html><body><div class="detail__date">Minggu, 18 Okt 2026 17:30 WIB</div></body></html>'
    dt4 = extract_article_metadata_date(html_ui)
    assert dt4 is not None
    assert dt4.year == 2026
    assert dt4.month == 10
    assert dt4.day == 18

