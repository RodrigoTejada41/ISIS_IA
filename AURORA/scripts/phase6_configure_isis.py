from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aurora.core.config import AuroraConfig, ConfigStore


def bytes_to_gb(value: int) -> float:
    return round(value / 1024 / 1024 / 1024, 3)


def configure(
    code_config_path: Path,
    isis_config_path: Path,
    validation_report_path: Path,
    min_free_gb: int = 40,
) -> dict:
    store = ConfigStore(code_config_path)
    config = store.load()
    validation = json.loads(validation_report_path.read_text(encoding="utf-8"))
    config.assistant_name = "ISIS"
    config.language = "pt-BR"
    config.obsidian.last_validation_status = validation.get("status", "unknown")
    config.obsidian.integration_mode = "READ_ONLY"
    config.obsidian.allow_note_writes = False
    config.obsidian.allow_note_delete = False
    config.obsidian.allow_note_move = False
    config.privacy.offline_mode = True
    config.privacy.internet_enabled = False
    config.privacy.screen_analysis_enabled = False
    config.privacy.camera_enabled = False
    config.privacy.microphone_enabled = False
    config.storage.minimum_free_gb = min_free_gb
    store.save(config)

    isis_config_path.parent.mkdir(parents=True, exist_ok=True)
    isis_config_path.write_text(config.model_dump_json(indent=2), encoding="utf-8")
    usage = shutil.disk_usage(Path(config.storage.dedicated_ssd_root).anchor)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "code_config": str(code_config_path),
        "isis_config": str(isis_config_path),
        "assistant_name": config.assistant_name,
        "obsidian_vault": config.obsidian.migrated_path,
        "obsidian_mode": config.obsidian.integration_mode,
        "offline_mode": config.privacy.offline_mode,
        "internet_enabled": config.privacy.internet_enabled,
        "screen_analysis_enabled": config.privacy.screen_analysis_enabled,
        "camera_enabled": config.privacy.camera_enabled,
        "microphone_enabled": config.privacy.microphone_enabled,
        "minimum_free_gb": config.storage.minimum_free_gb,
        "free_gb_current": bytes_to_gb(usage.free),
        "validation_status": config.obsidian.last_validation_status,
        "status": "configured",
    }
    return report


def write_report(report: dict, path: Path) -> None:
    lines = [
        "# Fase 6 - Configuracao Central da ISIS",
        "",
        f"Data: {report['generated_at']}",
        f"Config codigo: `{report['code_config']}`",
        f"Config ISIS: `{report['isis_config']}`",
        f"Assistente: `{report['assistant_name']}`",
        f"Cofre Obsidian: `{report['obsidian_vault']}`",
        f"Modo Obsidian: `{report['obsidian_mode']}`",
        f"Offline: `{report['offline_mode']}`",
        f"Internet habilitada: `{report['internet_enabled']}`",
        f"Tela habilitada: `{report['screen_analysis_enabled']}`",
        f"Camera habilitada: `{report['camera_enabled']}`",
        f"Microfone habilitado: `{report['microphone_enabled']}`",
        f"Reserva minima: `{report['minimum_free_gb']}` GB",
        f"Espaco livre atual: `{report['free_gb_current']}` GB",
        f"Validacao do cofre: `{report['validation_status']}`",
        f"Status: `{report['status']}`",
        "",
        "## Garantias",
        "",
        "- Configuracao nao contem credenciais.",
        "- Obsidian configurado como `READ_ONLY`.",
        "- Escrita, movimentacao e exclusao de notas desativadas.",
        "- Internet, tela, camera e microfone desativados por padrao.",
        "",
        "## Proxima fase",
        "",
        "Fase 7: nucleo da ISIS usando esta configuracao central.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-config", default=r"D:\ISIS_IA\AURORA\data\config.json")
    parser.add_argument("--isis-config", default=r"D:\ISIS_IA\ISIS\config\isis_config.json")
    parser.add_argument("--validation-json", default=r"D:\ISIS_IA\AURORA\reports\phase5_validation_after_remediation.json")
    parser.add_argument("--report", default=r"D:\ISIS_IA\AURORA\reports\phase6_configuration.md")
    parser.add_argument("--min-free-gb", type=int, default=40)
    args = parser.parse_args()
    report = configure(Path(args.code_config), Path(args.isis_config), Path(args.validation_json), args.min_free_gb)
    write_report(report, Path(args.report))
    print(json.dumps({"status": report["status"], "isis_config": report["isis_config"], "report": args.report}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
