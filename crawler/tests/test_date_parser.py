from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
from crab_news.extractor.date_parser import parse_indonesian_date, parse_date_from_url

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")


def test_parse_date_from_url():
    cnn_url = "https://www.cnnindonesia.com/nasional/20261018141338-14-1416721/foto-detik-detik-penggerebekan"
    dt = parse_date_from_url(cnn_url)
    assert dt is not None
    assert dt.year == 2026
    assert dt.month == 10
    assert dt.day == 18
    assert dt.hour == 14
    assert dt.minute == 13
    assert dt.second == 38

    kompas_url = "https://regional.kompas.com/read/2026/10/18/153534278/viral-balita-menangis"
    dt_k = parse_date_from_url(kompas_url)
    assert dt_k is not None
    assert dt_k.year == 2026
    assert dt_k.month == 10
    assert dt_k.day == 18
    assert dt_k.hour == 15
    assert dt_k.minute == 35
    assert dt_k.second == 34


def test_parse_relative_date():
    ref = datetime(2026, 10, 18, 15, 0, 0, tzinfo=JAKARTA_TZ)
    
    dt = parse_indonesian_date("10 menit lalu", reference_time=ref)
    assert dt == ref - timedelta(minutes=10)

    dt2 = parse_indonesian_date("2 jam yang lalu", reference_time=ref)
    assert dt2 == ref - timedelta(hours=2)

    dt3 = parse_indonesian_date("kemarin", reference_time=ref)
    assert dt3.date() == date(2026, 10, 17)


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
