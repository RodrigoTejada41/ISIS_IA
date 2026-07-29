from aurora.ui.hud_dashboard import hud_response_text, speech_excerpt
from aurora.ui.hud_web import build_hud_html
from aurora.voice.text import prepare_text_for_speech


def test_hud_response_text_prefers_model_text():
    assert hud_response_text({"text": "resposta", "output": "saida"}) == "resposta"
    assert hud_response_text({"output": "saida"}) == "saida"


def test_speech_excerpt_normalizes_and_limits_text():
    text = "linha 1\n\nlinha 2   linha 3"
    assert speech_excerpt(text, limit=14) == "linha 1 linha"


def test_prepare_text_for_speech_removes_markdown_and_summarizes_code():
    text = """# Status
**Corrigido**:
- item *um*
- veja [documento](https://exemplo.local)
```json
{"ok": true}
```
"""

    assert prepare_text_for_speech(text) == "Status Corrigido: item um. veja documento. Enviei um bloco de JSON na tela."


def test_web_hud_html_contains_operational_endpoints():
    html = build_hud_html(
        {
            "assistant_name": "ISIS",
            "ram_available_mb": 1000,
            "vram_available_mb": 0,
            "internet_enabled": False,
            "microphone_enabled": False,
            "tts_ready": True,
            "coding_model": "qwen3-coder:30b",
            "project_embeddings_indexed": 25,
            "project_embeddings_pending": 10,
            "embedding_model": "nomic-embed-text:latest",
            "tts_engine": "piper",
            "tts_voice": "pt_BR-faber-medium",
            "stt_engine": "mock",
            "project_notes_indexed": 35,
        }
    )

    assert "/api/chat" in html
    assert "/api/chat-status" in html
    assert "/api/conversation" in html
    assert "pollJob" in html
    assert "Novo projeto" in html
    assert "Tentar novamente" in html
    assert "Copiar" in html
    assert "/api/voice-test" in html
    assert "window.setTimeout(() => sendPrompt(), 150)" in html
    assert ".app { position:relative; height:100vh; min-height:0;" in html
    assert "grid-template-rows:78px minmax(0,1fr) 74px" in html
    assert ".workspace { overflow:auto; flex:1; min-height:0;" in html
    assert "function unlockInput()" in html
    assert "window.setTimeout(() => input.focus(), 0)" in html
    assert "Embeddings de projetos:" not in html
    assert "Memoria local pronta para consulta" in html
    assert "qwen3-coder:30b" in html
