from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROBOCOPY_SUCCESS_MAX = 7
MANIFEST_NAME = "migration_manifest.json"


def bytes_to_gb(value: int) -> float:
    return round(value / 1024 / 1024 / 1024, 3)


def obsidian_running() -> bool:
    proc = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Obsidian.exe"], capture_output=True, text=True)
    return "Obsidian.exe" in proc.stdout


def robocopy_totals(source: Path, destination: Path) -> dict:
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
    }


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_hash_index(root: Path) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name == MANIFEST_NAME:
            continue
        relative = str(path.relative_to(root)).replace("/", "\\")
        stat = path.stat()
        index[relative] = {
            "sha256": sha256_file(path),
            "bytes": stat.st_size,
            "modified_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        }
    return index


def compare_hashes(source_hashes: dict[str, dict], destination_hashes: dict[str, dict]) -> dict:
    source_keys = set(source_hashes)
    destination_keys = set(destination_hashes)
    missing_in_destination = sorted(source_keys - destination_keys)
    extra_in_destination = sorted(destination_keys - source_keys)
    changed = sorted(
        key
        for key in source_keys & destination_keys
        if source_hashes[key]["sha256"] != destination_hashes[key]["sha256"]
        or source_hashes[key]["bytes"] != destination_hashes[key]["bytes"]
    )
    return {
        "missing_in_destination": missing_in_destination,
        "extra_in_destination": extra_in_destination,
        "changed": changed,
        "matched_files": len(source_keys & destination_keys) - len(changed),
        "valid": not missing_in_destination and not extra_in_destination and not changed,
    }


def destination_has_files(destination: Path) -> bool:
    if not destination.exists():
        return False
    return any(path.is_file() for path in destination.rglob("*"))


def migrate(
    source: Path,
    destination: Path,
    backup_path: Path,
    logs_dir: Path,
    min_free_gb: int = 40,
    allow_existing: bool = False,
    allow_open_obsidian: bool = False,
) -> dict:
    source = source.resolve()
    destination = destination.resolve()
    backup_path = backup_path.resolve()
    logs_dir = logs_dir.resolve()
    if not source.exists():
        raise FileNotFoundError(source)
    if not backup_path.exists():
        raise FileNotFoundError(backup_path)
    if not (source / ".obsidian").exists():
        raise RuntimeError("source is not an Obsidian vault")
    if obsidian_running() and not allow_open_obsidian:
        raise RuntimeError("Obsidian is running. Close it before migration.")
    if destination_has_files(destination) and not allow_existing:
        raise RuntimeError(f"destination already has files: {destination}")

    source_totals = robocopy_totals(source, destination / "_dryrun_size_check")
    backup_totals = robocopy_totals(backup_path, destination / "_dryrun_backup_check")
    usage = shutil.disk_usage(destination.anchor)
    required = int(source_totals["bytes"]) + min_free_gb * 1024 * 1024 * 1024
    if usage.free < required:
        raise RuntimeError(f"insufficient free space: {bytes_to_gb(usage.free)} GB available")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"phase4_migration_{stamp}.log"
    destination.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
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
        ],
        capture_output=True,
        text=True,
    )
    copied_ok = proc.returncode <= ROBOCOPY_SUCCESS_MAX
    destination_totals = robocopy_totals(destination, destination / "_dryrun_destination_check")
    source_hashes = build_hash_index(source)
    destination_hashes = build_hash_index(destination)
    comparison = compare_hashes(source_hashes, destination_hashes)
    valid = (
        copied_ok
        and source_totals["files"] == destination_totals["files"]
        and source_totals["bytes"] == destination_totals["bytes"]
        and comparison["valid"]
    )
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "destination": str(destination),
        "backup_path": str(backup_path),
        "logs_dir": str(logs_dir),
        "log_path": str(log_path),
        "min_free_gb": min_free_gb,
        "free_gb_before": bytes_to_gb(usage.free),
        "source_totals": source_totals,
        "backup_totals": backup_totals,
        "destination_totals": destination_totals,
        "robocopy_exit_code": proc.returncode,
        "robocopy_success": copied_ok,
        "hash_algorithm": "sha256",
        "source_hashes": source_hashes,
        "destination_hashes": destination_hashes,
        "comparison": comparison,
        "status": "validated" if valid else "failed",
        "notes": [
            "Migration is copy-only and does not delete or move the source vault.",
            "No /MIR flag is used.",
            "Do not point Obsidian to the destination until manual validation is complete.",
        ],
    }
    manifest_path = logs_dir / MANIFEST_NAME
    stamped_manifest_path = logs_dir / f"migration_manifest_{stamp}.json"
    payload = json.dumps(manifest, ensure_ascii=False, indent=2)
    manifest_path.write_text(payload, encoding="utf-8")
    stamped_manifest_path.write_text(payload, encoding="utf-8")
    return manifest


