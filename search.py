from typing import List
from duckduckgo_search import DDGS
from .schemas import SearchResult

def web_search(query: str, max_results: int = 5) -> List[SearchResult]:
    results: List[SearchResult] = []
    try:
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=max_results, safesearch="moderate"):
                title = item.get("title") or ""
                url = item.get("href") or item.get("url") or ""
                snippet = item.get("body") or item.get("snippet") or ""
                if title and url:
                    results.append(SearchResult(title=title, url=url, snippet=snippet))
    except Exception:
        return []
    return results

def dedupe_results(results: List[SearchResult]) -> List[SearchResult]:
    seen = set()
    out = []
    for r in results:
        key = r.url.split("#")[0].rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out
