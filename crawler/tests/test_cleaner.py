from crab_news.processor.cleaner import strip_html, clean_text


def test_strip_html():
    raw_html = "<p>Pemerintah <b>Indonesia</b> mengumumkan kebijakan baru.</p><script>alert('test')</script>"
    cleaned = strip_html(raw_html)
    assert "Pemerintah Indonesia mengumumkan kebijakan baru." in cleaned
    assert "alert" not in cleaned


def test_clean_text():
    text = "Kunjungi https://example.com/news?ref=123 untuk info lebih lanjut! Email: info@example.com."
    cleaned = clean_text(text)
    assert "https" not in cleaned
    assert "info@example.com" not in cleaned
    assert "Kunjungi" in cleaned
    assert "untuk info lebih lanjut" in cleaned
