from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.phase5_validate_migrated_vault import link_exists, note_stems, validate_migration, write_report as write_validation_report


LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
PLACEHOLDERS = {"QXTECHTOKENQX", "`novo`", "`novo`QX", "`novo`AQX"}


def split_link(raw: str) -> tuple[str, str | None]:
    if "|" not in raw:
        return raw.strip(), None
    target, alias = raw.split("|", 1)
    return target.strip(), alias.strip()


def candidate_targets(target: str, alias: str | None) -> list[str]:
    candidates: list[str] = []
    normalized = target.strip()
    if normalized.endswith("QX"):
        candidates.append(normalized[:-2])
    if normalized in PLACEHOLDERS and alias:
        candidates.append(alias)
    if normalized.startswith("`") and normalized.endswith("`") and alias:
        candidates.append(alias)
    if normalized.endswith("QX") and alias:
        candidates.append(alias)
    return [item for item in candidates if item and item != target]


def remediate_links(vault: Path, backup_root: Path, dry_run: bool = False) -> dict:
    vault = vault.resolve()
    backup_root = backup_root.resolve()
    stems = note_stems(vault)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / f"phase5_link_remediation_{stamp}"
    changed_files: list[dict] = []
    unresolved_seen = 0
    replacements_total = 0

    for md in vault.rglob("*.md"):
        original = md.read_text(encoding="utf-8", errors="ignore")
        replacements: list[dict[str, str]] = []

        def replace(match: re.Match[str]) -> str:
            nonlocal unresolved_seen, replacements_total
            raw = match.group(1)
            target, alias = split_link(raw)
            if link_exists(vault, md, target, stems):
                return match.group(0)
            unresolved_seen += 1
            for candidate in candidate_targets(target, alias):
                if link_exists(vault, md, candidate, stems):
                    new_raw = f"{candidate}|{alias}" if alias else candidate
                    replacements.append({"old": raw, "new": new_raw})
                    replacements_total += 1
                    return f"[[{new_raw}]]"
            return match.group(0)

        updated = LINK_RE.sub(replace, original)
        if updated != original:
            relative = md.relative_to(vault)
            backup_path = backup_dir / relative
            changed_files.append({"file": str(md), "backup": str(backup_path), "replacements": replacements})
            if not dry_run:
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(md, backup_path)
                md.write_text(updated, encoding="utf-8")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "vault": str(vault),
        "backup_dir": str(backup_dir),
        "dry_run": dry_run,
        "unresolved_seen": unresolved_seen,
        "files_changed": len(changed_files),
        "replacements": replacements_total,
        "changed_files": changed_files,
        "status": "dry_run" if dry_run else "completed",
    }
    backup_root.mkdir(parents=True, exist_ok=True)
    (backup_root / f"phase5_link_remediation_{stamp}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def write_report(report: dict, path: Path) -> None:
    lines = [
        "# Fase 5 - Correcao Controlada de Links",
        "",
        f"Data: {report['generated_at']}",
        f"Cofre: `{report['vault']}`",
        f"Backup dos arquivos alterados: `{report['backup_dir']}`",
        f"Dry run: `{report['dry_run']}`",
        f"Links nao resolvidos vistos: `{report['unresolved_seen']}`",
        f"Arquivos alterados: `{report['files_changed']}`",
        f"Links corrigidos: `{report['replacements']}`",
        f"Status: `{report['status']}`",
        "",
        "## Regra aplicada",
        "",
        "- Corrigir somente quando o novo alvo existir.",
        "- Remover sufixo `QX` somente se o alvo sem `QX` existir.",
        "- Trocar placeholders pelo alias somente se o alias existir como nota/caminho.",
        "- Criar backup antes de editar cada arquivo.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", default=r"D:\ISIS_IA\ISIS\brain\cerebro_vivo")
    parser.add_argument("--backup-root", default=r"D:\ISIS_IA\ISIS\backups\manual")
    parser.add_argument("--report", default=r"D:\ISIS_IA\AURORA\reports\phase5_link_remediation.md")
    parser.add_argument("--validation-report", default=r"D:\ISIS_IA\AURORA\reports\phase5_validation_after_remediation.md")
    parser.add_argument("--validation-json", default=r"D:\ISIS_IA\AURORA\reports\phase5_validation_after_remediation.json")
    parser.add_argument("--manifest", default=r"D:\ISIS_IA\ISIS\logs\migration\migration_manifest.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    report = remediate_links(Path(args.vault), Path(args.backup_root), args.dry_run)
    write_report(report, Path(args.report))
    if not args.dry_run:
        validation = validate_migration(Path(args.vault), Path(args.manifest))
        Path(args.validation_json).write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
        write_validation_report(validation, Path(args.validation_report))
    print(json.dumps({"status": report["status"], "replacements": report["replacements"], "report": args.report}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
