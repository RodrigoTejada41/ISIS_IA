from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROBOCOPY_SUCCESS_MAX = 7


def bytes_to_gb(value: int) -> float:
    return round(value / 1024 / 1024 / 1024, 3)


def obsidian_running() -> bool:
    proc = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Obsidian.exe"], capture_output=True, text=True)
    return "Obsidian.exe" in proc.stdout


def robocopy_totals(source: Path, destination: Path) -> dict[str, int | str]:
    proc = subprocess.run(
        ["robocopy", str(source), str(destination), "/L", "/E", "/BYTES", "/NFL", "/NDL", "/NJH", "/R:0", "/W:0"],
        capture_output=True,
        text=True,
    )
    output = proc.stdout + proc.stderr
    dirs = re.search(r"Diret\S*rios:\s+(\d+)", output)
    files = re.search(r"Arquivos:\s+(\d+)", output)
    bytes_match = re.search(r"Bytes:\s+(\d+)", output)
    return {
        "exit_code": proc.returncode,
        "directories": int(dirs.group(1)) if dirs else -1,
        "files": int(files.group(1)) if files else -1,
        "bytes": int(bytes_match.group(1)) if bytes_match else -1,
        "raw": output,
    }


def run_backup(source: Path, backup_root: Path, min_free_gb: int = 40, allow_open_obsidian: bool = False) -> dict:
    source = source.resolve()
    backup_root = backup_root.resolve()
    if not source.exists():
        raise FileNotFoundError(source)
    if not (source / ".obsidian").exists():
        raise RuntimeError(f"obsidian vault marker not found: {source / '.obsidian'}")
    if obsidian_running() and not allow_open_obsidian:
        raise RuntimeError("Obsidian is running. Close it before backup.")

    source_totals = robocopy_totals(source, backup_root / "_dryrun_size_check")
    if source_totals["bytes"] < 0:
        raise RuntimeError("could not calculate source size with robocopy")

    usage = shutil.disk_usage(backup_root.anchor)
    required_free = int(source_totals["bytes"]) + min_free_gb * 1024 * 1024 * 1024
    if usage.free < required_free:
        raise RuntimeError(f"insufficient free space: {bytes_to_gb(usage.free)} GB available")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = backup_root / f"cerebro_vivo_backup_{stamp}"
    log_path = backup_root.parent.parent / "logs" / "migration" / f"phase3_backup_{stamp}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir(parents=True, exist_ok=False)

    cmd = [
        "robocopy",
        str(source),
        str(destination),
        "/E",
        "/COPY:DAT",
        "/DCOPY:DAT",
        "/R:2",
        "/W:1",
        "/MT:16",
        "/XJ",
        f"/LOG:{log_path}",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    copied_ok = proc.returncode <= ROBOCOPY_SUCCESS_MAX
    dest_totals = robocopy_totals(destination, backup_root / "_dryrun_dest_check")
    validated = (
        copied_ok
        and source_totals["files"] == dest_totals["files"]
        and source_totals["bytes"] == dest_totals["bytes"]
    )
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "destination": str(destination),
        "backup_root": str(backup_root),
        "obsidian_was_running": False,
        "min_free_gb": min_free_gb,
        "free_gb_before": bytes_to_gb(usage.free),
        "source_totals": source_totals,
        "destination_totals": dest_totals,
        "robocopy_exit_code": proc.returncode,
        "robocopy_success": copied_ok,
        "validated_by_count_and_size": validated,
        "log_path": str(log_path),
        "status": "validated" if validated else "failed",
        "notes": [
            "Backup uses copy only. It does not delete source files.",
            "No /MIR flag is used.",
            "Hash validation remains for the migration validation phase.",
        ],
    }
    manifest_path = destination / "backup_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def write_report(manifest: dict, path: Path) -> None:
    lines = [
        "# Fase 3 - Backup Inicial do CEREBRO VIVO",
        "",
        f"Data: {manifest['generated_at']}",
        f"Origem: `{manifest['source']}`",
        f"Destino: `{manifest['destination']}`",
        f"Espaco livre antes: `{manifest['free_gb_before']}` GB",
        f"Arquivos origem: `{manifest['source_totals']['files']}`",
        f"Bytes origem: `{manifest['source_totals']['bytes']}`",
        f"Arquivos destino: `{manifest['destination_totals']['files']}`",
        f"Bytes destino: `{manifest['destination_totals']['bytes']}`",
        f"Robocopy exit code: `{manifest['robocopy_exit_code']}`",
        f"Validado por contagem e tamanho: `{manifest['validated_by_count_and_size']}`",
        f"Status: `{manifest['status']}`",
        "",
        "## Logs",
        "",
        f"- `{manifest['log_path']}`",
        "",
        "## Garantias",
        "",
        "- Origem nao foi apagada.",
        "- Origem nao foi movida.",
        "- Backup nao usou `/MIR`.",
        "- Validacao por hash completo fica para a fase de migracao/validacao.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=r"E:\Projetos\CEREBRO_VIVO")
    parser.add_argument("--backup-root", default=r"D:\ISIS_IA\ISIS\backups\manual")
    parser.add_argument("--report", default=r"D:\ISIS_IA\AURORA\reports\phase3_backup.md")
    parser.add_argument("--min-free-gb", type=int, default=40)
    parser.add_argument("--allow-open-obsidian", action="store_true")
    args = parser.parse_args()

    manifest = run_backup(Path(args.source), Path(args.backup_root), args.min_free_gb, args.allow_open_obsidian)
    write_report(manifest, Path(args.report))
    print(json.dumps({"status": manifest["status"], "destination": manifest["destination"], "report": args.report}, ensure_ascii=False))
    return 0 if manifest["status"] == "validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
