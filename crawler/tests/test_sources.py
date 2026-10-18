from datetime import date, datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo
from crab_news.database.models import SourceModel
from crab_news.sources.antara import AntaraSource
from crab_news.sources.cnn_indonesia import CNNIndonesiaSource
from crab_news.sources.detik import DetikSource
from crab_news.sources.kompas import KompasSource

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")


MOCK_ANTARA_PAGE = """
<div class="card__post">
  <div class="post_title">
    <a href="https://www.antaranews.com/berita/1000001/berita-terbaru-1" title="Berita Terbaru 1">Berita Terbaru 1</a>
  </div>
  <div class="card__post__author-info"><span>10 menit lalu</span></div>
</div>
<div class="card__post">
  <div class="post_title">
    <a href="https://www.antaranews.com/berita/1000002/berita-lama-2" title="Berita Lama 2">Berita Lama 2</a>
  </div>
  <div class="card__post__author-info"><span>17 Oktober 2026</span></div>
</div>
"""

MOCK_CNN_PAGE = """
<article>
  <a href="https://www.cnnindonesia.com/nasional/20261018150000-14-10001/berita-cnn-1">
    <h2>Berita CNN 1</h2>
  </a>
</article>
<article>
  <a href="https://www.cnnindonesia.com/nasional/20261017120000-14-10002/berita-cnn-lama">
    <h2>Berita CNN Lama</h2>
  </a>
</article>
"""

MOCK_DETIK_PAGE = """
<article>
  <h3 class="media__title">
    <a href="https://news.detik.com/berita/d-10001/berita-detik-1">Berita Detik 1</a>
  </h3>
  <div class="media__date">
    <span d-time="1792309638" title="Minggu, 18 Okt 2026 14:47 WIB">2 jam yang lalu</span>
  </div>
</article>
<article>
  <h3 class="media__title">
    <a href="https://news.detik.com/berita/d-10002/berita-detik-lama">Berita Detik Lama</a>
  </h3>
  <div class="media__date">
    <span title="Sabtu, 17 Okt 2026 10:00 WIB">17 Okt 2026</span>
  </div>
</article>
"""

MOCK_KOMPAS_PAGE = """
<div class="articleItem">
  <a href="https://nasional.kompas.com/read/2026/10/18/15000000/berita-kompas-1">
    <h2 class="articleTitle">Berita Kompas 1</h2>
    <div class="articlePost-date">18 Oktober 2026</div>
  </a>
</div>
<div class="articleItem">
  <a href="https://nasional.kompas.com/read/2026/10/17/10000000/berita-kompas-lama">
    <h2 class="articleTitle">Berita Kompas Lama</h2>
    <div class="articlePost-date">17 Oktober 2026</div>
  </a>
</div>
"""


def test_antara_pagination_and_date_filter():
    source_model = SourceModel(name="Antara", slug="antara", domain="antaranews.com", website_url="https://antaranews.com")
    adapter = AntaraSource(source_model)

    with patch("crab_news.sources.antara.fetch_html_page") as mock_fetch:
        mock_fetch.return_value = MOCK_ANTARA_PAGE
        
        # Test 1: Only today's articles (2026-10-18)
        results = adapter.discover_articles(
            start_date=date(2026, 10, 18),
            end_date=date(2026, 10, 18),
            limit=10,
        )
        assert len(results) == 1
        assert results[0]["title"] == "Berita Terbaru 1"


def test_cnn_date_range_discovery():
    source_model = SourceModel(name="CNN", slug="cnn-indonesia", domain="cnnindonesia.com", website_url="https://cnnindonesia.com")
    adapter = CNNIndonesiaSource(source_model)

    def fake_fetch(url: str):
        if "date=2026/10/18" in url and "page=1" in url:
            return MOCK_CNN_PAGE
        return ""

    with patch("crab_news.sources.cnn_indonesia.fetch_html_page", side_effect=fake_fetch):
        results = adapter.discover_articles(
            start_date=date(2026, 10, 18),
            end_date=date(2026, 10, 18),
            limit=10,
        )
        assert len(results) == 2
        assert "Berita CNN 1" in results[0]["title"]
        assert results[0]["published_at"].year == 2026
        assert results[0]["published_at"].month == 10
        assert results[0]["published_at"].day == 18


