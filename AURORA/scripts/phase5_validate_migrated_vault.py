from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ATTACHMENT_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".docx", ".xlsx", ".pptx", ".mp3", ".wav", ".mp4", ".zip"}


def load_json(path: Path) -> dict | list:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"error": str(exc)}


def collect_markdown_files(vault: Path, max_files: int = 5000) -> list[Path]:
    files: list[Path] = []
    for path in vault.rglob("*.md"):
        files.append(path)
        if len(files) >= max_files:
            break
    return files


def note_stems(vault: Path) -> set[str]:
    return {path.stem.lower() for path in vault.rglob("*.md")}


def link_exists(vault: Path, current_file: Path, target: str, stems: set[str]) -> bool:
    normalized = target.replace("/", "\\").strip()
    if not normalized:
        return True
    relative_candidates = [
        (current_file.parent / normalized),
        (vault / normalized),
    ]
    for candidate in relative_candidates:
        if candidate.exists():
            return True
        if candidate.with_suffix(".md").exists():
            return True
    return Path(normalized).name.lower() in stems


def validate_links(vault: Path, max_files: int = 5000) -> dict:
    stems = note_stems(vault)
    checked_files = collect_markdown_files(vault, max_files)
    total_links = 0
    unresolved: list[dict[str, str]] = []
    for path in checked_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for raw in re.findall(r"\[\[([^\]]+)\]\]", text):
            total_links += 1
            target = raw.split("|", 1)[0].split("#", 1)[0].strip()
            ok = link_exists(vault, path, target, stems)
            if not ok and len(unresolved) < 200:
                unresolved.append({"file": str(path), "link": raw})
    return {
        "checked_markdown_files": len(checked_files),
        "total_links_checked": total_links,
        "unresolved_count_sampled": len(unresolved),
        "unresolved_sample": unresolved,
        "status": "warning" if unresolved else "ok",
    }


def validate_attachments(vault: Path) -> dict:
    attachments = [path for path in vault.rglob("*") if path.is_file() and path.suffix.lower() in ATTACHMENT_EXTS]
    missing_or_empty = [{"file": str(path), "bytes": path.stat().st_size} for path in attachments if path.stat().st_size == 0][:200]
    by_extension = Counter(path.suffix.lower() for path in attachments)
    return {
        "attachments": len(attachments),
        "by_extension": dict(by_extension.most_common()),
        "empty_count_sampled": len(missing_or_empty),
        "empty_sample": missing_or_empty,
        "status": "warning" if missing_or_empty else "ok",
    }


def validate_plugins(vault: Path) -> dict:
    obsidian = vault / ".obsidian"
    community = obsidian / "community-plugins.json"
    plugins = load_json(community) if community.exists() else []
    plugin_dirs = obsidian / "plugins"
    installed_dirs = sorted(path.name for path in plugin_dirs.iterdir() if path.is_dir()) if plugin_dirs.exists() else []
    missing_dirs = sorted(set(plugins) - set(installed_dirs)) if isinstance(plugins, list) else []
    return {
        "community_plugins_file": str(community),
        "configured_plugins": plugins,
        "installed_plugin_dirs": installed_dirs,
        "missing_plugin_dirs": missing_dirs,
        "status": "warning" if missing_dirs else "ok",
    }


def validate_migration(vault: Path, manifest_path: Path, max_link_files: int = 5000) -> dict:
    manifest = load_json(manifest_path)
    source_status = manifest.get("status") if isinstance(manifest, dict) else None
    comparison_valid = manifest.get("comparison", {}).get("valid") if isinstance(manifest, dict) else None
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "vault": str(vault),
        "manifest": str(manifest_path),
        "vault_exists": vault.exists(),
        "obsidian_dir_exists": (vault / ".obsidian").exists(),
        "migration_manifest_status": source_status,
        "migration_hash_valid": comparison_valid,
        "links": validate_links(vault, max_link_files),
        "attachments": validate_attachments(vault),
        "plugins": validate_plugins(vault),
    }
    report["status"] = "validated" if all(
        [
            report["vault_exists"],
            report["obsidian_dir_exists"],
            source_status == "validated",
            comparison_valid is True,
            report["links"]["status"] == "ok",
            report["attachments"]["status"] == "ok",
            report["plugins"]["status"] == "ok",
        ]
    ) else "warning"
    return report


def write_report(report: dict, path: Path) -> None:
    lines = [
        "# Fase 5 - Validacao do Cofre Migrado",
        "",
        f"Data: {report['generated_at']}",
        f"Cofre: `{report['vault']}`",
        f"Manifesto: `{report['manifest']}`",
        f"Cofre existe: `{report['vault_exists']}`",
        f".obsidian existe: `{report['obsidian_dir_exists']}`",
        f"Manifesto de migracao: `{report['migration_manifest_status']}`",
        f"Hashes validos: `{report['migration_hash_valid']}`",
        f"Status geral: `{report['status']}`",
        "",
        "## Links internos",
        "",
        f"- Arquivos Markdown verificados: `{report['links']['checked_markdown_files']}`",
        f"- Links verificados: `{report['links']['total_links_checked']}`",
        f"- Links nao resolvidos na amostra: `{report['links']['unresolved_count_sampled']}`",
        "",
        "## Anexos",
        "",
        f"- Anexos encontrados: `{report['attachments']['attachments']}`",
        f"- Anexos vazios na amostra: `{report['attachments']['empty_count_sampled']}`",
        "",
        "## Plugins",
        "",
        f"- Plugins configurados: `{report['plugins']['configured_plugins']}`",
        f"- Pastas de plugin instaladas: `{report['plugins']['installed_plugin_dirs']}`",
        f"- Plugins sem pasta: `{report['plugins']['missing_plugin_dirs']}`",
        "",
        "## Observacao",
        "",
        "Validacao somente leitura. Nenhuma nota foi alterada.",
    ]
    if report["links"]["unresolved_sample"]:
        lines.extend(["", "## Amostra de links nao resolvidos", ""])
        lines.extend([f"- `{item['file']}` -> `[[{item['link']}]]`" for item in report["links"]["unresolved_sample"][:50]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", default=r"D:\ISIS_IA\ISIS\brain\cerebro_vivo")
    parser.add_argument("--manifest", default=r"D:\ISIS_IA\ISIS\logs\migration\migration_manifest.json")
    parser.add_argument("--report", default=r"D:\ISIS_IA\AURORA\reports\phase5_validation.md")
    parser.add_argument("--json-report", default=r"D:\ISIS_IA\AURORA\reports\phase5_validation.json")
    parser.add_argument("--max-link-files", type=int, default=5000)
    args = parser.parse_args()
    report = validate_migration(Path(args.vault), Path(args.manifest), args.max_link_files)
    Path(args.json_report).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(report, Path(args.report))
    print(json.dumps({"status": report["status"], "report": args.report, "json": args.json_report}, ensure_ascii=False))
    return 0 if report["status"] in {"validated", "warning"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
