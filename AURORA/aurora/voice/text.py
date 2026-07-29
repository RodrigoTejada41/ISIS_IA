from __future__ import annotations

import re


VOICE_INSTRUCTIONS_PT_BR = (
    "Fale em portugues do Brasil, com voz feminina adulta, natural, calma e nao robotica. "
    "Use ritmo conversacional, pausas leves e entonacao humana. Nao leia simbolos de "
    "formatacao, markdown, bullets ou pontuacao literal."
)

CODE_SUMMARY = "Enviei um bloco de codigo na tela."
JSON_SUMMARY = "Enviei um bloco de JSON na tela."
COMMAND_SUMMARY = "Enviei um comando na tela."

_FENCED_BLOCK_RE = re.compile(r"```([a-zA-Z0-9_-]+)?\s*\n.*?```", re.DOTALL)
_MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_RAW_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_EMOJI_RE = re.compile(
    "["
    "\U0001f300-\U0001f5ff"
    "\U0001f600-\U0001f64f"
    "\U0001f680-\U0001f6ff"
    "\U0001f700-\U0001f77f"
    "\U0001f780-\U0001f7ff"
    "\U0001f800-\U0001f8ff"
    "\U0001f900-\U0001f9ff"
    "\U0001fa00-\U0001faff"
    "\U00002700-\U000027bf"
    "\U00002600-\U000026ff"
    "]+"
)
_DECORATIVE_SYMBOL_RE = re.compile(r"[•◆◇■□●○★☆✓✔✗✘→←↑↓]+")
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")


def prepare_text_for_speech(text: str, limit: int | None = None) -> str:
    raw = str(text or "")
    if not raw.strip():
        return ""

    raw = _FENCED_BLOCK_RE.sub(_summarize_fenced_block, raw)
    raw = _MARKDOWN_LINK_RE.sub(r"\1", raw)
    raw = _RAW_URL_RE.sub("link", raw)

    lines: list[str] = []
    for line in raw.splitlines():
        cleaned = _clean_line_for_speech(line)
        if cleaned:
            lines.append(cleaned)

    speech = " ".join(lines)
    speech = _strip_markdown_marks(speech)
    speech = _INLINE_CODE_RE.sub(_summarize_inline_code, speech)
    speech = _EMOJI_RE.sub("", speech)
    speech = _DECORATIVE_SYMBOL_RE.sub("", speech)
    speech = re.sub(r"[{}\[\]<>|~^]+", " ", speech)
    speech = re.sub(r"([!?.,;:]){2,}", r"\1", speech)
    speech = re.sub(r"\s+([,.!?;:])", r"\1", speech)
    speech = re.sub(r"([,.!?;:])(?=\S)", r"\1 ", speech)
    speech = re.sub(r"\s+", " ", speech).strip()

    if limit is not None:
        speech = speech[:limit].rstrip()
    return speech


def _summarize_fenced_block(match: re.Match[str]) -> str:
    language = (match.group(1) or "").lower()
    content = match.group(0)
    if language == "json" or _looks_like_json(content):
        return f"\n{JSON_SUMMARY}\n"
    if language in {"bash", "sh", "shell", "powershell", "ps1", "cmd"}:
        return f"\n{COMMAND_SUMMARY}\n"
    return f"\n{CODE_SUMMARY}\n"


def _clean_line_for_speech(line: str) -> str:
    value = line.strip()
    if not value:
        return ""
    if _looks_like_command(value):
        return COMMAND_SUMMARY
    if _looks_like_json(value):
        return JSON_SUMMARY
    is_list_item = bool(re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", value))
    value = re.sub(r"^\s{0,3}#{1,6}\s+", "", value)
    value = re.sub(r"^\s*[-*•]\s+", "", value)
    value = re.sub(r"^\s*\d+[.)]\s+", "", value)
    if is_list_item and value and value[-1] not in ".!?":
        value += "."
    return value.strip()


def _strip_markdown_marks(text: str) -> str:
    value = text
    value = re.sub(r"(\*\*|__)(.*?)\1", r"\2", value)
    value = re.sub(r"(?<!\w)[*_]([^*_]+)[*_](?!\w)", r"\1", value)
    value = value.replace("```", " ")
    value = value.replace("`", " ")
    value = value.replace("#", " ")
    value = value.replace("*", " ")
    value = value.replace("_", " ")
    return value


def _summarize_inline_code(match: re.Match[str]) -> str:
    code = match.group(1).strip()
    if _looks_like_command(code):
        return COMMAND_SUMMARY
    if _looks_like_json(code):
        return JSON_SUMMARY
    if _looks_like_code(code):
        return CODE_SUMMARY
    return code


def _looks_like_command(text: str) -> bool:
    value = text.strip()
    return bool(re.match(r"^(\.\\|python\s+-m|pip\s+|npm\s+|npx\s+|git\s+|powershell\s+|cmd\s+/c)", value, re.I))


def _looks_like_json(text: str) -> bool:
    value = text.strip()
    return (value.startswith("{") and value.endswith("}")) or (value.startswith("[") and value.endswith("]"))


def _looks_like_code(text: str) -> bool:
    return bool(re.search(r"[=;{}()]|->|=>|::|\\\\|/[A-Za-z0-9_.-]+", text))
