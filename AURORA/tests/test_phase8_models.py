from pathlib import Path

import pytest

from aurora.cli import main
from aurora.core.assistant import IsisAssistantCore
from aurora.core.model_provider import (
    LlamaCppModelProvider,
    LmStudioModelProvider,
    MockModelProvider,
    ModelPrompt,
    ModelProviderRegistry,
    OllamaModelProvider,
    discover_local_provider_names,
)
from aurora.core.audit import AuditLogger


def test_mock_model_provider_generates_text():
    provider = MockModelProvider()

    response = provider.generate(ModelPrompt(model_id="coding-local-mock", prompt="teste"))

    assert response.provider == "mock"
    assert "teste" in response.text


def test_provider_registry_reports_unavailable_model():
    registry = ModelProviderRegistry([MockModelProvider()])

    with pytest.raises(RuntimeError):
        registry.generate(ModelPrompt(model_id="missing", prompt="x"))


def test_llama_cpp_unavailable_without_files(tmp_path):
    provider = LlamaCppModelProvider(tmp_path / "main.exe", tmp_path / "model.gguf")

    assert provider.is_available() is False
    with pytest.raises(RuntimeError):
        provider.generate(ModelPrompt(model_id="model.gguf", prompt="x"))


def test_lm_studio_unavailable_by_default():
    provider = LmStudioModelProvider(base_url="http://127.0.0.1:9/v1")

    assert provider.is_available() is False
    assert provider.list_models() == []


def test_ollama_unavailable_on_closed_port(tmp_path):
    provider = OllamaModelProvider(AuditLogger(tmp_path / "audit.jsonl"), base_url="http://127.0.0.1:9")

    assert provider.is_available() is False
    assert provider.list_models() == []


def test_discover_local_provider_names_returns_flags():
    flags = discover_local_provider_names()

    assert "ollama_cli" in flags
    assert "nvidia_smi" in flags


def test_core_generate_uses_mock_provider(tmp_path):
    core = IsisAssistantCore(tmp_path)
    core.initialize()

    result = core.generate_text("corrija este codigo")

    assert result["provider"] == "mock"
    assert result["model"] == "coding-local-mock"


def test_cli_generate_outputs_json(tmp_path, capsys):
    code = main(["--root", str(tmp_path), "generate", "ola"])

    payload = capsys.readouterr().out
    assert code == 0
    assert "mock" in payload
