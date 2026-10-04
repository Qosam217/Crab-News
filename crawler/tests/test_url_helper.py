from crab_news.utils.url_helper import normalize_url
from crab_news.utils.hasher import compute_content_hash


def test_normalize_url():
    raw_url = "https://news.kompas.com/read/2026/10/04/123456/berita-baru/?utm_source=twitter&utm_medium=social#comments"
    clean = normalize_url(raw_url)
    assert clean == "https://news.kompas.com/read/2026/10/04/123456/berita-baru"
    assert "utm_source" not in clean
    assert "#comments" not in clean


def test_compute_content_hash():
    text1 = "Berita hari ini di Jakarta Selatan"
    text2 = "  berita hari   ini DI jakarta selatan \n "
    hash1 = compute_content_hash(text1)
    hash2 = compute_content_hash(text2)
    assert hash1 == hash2
    assert len(hash1) == 64
