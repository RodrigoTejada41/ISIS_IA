from __future__ import annotations

import re

from aurora.voice.text import prepare_text_for_speech


_PATH_RE = re.compile(r"\b[A-Za-z]:\\[^\s]+")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.\w+\b")
_HTTP_STATUS_RE = re.compile(r"\bHTTP\s+200\b", re.I)
_PERCENT_RE = re.compile(r"\b(CPU|RAM|GPU)\s+(\d{1,3})%", re.I)
_TEMP_RE = re.compile(r"\b(\d{1,3})\s*°\s*C\b|\b(\d{1,3})\s*C\b", re.I)


class PortugueseSpeechNormalizer:
    def normalize(self, text: str, limit: int | None = None) -> str:
        value = str(text or "")
        value = _HTTP_STATUS_RE.sub("A operacao foi concluida com sucesso", value)
        value = _PATH_RE.sub("o caminho local indicado", value)
        value = _EMAIL_RE.sub("o endereco de email informado", value)
        value = _PERCENT_RE.sub(lambda m: f"{m.group(1).upper()} em {m.group(2)} por cento", value)
        value = _TEMP_RE.sub(lambda m: f"{m.group(1) or m.group(2)} graus", value)
        return prepare_text_for_speech(value, limit=limit)