def test_cnn_extract_article_with_metadata_date():
    source_model = SourceModel(name="CNN", slug="cnn-indonesia", domain="cnnindonesia.com", website_url="https://cnnindonesia.com")
    adapter = CNNIndonesiaSource(source_model)

    mock_article_html = """
    <html>
    <head>
      <meta name="publishdate" content="2026/10/18 17:30:00">
    </head>
    <body>
      <div class="detail-text">
        <p>Isi berita Transmart Full Day Sale diskon besar-besaran.</p>
      </div>
    </body>
    </html>
    """
    item = {
        # URL slug looks like 2026-09-04 (draft/planning timestamp)
        "url": "https://www.cnnindonesia.com/ekonomi/20260904144401-97-1400064/ac-dan-kulkas-lagi-banting-harga",
        "title": "AC dan Kulkas Lagi Banting Harga",
        "published_at": None,
    }

    with patch.object(adapter, "fetch_article_html", return_value=mock_article_html):
        extracted = adapter.extract_article(item)
        assert extracted is not None
        assert extracted.title == "AC dan Kulkas Lagi Banting Harga"
        # Must extract actual publish date from metadata, NOT draft date from URL
        assert extracted.published_at is not None
        assert extracted.published_at.year == 2026
        assert extracted.published_at.month == 10
        assert extracted.published_at.day == 18
        assert extracted.published_at.hour == 17
        assert extracted.published_at.minute == 30
        assert "diskon besar-besaran" in extracted.content


def test_detik_date_extraction_and_filter():
    source_model = SourceModel(name="Detik", slug="detik", domain="detik.com", website_url="https://detik.com")
    adapter = DetikSource(source_model)

    with patch("crab_news.sources.detik.fetch_html_page") as mock_fetch:
        mock_fetch.return_value = MOCK_DETIK_PAGE

        results = adapter.discover_articles(
            start_date=date(2026, 10, 18),
            end_date=date(2026, 10, 18),
            limit=10,
        )
        assert len(results) == 1
        assert results[0]["title"] == "Berita Detik 1"


def test_kompas_date_extraction_and_filter():
    source_model = SourceModel(name="Kompas", slug="kompas", domain="kompas.com", website_url="https://kompas.com")
    adapter = KompasSource(source_model)

    with patch("crab_news.sources.kompas.fetch_html_page") as mock_fetch:
        mock_fetch.return_value = MOCK_KOMPAS_PAGE

        results = adapter.discover_articles(
            start_date=date(2026, 10, 18),
            end_date=date(2026, 10, 18),
            limit=10,
        )
        assert len(results) == 1
        assert results[0]["title"] == "Berita Kompas 1"
        assert results[0]["published_at"].day == 18


def test_tempo_rss_fallback_when_blocked():
    from crab_news.sources.tempo import TempoSource
    source_model = SourceModel(name="Tempo", slug="tempo", domain="tempo.co", website_url="https://tempo.co", rss_url="https://rss.tempo.co/nasional")
    adapter = TempoSource(source_model)

    # Simulate fetch_html_page returning None (403 Cloudflare challenge)
    with patch("crab_news.sources.tempo.fetch_html_page") as mock_fetch, \
         patch("crab_news.sources.tempo.fetch_and_parse_rss") as mock_rss:
        mock_fetch.return_value = None
        mock_rss.return_value = [
            {
                "url": "https://nasional.tempo.co/read/1/tempo-berita-1",
                "title": "Berita Tempo 1",
                "published_at": datetime(2026, 10, 18, 10, 0, 0, tzinfo=JAKARTA_TZ),
                "summary": "Ringkasan berita tempo 1",
            },
            {
                "url": "https://nasional.tempo.co/read/2/tempo-berita-lama",
                "title": "Berita Tempo Lama",
                "published_at": datetime(2026, 10, 10, 10, 0, 0, tzinfo=JAKARTA_TZ),
                "summary": "Ringkasan berita tempo lama",
            },
        ]

        results = adapter.discover_articles(
            start_date=date(2026, 10, 18),
            end_date=date(2026, 10, 18),
            limit=10,
        )
        assert len(results) == 1
        assert results[0]["title"] == "Berita Tempo 1"
        assert results[0]["published_at"].day == 18

