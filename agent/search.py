import logging
import time
from typing import List
from urllib.parse import urlparse

from duckduckgo_search import DDGS

from .schemas import SearchResult

logger = logging.getLogger(__name__)


def web_search(query: str, max_results: int = 5) -> List[SearchResult]:
    """Search DuckDuckGo with a small retry policy."""

    results: List[SearchResult] = []
    retries = 2

    for attempt in range(retries + 1):
        try:
            with DDGS() as ddgs:
                for item in ddgs.text(
                    query,
                    max_results=max_results,
                    safesearch="moderate",
                ):
                    title = item.get("title") or ""
                    url = item.get("href") or item.get("url") or ""
                    snippet = item.get("body") or item.get("snippet") or ""

                    if not title or not url:
                        continue

                    domain = urlparse(url).netloc.lower()

                    results.append(
                        SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            domain=domain,
                        )
                    )

            break

        except Exception as exc:
            logger.warning(
                "Search attempt %s failed for query %r: %s",
                attempt + 1,
                query,
                exc,
            )

            if attempt < retries:
                time.sleep(1)

    if not results:
        logger.error("No search results found for query: %s", query)

    return dedupe_results(results)


def dedupe_results(results: List[SearchResult]) -> List[SearchResult]:
    """Remove duplicate URLs using normalized scheme/netloc/path."""

    seen = set()
    output: List[SearchResult] = []

    for result in results:
        parsed = urlparse(result.url)

        scheme = parsed.scheme.lower() or "https"
        netloc = parsed.netloc.lower().removeprefix("www.")
        path = (parsed.path or "/").rstrip("/") or "/"

        key = f"{scheme}://{netloc}{path}"

        if key in seen:
            continue

        seen.add(key)
        output.append(result)

    return output


def search_with_fallback(
    query: str,
    max_results: int = 5,
) -> List[SearchResult]:
    """Search normally, then retry with a simplified query if needed."""

    results = web_search(
        query,
        max_results=max_results,
    )

    if results:
        return results

    fallback_query = " ".join(query.split()[:5]).strip()

    if not fallback_query or fallback_query == query.strip():
        return []

    logger.info(
        "Falling back from %r to %r",
        query,
        fallback_query,
    )

    return web_search(
        fallback_query,
        max_results=max_results,
    )