def write_report(manifest: dict, path: Path) -> None:
    comparison = manifest["comparison"]
    lines = [
        "# Fase 4 - Migracao Segura do CEREBRO VIVO",
        "",
        f"Data: {manifest['generated_at']}",
        f"Origem: `{manifest['source']}`",
        f"Destino: `{manifest['destination']}`",
        f"Backup usado: `{manifest['backup_path']}`",
        f"Espaco livre antes: `{manifest['free_gb_before']}` GB",
        f"Arquivos origem: `{manifest['source_totals']['files']}`",
        f"Bytes origem: `{manifest['source_totals']['bytes']}`",
        f"Arquivos destino: `{manifest['destination_totals']['files']}`",
        f"Bytes destino: `{manifest['destination_totals']['bytes']}`",
        f"Robocopy exit code: `{manifest['robocopy_exit_code']}`",
        f"Hashes comparados: `{len(manifest['source_hashes'])}`",
        f"Arquivos iguais por hash: `{comparison['matched_files']}`",
        f"Ausentes no destino: `{len(comparison['missing_in_destination'])}`",
        f"Extras no destino: `{len(comparison['extra_in_destination'])}`",
        f"Alterados: `{len(comparison['changed'])}`",
        f"Status: `{manifest['status']}`",
        "",
        "## Logs e manifestos",
        "",
        f"- Log: `{manifest['log_path']}`",
        f"- Manifesto: `{Path(manifest['logs_dir']) / MANIFEST_NAME}`",
        "",
        "## Garantias",
        "",
        "- Origem nao foi apagada.",
        "- Origem nao foi movida.",
        "- Migracao nao usou `/MIR`.",
        "- Obsidian ainda nao foi apontado para o novo local.",
        "",
        "## Proxima fase",
        "",
        "Fase 5: validacao manual do cofre migrado, anexos, links e plugins.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=r"E:\Projetos\CEREBRO_VIVO")
    parser.add_argument("--destination", default=r"D:\ISIS_IA\ISIS\brain\cerebro_vivo")
    parser.add_argument("--backup", default=r"D:\ISIS_IA\ISIS\backups\manual\cerebro_vivo_backup_20260728_153131")
    parser.add_argument("--logs-dir", default=r"D:\ISIS_IA\ISIS\logs\migration")
    parser.add_argument("--report", default=r"D:\ISIS_IA\AURORA\reports\phase4_migration.md")
    parser.add_argument("--min-free-gb", type=int, default=40)
    parser.add_argument("--allow-existing", action="store_true")
    parser.add_argument("--allow-open-obsidian", action="store_true")
    args = parser.parse_args()
    manifest = migrate(
        Path(args.source),
        Path(args.destination),
        Path(args.backup),
        Path(args.logs_dir),
        args.min_free_gb,
        args.allow_existing,
        args.allow_open_obsidian,
    )
    write_report(manifest, Path(args.report))
    print(json.dumps({"status": manifest["status"], "destination": manifest["destination"], "report": args.report}, ensure_ascii=False))
    return 0 if manifest["status"] == "validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
