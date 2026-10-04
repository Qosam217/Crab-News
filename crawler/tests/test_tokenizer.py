from crab_news.processor.tokenizer import tokenize
from crab_news.processor.stopwords import is_stopword


def test_is_stopword():
    assert is_stopword("yang") is True
    assert is_stopword("dan") is True
    assert is_stopword("ekonomi") is False
    assert is_stopword("teknologi") is False


def test_tokenize():
    text = "Presiden Joko Widodo membahas pertumbuhan ekonomi dan transformasi digital di Indonesia."
    tokens = tokenize(text)
    # Stopwords like 'dan', 'di', 'indonesia' should be filtered
    assert "presiden" in tokens
    assert "joko" in tokens
    assert "widodo" in tokens
    assert "pertumbuhan" in tokens
    assert "ekonomi" in tokens
    assert "transformasi" in tokens
    assert "digital" in tokens
    assert "dan" not in tokens
    assert "di" not in tokens
