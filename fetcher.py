from typing import Optional
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ResearchMindAI/1.0)"
}

def fetch_html(url: str, timeout: int = 12) -> Optional[str]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        if resp.status_code >= 400:
            return None
        content_type = resp.headers.get("content-type", "")
        if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
            return None
        return resp.text
    except Exception:
        return None

def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "img", "header", "footer", "nav"]):
        tag.decompose()

    parts = []
    for block in soup.find_all(["article", "main", "p", "li", "h1", "h2", "h3"]):
        text = " ".join(block.get_text(" ", strip=True).split())
        if len(text) >= 40:
            parts.append(text)

    if not parts:
        body = soup.get_text(" ", strip=True)
        body = " ".join(body.split())
        return body[:6000]

    text = "\n".join(parts)
    return text[:8000]
