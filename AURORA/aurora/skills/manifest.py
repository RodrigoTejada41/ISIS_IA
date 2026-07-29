from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SkillRisk(str, Enum):
    READ_ONLY = "READ_ONLY"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SkillPermission(str, Enum):
    FILES_READ = "files.read"
    FILES_WRITE = "files.write"
    FILES_DELETE = "files.delete"
    PROCESSES_READ = "processes.read"
    PROCESSES_START = "processes.start"
    PROCESSES_STOP = "processes.stop"
    NETWORK_LOCAL = "network.local"
    NETWORK_INTERNET = "network.internet"
    DATABASE_READ = "database.read"
    DATABASE_WRITE = "database.write"
    SYSTEM_INFO = "system.info"


class SkillManifest(BaseModel):
    id: str
    name: str
    display_name: str
    description: str
    version: str
    author: str
    entrypoint: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    supported_platforms: list[str] = Field(default_factory=lambda: ["windows"])
    minimum_aurora_version: str = "0.1.0"
    permissions: list[SkillPermission] = Field(default_factory=list)
    risk_level: SkillRisk = SkillRisk.READ_ONLY
    requires_confirmation: bool = False
    timeout_seconds: int = 10
    enabled: bool = True
    checksum: str = ""

    @field_validator("id", "name")
    @classmethod
    def safe_identifier(cls, value: str) -> str:
        if not value.replace("_", "").replace("-", "").isalnum():
            raise ValueError("identifier must be alphanumeric, dash or underscore")
        return value
