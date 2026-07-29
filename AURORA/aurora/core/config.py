from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from aurora.core.permissions import PrivilegeProfile
from aurora.core.resources import ResourceLimits
from aurora.core.routing import ModelProfile


class VoiceSettings(BaseModel):
    language: str = "pt-BR"
    wake_word_enabled: bool = True
    wake_word: str = "aurora"
    stt_engine: str = "mock"
    stt_binary_path: str = ""
    stt_model_path: str = ""
    tts_engine: str = "mock"
    piper_binary_path: str = ""
    piper_voice_path: str = ""
    kokoro_model_dir: str = r"D:\ISIS_IA\ISIS\models\voice\kokoro"
    kokoro_command: list[str] = Field(default_factory=list)
    kokoro_voice: str = ""
    chatterbox_model_dir: str = r"D:\ISIS_IA\ISIS\models\voice\chatterbox"
    chatterbox_command: list[str] = Field(default_factory=list)
    chatterbox_voice: str = ""
    selected_voice: str = "pt-BR-female-mock"
    response_mode: str = "text_and_voice"
    output_device: str = ""
    microphone_device: str = ""
    speed: float = 1.0
    volume: float = 1.0
    microphone_sensitivity: float = 0.02
    recognition_profile: str = "fast"
    allow_interruption: bool = True
    use_gpu: bool = True
    preload_models: bool = False
    keep_model_loaded: bool = False
    audio_cache_enabled: bool = True
    audio_cache_max_files: int = 200
    strict_offline: bool = True


class InternetSettings(BaseModel):
    enabled: bool = True
    mode: str = "controlled"
    automatic_search: bool = True
    default_research_mode: str = "quick"
    search_provider: str = "duckduckgo_html+bing_html"
    max_results: int = 5
    max_pages: int = 3
    deep_max_results: int = 10
    deep_max_pages: int = 6
    max_results_hard_limit: int = 20
    max_pages_hard_limit: int = 10
    max_page_bytes: int = 1500000
    timeout_seconds: int = 10
    requests_per_minute: int = 10
    requests_per_hour: int = 60
    allow_downloads: bool = False
    max_download_mb: int = 50
    save_research: bool = True
    save_sources: bool = True
    update_obsidian: bool = False
    require_memory_confirmation: bool = True
    use_cache: bool = True
    cache_ttl_seconds: int = 86400
    strict_offline: bool = False
    use_browser: bool = False
    allow_javascript: bool = False
    allow_cookies: bool = False
    allow_login: bool = False
    allow_private_networks: bool = False
    trusted_domains: list[str] = Field(default_factory=lambda: ["python.org", "github.com", "docs.github.com", "microsoft.com", "openai.com", "wikipedia.org"])
    allowed_domains: list[str] = Field(default_factory=list)
    blocked_domains: list[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1", "0.0.0.0"])
    blocked_extensions: list[str] = Field(default_factory=lambda: [".exe", ".msi", ".bat", ".cmd", ".ps1", ".scr", ".com", ".vbs", ".js", ".jar", ".dll"])


class ObsidianSettings(BaseModel):
    vault_name: str = "CEREBRO_VIVO"
    source_path: str = r"E:\Projetos\CEREBRO_VIVO"
    migrated_path: str = r"D:\ISIS_IA\ISIS\brain\cerebro_vivo"
    integration_mode: str = "READ_ONLY"
    allow_note_writes: bool = False
    allow_note_delete: bool = False
    allow_note_move: bool = False
    last_validation_status: str = "warning"


class IsisPaths(BaseModel):
    isis_root: str = r"D:\ISIS_IA\ISIS"
    code_root: str = r"D:\ISIS_IA\AURORA"
    models_dir: str = r"D:\ISIS_IA\ISIS\models"
    backups_dir: str = r"D:\ISIS_IA\ISIS\backups"
    logs_dir: str = r"D:\ISIS_IA\ISIS\logs"
    cache_dir: str = r"D:\ISIS_IA\ISIS\data\cache"
    temporary_dir: str = r"D:\ISIS_IA\ISIS\data\temporary"


class StorageSettings(BaseModel):
    dedicated_ssd_root: str = r"D:\ISIS_IA"
    minimum_free_gb: int = 40
    max_cache_gb: int = 20
    max_logs_gb: int = 10


class PrivacySettings(BaseModel):
    offline_mode: bool = True
    screen_analysis_enabled: bool = False
    camera_enabled: bool = False
    microphone_enabled: bool = False
    internet_enabled: bool = False


class ModelMapping(BaseModel):
    model_id: str
    profiles: list[ModelProfile]
    estimated_memory_mb: int
    context_tokens: int = 4096
    enabled: bool = True
    priority: int = 100


class AuroraConfig(BaseModel):
    assistant_name: str = "ISIS"
    language: str = "pt-BR"
    paths: IsisPaths = Field(default_factory=IsisPaths)
    obsidian: ObsidianSettings = Field(default_factory=ObsidianSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)
    profile: PrivilegeProfile = PrivilegeProfile.CONTROLLED
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    internet: InternetSettings = Field(default_factory=InternetSettings)
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits)
    models: list[ModelMapping] = Field(
        default_factory=lambda: [
            ModelMapping(model_id="fast-local-mock", profiles=[ModelProfile.FAST, ModelProfile.GENERAL], estimated_memory_mb=64, priority=1),
            ModelMapping(model_id="coding-local-mock", profiles=[ModelProfile.CODING], estimated_memory_mb=64, priority=2),
            ModelMapping(model_id="vision-local-mock", profiles=[ModelProfile.VISION], estimated_memory_mb=64, priority=3),
            ModelMapping(model_id="embedding-local-mock", profiles=[ModelProfile.EMBEDDING], estimated_memory_mb=64, priority=1),
        ]
    )
    allowed_folders: list[str] = Field(default_factory=lambda: ["D:\\ISIS_IA"])
    protected_folders: list[str] = Field(default_factory=lambda: ["C:\\Users"])
    blocked_commands: list[str] = Field(default_factory=lambda: ["format", "diskpart", "reg delete"])
    online_enabled: bool = False


class ConfigStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> AuroraConfig:
        if not self.path.exists():
            config = AuroraConfig()
            self.save(config)
            return config
        return AuroraConfig.model_validate(json.loads(self.path.read_text(encoding="utf-8")))

    def save(self, config: AuroraConfig) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(config.model_dump_json(indent=2), encoding="utf-8")
