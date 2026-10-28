from datetime import date, datetime
from unittest.mock import patch, MagicMock
from zoneinfo import ZoneInfo
from crab_news.database.models import SourceModel
from crab_news.sources import get_source_adapter, SOURCE_REGISTRY
from crab_news.sources.jawapos import JawaPosSource
from crab_news.sources.idntimes import IDNTimesSource
from crab_news.extractor.date_parser import parse_indonesian_date

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")


def test_registry_registration():
    """Verify jawapos and idntimes are properly registered."""
    assert "jawapos" in SOURCE_REGISTRY
    assert SOURCE_REGISTRY["jawapos"] == JawaPosSource
    assert "idntimes" in SOURCE_REGISTRY
    assert SOURCE_REGISTRY["idntimes"] == IDNTimesSource

    jp_model = SourceModel(name="JawaPos", slug="jawapos", domain="jawapos.com", website_url="https://www.jawapos.com")
    adapter = get_source_adapter(jp_model)
    assert isinstance(adapter, JawaPosSource)

    idn_model = SourceModel(name="IDN Times", slug="idntimes", domain="idntimes.com", website_url="https://www.idntimes.com")
    adapter = get_source_adapter(idn_model)
    assert isinstance(adapter, IDNTimesSource)


def test_date_parser_english_abbreviations():
    """Verify parse_indonesian_date handles English month abbreviations like Oct, Aug, Dec."""
    dt = parse_indonesian_date("27 Oct 2026, 23:46 WIB")
    assert dt is not None
    assert dt.year == 2026
    assert dt.month == 10
    assert dt.day == 27
    assert dt.hour == 23
    assert dt.minute == 46

    dt_aug = parse_indonesian_date("15 Aug 2026 10:00")
    assert dt_aug is not None
    assert dt_aug.month == 8


def test_jawapos_discover_via_graphql():
    """Test JawaPosSource discovery using mock GraphQL response."""
    source_model = SourceModel(name="JawaPos", slug="jawapos", domain="jawapos.com", website_url="https://www.jawapos.com")
    adapter = JawaPosSource(source_model)

    mock_gql_response = {
        "data": {
            "searchArticle": {
                "paginatorInfo": {
                    "hasMorePages": False
                },
                "data": [
                    {
                        "id": "uuid-1",
                        "article_id": "261027001",
                        "title": "Berita Olahraga Terbaru",
                        "slug": "berita-olahraga-terbaru",
                        "published_at": "2026-10-27 14:00:00",
                        "authors": [{"name": "Reporter JawaPos"}],
                        "category": {"slug": "sports", "name": "Sports"}
                    },
                    {
                        "id": "uuid-2",
                        "article_id": "261027002",
                        "title": "Berita Nasional Terkini",
                        "slug": "berita-nasional-terkini",
                        "published_at": "2026-10-27 12:00:00",
                        "authors": [{"name": "Antara"}],
                        "category": {"slug": "nasional", "name": "Nasional"}
                    }
                ]
            }
        }
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_gql_response

    with patch("requests.post", return_value=mock_resp) as mock_post:
        candidates = adapter.discover_articles(
            start_date=date(2026, 10, 27),
            end_date=date(2026, 10, 27),
            limit=10
        )

        assert mock_post.called
        assert len(candidates) == 2
        assert candidates[0]["title"] == "Berita Olahraga Terbaru"
        assert candidates[0]["url"] == "https://www.jawapos.com/sports/261027001/berita-olahraga-terbaru"
        assert candidates[0]["author"] == "Reporter JawaPos"
        assert candidates[0]["published_at"].day == 27


def test_jawapos_extract_content_from_next_data():
    """Test JawaPos content extraction from embedded __NEXT_DATA__ script."""
    source_model = SourceModel(name="JawaPos", slug="jawapos", domain="jawapos.com", website_url="https://www.jawapos.com")
    adapter = JawaPosSource(source_model)

    html = """
    <html>
      <body>
        <script id="__NEXT_DATA__" type="application/json">
        {
          "props": {
            "pageProps": {
              "article": {
                "content": "<p>Ini adalah paragraf pertama berita JawaPos yang sangat lengkap dan informatif.</p><p>Dan ini paragraf kedua berita tersebut.</p>"
              }
            }
          }
        }
        </script>
      </body>
    </html>
    """
    content = adapter.extract_content_from_html(html)
    assert "Ini adalah paragraf pertama berita JawaPos" in content
    assert "Dan ini paragraf kedua berita tersebut" in content


def test_idntimes_discover_via_html():
    """Test IDNTimesSource discovery via index HTML cards."""
    source_model = SourceModel(name="IDN Times", slug="idntimes", domain="idntimes.com", website_url="https://www.idntimes.com")
    adapter = IDNTimesSource(source_model)

    mock_html = """
    <html>
      <body>
        <article>
          <a href="https://www.idntimes.com/news/indonesia/berita-idn-1-00-abc-123">
            <h2>Pramono Tegaskan Tiket Ragunan Tak Bisa Gratis</h2>
          </a>
          <span>27 Oct 2026, 23:46 WIB</span>
        </article>
        <article>
          <a href="https://www.idntimes.com/business/economy/ekonomi-digital-indonesia-00-def-456">
            <h2>Ekonomi Digital Indonesia Tumbuh Signifikan</h2>
          </a>
          <span>27 Oct 2026, 21:00 WIB</span>
        </article>
      </body>
    </html>
    """

    with patch("crab_news.sources.idntimes.fetch_html_page") as mock_fetch:
        # First page returns mock_html, second page returns empty page
        mock_fetch.side_effect = [mock_html, "<html><body></body></html>"]

        candidates = adapter.discover_articles(
            start_date=date(2026, 10, 27),
            end_date=date(2026, 10, 27),
            limit=10
        )

        assert len(candidates) == 2
        assert candidates[0]["title"] == "Pramono Tegaskan Tiket Ragunan Tak Bisa Gratis"
        assert candidates[0]["url"] == "https://www.idntimes.com/news/indonesia/berita-idn-1-00-abc-123"
        assert candidates[0]["published_at"].day == 27


def test_idntimes_extract_content_from_ld_json():
    """Test IDNTimes content extraction from Schema.org JSON-LD."""
    source_model = SourceModel(name="IDN Times", slug="idntimes", domain="idntimes.com", website_url="https://www.idntimes.com")
    adapter = IDNTimesSource(source_model)

    html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "NewsArticle",
          "headline": "Judul Berita IDN Times",
          "articleBody": "Jakarta, IDN Times - Ini merupakan isi berita lengkap dari artikel IDN Times yang diambil dari schema JSON-LD dengan format rapi."
        }
        </script>
      </head>
      <body>
        <article><p>Fallback text</p></article>
      </body>
    </html>
    """
    content = adapter.extract_content_from_html(html)
    assert "Ini merupakan isi berita lengkap dari artikel IDN Times" in content
