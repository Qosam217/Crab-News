
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

START_URL = "https://www.cnnindonesia.com/nasional/indeks/3"

session = requests.Session()
session.headers.update({
    "User-Agent": "CrabNewsCrawler/0.1"
})

response = session.get(START_URL, timeout=30)

print("HTTP:", response.status_code)
print("Final URL:", response.url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

article_pattern = re.compile(
    r"/nasional/\d{14}-\d+-\d+/"
)

article_links = set()
pagination_links = set()

for anchor in soup.select("a[href]"):
    href = urljoin(response.url, anchor["href"])
    parsed = urlparse(href)
    text = anchor.get_text(" ", strip=True).lower()
    path = parsed.path.lower()
    query = parsed.query.lower()

    if article_pattern.search(path):
        article_links.add(href)

    # Diagnostic only: inspect possible pagination links.
    if (
        "page" in query
        or "page" in path
        or "pagination" in path
        or text in {"next", "berikutnya", "›", "»", "→"}
    ):
        pagination_links.add(href)

print(f"\nArticle links found: {len(article_links)}")
for link in sorted(article_links)[:10]:
    print("ARTICLE:", link)

print(f"\nPossible pagination links: {len(pagination_links)}")
for link in sorted(pagination_links):
    print("PAGINATION:", link)