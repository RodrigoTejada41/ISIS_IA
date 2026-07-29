from __future__ import annotations

import hashlib
import gzip
import re
import time
from dataclasses import dataclass
from html import unescape
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import HTTPRedirectHandler, Request, build_opener

from aurora.internet.content_sanitizer import ContentSanitizer


@dataclass(slots=True)
class PageContent:
    url: str
    title: str
    text: str
    fetched_at: str
    content_hash: str
    suspicious: bool = False
    warnings: list[str] | None = None


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class PageReader:
    def __init__(self, timeout_seconds: int = 10, max_bytes: int = 1_500_000, max_redirects: int = 3, url_validator=None) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes
        self.max_redirects = max_redirects
        self.url_validator = url_validator
        self.sanitizer = ContentSanitizer()

    def read(self, url: str) -> PageContent:
        current_url = url
        opener = build_opener(_NoRedirect)
        response = None
        for _ in range(self.max_redirects + 1):
            if self.url_validator:
                decision = self.url_validator(current_url)
                if not decision.allowed:
                    raise RuntimeError(f"redirect blocked: {decision.reason}")
            request = Request(current_url, headers={"User-Agent": "ISIS-local-page-reader/1.0", "Accept-Encoding": "identity"})
            try:
                response = opener.open(request, timeout=self.timeout_seconds)
                break
            except HTTPError as exc:
                if exc.code not in {301, 302, 303, 307, 308}:
                    raise
                location = exc.headers.get("location")
                if not location:
                    raise
                current_url = urljoin(current_url, location)
        if response is None:
            raise RuntimeError("redirect limit exceeded")
        with response:
            raw = response.read(self.max_bytes)
            if response.headers.get("content-encoding", "").lower() == "gzip":
                raw = gzip.decompress(raw)
        html = raw.decode("utf-8", errors="ignore")
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
        title = re.sub(r"\s+", " ", unescape(title_match.group(1))).strip() if title_match else url
        clean = re.sub(r"(?is)<(script|style|nav|footer|header).*?>.*?</\1>", " ", html)
        clean = re.sub(r"(?s)<[^>]+>", " ", clean)
        clean = unescape(re.sub(r"\s+", " ", clean)).strip()
        clean = "".join(ch if ch in "\n\t" or ord(ch) >= 32 else " " for ch in clean)
        sanitized = self.sanitizer.sanitize_external_text(clean)
        return PageContent(
            url=current_url,
            title=title[:240],
            text=sanitized.text,
            fetched_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            content_hash=hashlib.sha256(raw).hexdigest(),
            suspicious=sanitized.suspicious,
            warnings=sanitized.warnings,
        )
