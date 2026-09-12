import hashlib
import logging
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; ResearchMindAI/2.0; "
        "+https://github.com/HridayUpadhyaya/Researchmind-ai-agent)"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.5",
}

MAX_RESPONSE_BYTES = 5 * 1024 * 1024

_RESPONSE_CACHE: dict[str, str] = {}

_SESSION = requests.Session()


def _cache_key(url: str) -> str:
    return hashlib.md5(
        url.encode("utf-8"),
        usedforsecurity=False,
    ).hexdigest()


def fetch_html(
    url: str,
    timeout: int = 12,
    follow_redirects: bool = True,
) -> Optional[str]:
    """Fetch an HTML page with caching and a response-size limit."""

    cache_key = _cache_key(url)

    if cache_key in _RESPONSE_CACHE:
        return _RESPONSE_CACHE[cache_key]

    try:
        with _SESSION.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=follow_redirects,
            stream=True,
        ) as response:

            if response.status_code >= 400:
                logger.warning(
                    "Failed to fetch %s: status=%s",
                    url,
                    response.status_code,
                )
                return None

            content_type = response.headers.get(
                "content-type",
                "",
            ).lower()

            if (
                "text/html" not in content_type
                and "application/xhtml+xml" not in content_type
            ):
                logger.warning(
                    "Skipping non-HTML URL %s: content-type=%s",
                    url,
                    content_type,
                )
                return None

            content = response.raw.read(
                MAX_RESPONSE_BYTES,
                decode_content=True,
            )

            encoding = response.encoding or "utf-8"

            html = content.decode(
                encoding,
                errors="replace",
            )

            _RESPONSE_CACHE[cache_key] = html

            return html

    except requests.RequestException as exc:
        logger.warning(
            "Request failed for %s: %s",
            url,
            exc,
        )

    except Exception as exc:
        logger.exception(
            "Unexpected fetch error for %s: %s",
            url,
            exc,
        )

    return None


def extract_text(
    html: str,
    max_length: int = 10_000,
) -> Tuple[str, int]:
    """Extract readable text from the main HTML content."""

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
            "img",
            "header",
            "footer",
            "nav",
        ]
    ):
        tag.decompose()

    blocks = []
    seen = set()

    for block in soup.find_all(
        [
            "article",
            "main",
            "p",
            "li",
            "h1",
            "h2",
            "h3",
            "section",
            "blockquote",
            "td",
            "th",
        ]
    ):
        text = " ".join(
            block.get_text(
                " ",
                strip=True,
            ).split()
        )

        if len(text) >= 40 and text not in seen:
            seen.add(text)
            blocks.append(text)

    if blocks:
        extracted = "\n".join(blocks)[:max_length]

    else:
        body = " ".join(
            soup.get_text(
                " ",
                strip=True,
            ).split()
        )

        extracted = body[:max_length]

    return extracted, len(extracted.split())


def extract_title(html: str) -> str:
    """Extract the page title, falling back to the first H1."""

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    title_tag = soup.find("title")

    if title_tag:
        title = title_tag.get_text(
            " ",
            strip=True,
        )

        if title:
            return title

    h1_tag = soup.find("h1")

    if h1_tag:
        title = h1_tag.get_text(
            " ",
            strip=True,
        )

        if title:
            return title

    return ""


def clear_cache() -> int:
    """Clear the in-memory HTML cache."""

    count = len(_RESPONSE_CACHE)

    _RESPONSE_CACHE.clear()

    return count
