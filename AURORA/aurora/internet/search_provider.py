from __future__ import annotations

import re
import time
import base64
from dataclasses import dataclass
from html import unescape
from urllib.parse import parse_qs, quote_plus, urlparse
from urllib.request import Request, urlopen


@dataclass(slots=True)
class SearchResult:
    title: str
    url: str
    snippet: str
    provider: str
    published_at: str | None = None


class DuckDuckGoHtmlSearchProvider:
    name = "duckduckgo_html"

    def __init__(self, timeout_seconds: int = 10) -> None:
        self.timeout_seconds = timeout_seconds

    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
        request = Request(url, headers={"User-Agent": "Mozilla/5.0 ISIS-local-research/1.0"})
        started = time.time()
        with urlopen(request, timeout=self.timeout_seconds) as response:
            html = response.read(1024 * 1024).decode("utf-8", errors="ignore")
        results: list[SearchResult] = []
        for match in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.I | re.S):
            href = unescape(match.group(1))
            title = re.sub("<.*?>", "", unescape(match.group(2))).strip()
            if href.startswith("//duckduckgo.com/l/?uddg="):
                href = unescape(href.split("uddg=", 1)[1].split("&", 1)[0])
            if not title or not urlparse(href).scheme:
                continue
            snippet = ""
            after = html[match.end() : match.end() + 1400]
            snippet_match = re.search(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', after, re.I | re.S)
            if snippet_match:
                snippet = re.sub("<.*?>", "", unescape(snippet_match.group(1))).strip()
            results.append(SearchResult(title=title, url=href, snippet=snippet, provider=self.name))
            if len(results) >= max_results:
                break
        return results


class BingHtmlSearchProvider:
    name = "bing_html"

    def __init__(self, timeout_seconds: int = 10) -> None:
        self.timeout_seconds = timeout_seconds

    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        url = f"https://www.bing.com/search?q={quote_plus(query)}"
        request = Request(url, headers={"User-Agent": "Mozilla/5.0 ISIS-local-research/1.0"})
        with urlopen(request, timeout=self.timeout_seconds) as response:
            html = response.read(1024 * 1024).decode("utf-8", errors="ignore")
        results: list[SearchResult] = []
        for match in re.finditer(r'<li class="b_algo".*?<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?</h2>(.*?)</li>', html, re.I | re.S):
            href = self._decode_url(unescape(match.group(1)))
            title = re.sub("<.*?>", "", unescape(match.group(2))).strip()
            body = re.sub("<.*?>", " ", unescape(match.group(3)))
            snippet = re.sub(r"\s+", " ", body).strip()
            if not title or not urlparse(href).scheme:
                continue
            results.append(SearchResult(title=title, url=href, snippet=snippet, provider=self.name))
            if len(results) >= max_results:
                break
        return results

    def _decode_url(self, href: str) -> str:
        parsed = urlparse(href)
        if parsed.netloc.endswith("bing.com") and parsed.path.startswith("/ck/"):
            encoded = parse_qs(parsed.query).get("u", [""])[0]
            if encoded.startswith("a1"):
                payload = encoded[2:]
                payload += "=" * (-len(payload) % 4)
                try:
                    return base64.urlsafe_b64decode(payload).decode("utf-8", errors="ignore")
                except Exception:
                    return href
        return href


class CascadingSearchProvider:
    name = "duckduckgo_html+bing_html"

    def __init__(self, timeout_seconds: int = 10) -> None:
        self.providers = [DuckDuckGoHtmlSearchProvider(timeout_seconds), BingHtmlSearchProvider(timeout_seconds)]

    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        errors: list[str] = []
        for provider in self.providers:
            try:
                results = provider.search(query, max_results=max_results)
                if results:
                    return results
            except Exception as exc:
                errors.append(f"{provider.name}: {exc}")
        return []
