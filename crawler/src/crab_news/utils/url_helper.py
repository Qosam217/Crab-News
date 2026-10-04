"""URL normalization and cleanup utilities."""

from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
    "_ga",
    "ref",
    "source",
}


def normalize_url(url: str) -> str:
    """Normalizes a URL by stripping tracking parameters, standardizing scheme/host,

    and removing unnecessary query strings and fragments.
    """
    if not url:
        return ""

    url = url.strip()
    parsed = urlparse(url)

    # Standardize scheme and lowercased netloc
    scheme = parsed.scheme.lower() if parsed.scheme else "https"
    netloc = parsed.netloc.lower()

    # Filter tracking query parameters
    query_params = parse_qsl(parsed.query, keep_blank_values=False)
    filtered_params = [
        (k, v) for k, v in query_params if k.lower() not in TRACKING_PARAMS
    ]
    query = urlencode(filtered_params)

    # Clean path (strip trailing slash if not root)
    path = parsed.path
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    # Reconstruct clean URL (drop fragment)
    clean_url = urlunparse((scheme, netloc, path, parsed.params, query, ""))
    return clean_url
