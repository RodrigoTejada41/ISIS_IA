from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aurora.core.config import AuroraConfig
from aurora.core.permissions import PrivilegeProfile
from aurora.internet.domain_policy import DomainPolicy
from aurora.internet.download_manager import DownloadManager
from aurora.internet.research_agent import ResearchAgent
from aurora.internet.search_provider import SearchResult
from aurora.permissions.permission_engine import ActionContext, PermissionEngine
from aurora.permissions.rule_activation import RuleActivationService
from aurora.permissions.rule_parser import RuleParser


def _config(tmp_path: Path) -> AuroraConfig:
    config = AuroraConfig()
    config.profile = PrivilegeProfile.MEDIUM
    config.paths.isis_root = str(tmp_path)
    config.privacy.offline_mode = False
    config.privacy.internet_enabled = True
    config.internet.enabled = True
    config.internet.mode = "controlled"
    config.internet.allowed_domains = []
    config.internet.trusted_domains = ["example.com"]
    return config


def test_domain_policy_blocks_private_and_unsafe_schemes():
    policy = DomainPolicy([], [], [], allow_private_networks=False)

    assert policy.validate_url("file:///C:/senha.txt", resolve_dns=False).allowed is False
    assert policy.validate_url("http://127.0.0.1/admin", resolve_dns=False).allowed is False
    assert policy.validate_url("https://example.com/docs", resolve_dns=False).allowed is True


def test_permission_engine_blocks_offline_internet(tmp_path):
    config = _config(tmp_path)
    config.privacy.offline_mode = True
    engine = PermissionEngine(config, tmp_path / "permissions")

    decision = engine.evaluate(ActionContext("internet.search", "python docs"))

    assert decision.status == "deny"
    assert "Internet bloqueada" in decision.reason


def test_permission_engine_requires_confirmation_for_controlled_profile(tmp_path):
    config = _config(tmp_path)
    config.profile = PrivilegeProfile.CONTROLLED
    engine = PermissionEngine(config, tmp_path / "permissions")

    decision = engine.evaluate(ActionContext("internet.search", "python docs"))

    assert decision.status == "confirm"
    assert decision.requires_confirmation is True


def test_rule_parser_extracts_limits_domains_and_download_policy():
    parsed = RuleParser().parse("Permita github.com por no maximo 5 paginas. Nao pode executar arquivos baixados.")

    assert parsed.structured["domains"]["allowed"] == ["github.com"]
    assert parsed.structured["limits"]["max_pages_per_research"] == 5
    assert parsed.structured["downloads"]["automatic_execution"] is False
    assert parsed.risk == "HIGH"


class _FakeProvider:
    name = "fake"

    def search(self, query: str, max_results: int = 10):
        return [SearchResult("Example", "https://example.com/page", "Snippet seguro", self.name)]


class _FakeReader:
    def read(self, url: str):
        @dataclass(slots=True)
        class Page:
            title: str = "Example page"
            text: str = "Conteudo publico de teste."
            content_hash: str = "abc"
            suspicious: bool = False
            warnings: list[str] | None = None

        return Page()


def test_research_agent_records_sources_without_network(tmp_path):
    config = _config(tmp_path)
    agent = ResearchAgent(config, tmp_path)
    agent.provider = _FakeProvider()
    agent.reader = _FakeReader()
    agent.domain_policy = DomainPolicy([], ["example.com"], [], allow_private_networks=False)

    result = agent.research("pesquise documentacao", confirmed=True)

    assert result["ok"] is True
    assert result["sources"][0]["url"] == "https://example.com/page"
    assert result["confidence"] in {"Alta", "Moderada"}
    assert agent.history.list(1)[0]["query"] == "pesquise documentacao"


class _ConfigStore:
    def __init__(self):
        self.saved = False

    def save(self, config):
        self.saved = True


def test_rule_activation_updates_config_with_confirmation(tmp_path):
    config = _config(tmp_path)
    store = _ConfigStore()
    service = RuleActivationService(config, store, tmp_path / "permissions")

    result = service.apply_text("Permita github.com por no maximo 4 paginas.", confirmed=True)

    assert result["ok"] is True
    assert config.internet.max_pages == 4
    assert "github.com" in config.internet.trusted_domains
    assert store.saved is True
    assert service.history(1)[0]["parsed"]["limits"]["max_pages_per_research"] == 4


def test_download_manager_blocks_executables_before_network(tmp_path):
    config = _config(tmp_path)
    manager = DownloadManager(config, tmp_path)

    result = manager.download("https://example.com/tool.exe", confirmed=True)

    assert result.ok is False
    assert result.status == "blocked"
    assert ".exe" in result.error
