from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ISIS_DIRS = [
    "app/core",
    "app/agents",
    "app/memory",
    "app/models",
    "app/voice",
    "app/perception/screen",
    "app/perception/camera",
    "app/automation",
    "app/permissions",
    "app/security",
    "app/integrations/obsidian",
    "app/interface",
    "app/learning",
    "app/monitoring",
    "brain/cerebro_vivo",
    "brain/knowledge",
    "brain/memory",
    "brain/decisions",
    "brain/bugs",
    "brain/projects",
    "brain/prompts",
    "brain/imported",
    "data/databases",
    "data/vector_store",
    "data/embeddings",
    "data/user_memory",
    "data/conversations",
    "data/cache",
    "data/temporary",
    "models",
    "voice/stt",
    "voice/tts",
    "voice/wakeword",
    "logs/audit",
    "logs/app",
    "logs/migration",
    "backups/daily",
    "backups/weekly",
    "backups/monthly",
    "backups/manual",
    "config",
    "docs",
    "scripts",
    "tests",
    "tools",
    "quarantine",
]


def bytes_to_gb(value: int) -> float:
    return round(value / 1024 / 1024 / 1024, 3)


def create_structure(root: Path, min_free_gb: int = 40) -> dict:
    root = root.resolve()
    usage = shutil.disk_usage(root.anchor)
    min_free_bytes = min_free_gb * 1024 * 1024 * 1024
    if usage.free < min_free_bytes:
        raise RuntimeError(f"free space below safety reserve: {bytes_to_gb(usage.free)} GB < {min_free_gb} GB")

    created: list[str] = []
    existing: list[str] = []
    root.mkdir(parents=True, exist_ok=True)
    for relative in ISIS_DIRS:
        path = root / relative
        if path.exists():
            existing.append(str(path))
        else:
            path.mkdir(parents=True, exist_ok=False)
            created.append(str(path))

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "drive": root.anchor,
        "free_bytes_before": usage.free,
        "free_gb_before": bytes_to_gb(usage.free),
        "minimum_free_gb_required": min_free_gb,
        "created_count": len(created),
        "existing_count": len(existing),
        "created": created,
        "existing": existing,
        "status": "created" if created else "already_exists",
        "notes": [
            "No CEREBRO VIVO files were copied, moved, deleted, renamed or modified.",
            "brain/cerebro_vivo is only a placeholder for the future validated migration.",
        ],
    }
    manifest_path = root / "config" / "phase2_structure_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def write_report(manifest: dict, path: Path) -> None:
    lines = [
        "# Fase 2 - Estrutura Inicial do SSD",
        "",
        f"Data: {manifest['generated_at']}",
        f"Raiz: `{manifest['root']}`",
        f"Drive: `{manifest['drive']}`",
        f"Espaco livre antes: `{manifest['free_gb_before']}` GB",
        f"Reserva minima exigida: `{manifest['minimum_free_gb_required']}` GB",
        f"Diretorios criados: `{manifest['created_count']}`",
        f"Diretorios ja existentes: `{manifest['existing_count']}`",
        f"Status: `{manifest['status']}`",
        "",
        "## Diretorios criados",
        "",
    ]
    lines.extend([f"- `{item}`" for item in manifest["created"]] or ["- Nenhum. Estrutura ja existia."])
    lines.extend(
        [
            "",
            "## Garantias",
            "",
            "- Nenhum arquivo do CEREBRO VIVO foi copiado.",
            "- Nenhum arquivo do CEREBRO VIVO foi movido.",
            "- Nenhum arquivo do CEREBRO VIVO foi apagado.",
            "- Estrutura criada apenas como destino futuro.",
            "",
            "## Proxima fase",
            "",
            "Fase 3: backup inicial antes da migracao.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=r"D:\ISIS_IA\ISIS")
    parser.add_argument("--report", default=r"D:\ISIS_IA\AURORA\reports\phase2_structure.md")
    parser.add_argument("--min-free-gb", type=int, default=40)
    args = parser.parse_args()

    manifest = create_structure(Path(args.root), args.min_free_gb)
    write_report(manifest, Path(args.report))
    print(json.dumps({"root": manifest["root"], "created_count": manifest["created_count"], "report": args.report}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
