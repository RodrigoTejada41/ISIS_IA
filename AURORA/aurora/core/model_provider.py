from __future__ import annotations

import json
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from aurora.core.audit import AuditEvent, AuditLogger


@dataclass(frozen=True, slots=True)
class ModelPrompt:
    model_id: str
    prompt: str
    system: str = ""
    context: str = ""
    temperature: float = 0.2
    max_tokens: int = 1024


@dataclass(frozen=True, slots=True)
class ModelResponse:
    text: str
    model_id: str
    provider: str
    duration_ms: int
    tokens_estimated: int = 0


class ModelProvider(Protocol):
    provider_name: str

    def is_available(self) -> bool: ...
    def list_models(self) -> list[str]: ...
    def generate(self, prompt: ModelPrompt) -> ModelResponse: ...


class MockModelProvider:
    provider_name = "mock"

    def is_available(self) -> bool:
        return True

    def list_models(self) -> list[str]:
        return ["fast-local-mock", "coding-local-mock", "vision-local-mock", "embedding-local-mock"]

    def generate(self, prompt: ModelPrompt) -> ModelResponse:
        started = time.time()
        text = f"[mock:{prompt.model_id}] {prompt.prompt}"
        return ModelResponse(text=text, model_id=prompt.model_id, provider=self.provider_name, duration_ms=int((time.time() - started) * 1000), tokens_estimated=len(text.split()))


class OllamaModelProvider:
    provider_name = "ollama"

    def __init__(self, audit: AuditLogger, base_url: str = "http://127.0.0.1:11434", timeout_seconds: int = 300) -> None:
        self.audit = audit
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def is_available(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=2) as response:
                return response.status == 200
        except (OSError, urllib.error.URLError):
            return False

    def list_models(self) -> list[str]:
        if not self.is_available():
            return []
        with urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return [item["name"] for item in payload.get("models", []) if "name" in item]

    def generate(self, prompt: ModelPrompt) -> ModelResponse:
        started = time.time()
        if not self.is_available():
            raise RuntimeError("ollama unavailable")
        payload = {
            "model": prompt.model_id,
            "prompt": f"{prompt.system}\n\n{prompt.context}\n\n{prompt.prompt}".strip(),
            "stream": False,
            "options": {"temperature": prompt.temperature, "num_predict": prompt.max_tokens},
        }
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
        text = data.get("response", "")
        duration = int((time.time() - started) * 1000)
        self.audit.record(AuditEvent(action="model.generate", component="models", params={"provider": self.provider_name, "model": prompt.model_id}, duration_ms=duration))
        return ModelResponse(text=text, model_id=prompt.model_id, provider=self.provider_name, duration_ms=duration, tokens_estimated=len(text.split()))


class LlamaCppModelProvider:
    provider_name = "llama.cpp"

    def __init__(self, binary_path: str | Path, model_path: str | Path, timeout_seconds: int = 120) -> None:
        self.binary_path = Path(binary_path)
        self.model_path = Path(model_path)
        self.timeout_seconds = timeout_seconds

    def is_available(self) -> bool:
        return self.binary_path.exists() and self.model_path.exists()

    def list_models(self) -> list[str]:
        return [self.model_path.name] if self.is_available() else []

    def generate(self, prompt: ModelPrompt) -> ModelResponse:
        started = time.time()
        if not self.is_available():
            raise RuntimeError("llama.cpp binary or model unavailable")
        proc = subprocess.run(
            [str(self.binary_path), "-m", str(self.model_path), "-p", prompt.prompt, "-n", str(prompt.max_tokens), "--temp", str(prompt.temperature)],
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or "llama.cpp failed")
        text = proc.stdout.strip()
        return ModelResponse(text=text, model_id=prompt.model_id, provider=self.provider_name, duration_ms=int((time.time() - started) * 1000), tokens_estimated=len(text.split()))


class LmStudioModelProvider:
    provider_name = "lm_studio"

    def __init__(self, base_url: str = "http://127.0.0.1:1234/v1", timeout_seconds: int = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def is_available(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.base_url}/models", timeout=2) as response:
                return response.status == 200
        except (OSError, urllib.error.URLError):
            return False

    def list_models(self) -> list[str]:
        if not self.is_available():
            return []
        with urllib.request.urlopen(f"{self.base_url}/models", timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return [item["id"] for item in payload.get("data", []) if "id" in item]

    def generate(self, prompt: ModelPrompt) -> ModelResponse:
        started = time.time()
        if not self.is_available():
            raise RuntimeError("LM Studio local server unavailable")
        payload = {
            "model": prompt.model_id,
            "messages": [
                {"role": "system", "content": prompt.system or "Responda em pt-BR."},
                {"role": "user", "content": f"{prompt.context}\n\n{prompt.prompt}".strip()},
            ],
            "temperature": prompt.temperature,
            "max_tokens": prompt.max_tokens,
        }
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return ModelResponse(text=text, model_id=prompt.model_id, provider=self.provider_name, duration_ms=int((time.time() - started) * 1000), tokens_estimated=len(text.split()))


class ModelProviderRegistry:
    def __init__(self, providers: list[ModelProvider] | None = None) -> None:
        self.providers = providers or [MockModelProvider()]

    def available_models(self) -> dict[str, list[str]]:
        return {provider.provider_name: provider.list_models() for provider in self.providers if provider.is_available()}

    def generate(self, prompt: ModelPrompt, preferred_provider: str | None = None) -> ModelResponse:
        providers = self.providers
        if preferred_provider:
            providers = [p for p in self.providers if p.provider_name == preferred_provider]
        for provider in providers:
            if provider.is_available() and prompt.model_id in provider.list_models():
                return provider.generate(prompt)
        raise RuntimeError(f"model unavailable: {prompt.model_id}")


def discover_local_provider_names() -> dict[str, bool]:
    return {
        "ollama_cli": shutil.which("ollama") is not None,
        "nvidia_smi": shutil.which("nvidia-smi") is not None,
    }
