from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ATTACHMENT_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".docx",
    ".xlsx",
    ".pptx",
    ".mp3",
    ".wav",
    ".mp4",
    ".zip",
}

SKIP_CONTENT_DIRS = {".git", "__pycache__", ".pytest_cache", ".tmp_codex_memory", ".tmp_main_nexus_validation", "node_modules", ".venv"}


def drive_usage(path: Path) -> dict[str, int | str]:
    usage = shutil.disk_usage(path.anchor or path)
    return {
        "root": path.anchor,
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,
    }


def safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"error": str(exc)}


def classify_markdown(text: str) -> str:
    lower = text.lower()
    if "bug" in lower or "erro" in lower:
        return "Bug"
    if "solução" in lower or "solucao" in lower:
        return "Solucao"
    if "decisão" in lower or "decisao" in lower or "adr" in lower:
        return "Decisao"
    if "prompt" in lower:
        return "Prompt"
    if "requisito" in lower:
        return "Requisito"
    if "arquitetura" in lower:
        return "Arquitetura"
    if "tarefa" in lower or "- [ ]" in lower or "- [x]" in lower:
        return "Tarefa"
    if "ideia" in lower:
        return "Ideia"
    return "Documentacao"


def extract_frontmatter(text: str) -> str | None:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[3:end].strip()
    return None


def audit_vault(vault: Path, max_seconds: int = 90, max_markdown_bytes: int = 200_000, max_files: int = 20_000) -> dict[str, Any]:
    started = time.monotonic()
    result: dict[str, Any] = {
        "path": str(vault),
        "exists": vault.exists(),
        "obsidian_dir": str(vault / ".obsidian"),
        "has_obsidian_dir": (vault / ".obsidian").exists(),
        "total_files": 0,
        "total_dirs": 0,
        "total_bytes": 0,
        "markdown_files": 0,
        "attachments": 0,
        "attachment_bytes": 0,
        "extensions": {},
        "plugins": [],
        "tags_top": [],
        "links_count": 0,
        "frontmatter_files": 0,
        "categories": {},
        "projects_identified": [],
        "duplicate_names": [],
        "duplicate_size_groups": 0,
        "errors": [],
        "status": "complete",
        "stopped_reason": None,
    }
    if not vault.exists():
        return result

    extension_counter: Counter[str] = Counter()
    tag_counter: Counter[str] = Counter()
    category_counter: Counter[str] = Counter()
    file_names: defaultdict[str, list[str]] = defaultdict(list)
    size_groups: defaultdict[int, list[str]] = defaultdict(list)
    projects: set[str] = set()
    link_count = 0
    frontmatter_count = 0

    for root, dirs, files in os.walk(vault):
        dirs[:] = [item for item in dirs if item not in SKIP_CONTENT_DIRS]
        if time.monotonic() - started > max_seconds:
            result["status"] = "partial"
            result["stopped_reason"] = f"time budget exceeded: {max_seconds}s"
            break
        root_path = Path(root)
        result["total_dirs"] += len(dirs)
        if root_path.name.lower() in {"projetos", "projects"}:
            projects.update(d.name for d in root_path.iterdir() if d.is_dir())
        for name in files:
            if result["total_files"] >= max_files:
                result["status"] = "partial"
                result["stopped_reason"] = f"file budget exceeded: {max_files}"
                break
            path = root_path / name
            try:
                stat = path.stat()
                size = stat.st_size
                suffix = path.suffix.lower() or "<no_ext>"
                result["total_files"] += 1
                result["total_bytes"] += size
                extension_counter[suffix] += 1
                file_names[name.lower()].append(str(path))
                size_groups[size].append(str(path))
                if suffix in ATTACHMENT_EXTS:
                    result["attachments"] += 1
                    result["attachment_bytes"] += size
                if suffix == ".md":
                    result["markdown_files"] += 1
                    with path.open("rb") as fh:
                        text = fh.read(max_markdown_bytes).decode("utf-8", errors="ignore")
                    if extract_frontmatter(text):
                        frontmatter_count += 1
                    tag_counter.update(re.findall(r"(?<!\w)#([\w\-/]+)", text, flags=re.UNICODE))
                    link_count += len(re.findall(r"\[\[([^\]]+)\]\]", text))
                    category_counter[classify_markdown(text)] += 1
                    if "projeto" in text.lower() or "project" in text.lower():
                        projects.add(path.parent.name)
            except Exception as exc:
                result["errors"].append({"path": str(path), "error": str(exc)})
        if result["status"] == "partial":
            break

    plugins_path = vault / ".obsidian" / "community-plugins.json"
    if plugins_path.exists():
        plugins = safe_read_json(plugins_path)
        result["plugins"] = plugins if isinstance(plugins, list) else [plugins]

    result["extensions"] = dict(extension_counter.most_common())
    result["tags_top"] = tag_counter.most_common(50)
    result["links_count"] = link_count
    result["frontmatter_files"] = frontmatter_count
    result["categories"] = dict(category_counter)
    result["projects_identified"] = sorted(projects)
    result["duplicate_names"] = [
        {"name": name, "paths": paths[:10], "count": len(paths)}
        for name, paths in file_names.items()
        if len(paths) > 1
    ][:50]
    result["duplicate_size_groups"] = sum(1 for paths in size_groups.values() if len(paths) > 1)
    result["duration_seconds"] = round(time.monotonic() - started, 3)
    return result


def write_markdown(report: dict[str, Any], path: Path) -> None:
    vault = report["cerebro_vivo"]
    lines = [
        "# Auditoria Fase 1 - ISIS e CEREBRO VIVO",
        "",
        f"Data: {report['generated_at']}",
        "",
        "## Estado atual da ISIS",
        "",
        f"- Pasta analisada: `{report['isis_project']['path']}`",
        f"- Existe: `{report['isis_project']['exists']}`",
        f"- Arquivos: `{report['isis_project']['files']}`",
        f"- Tamanho: `{report['isis_project']['bytes']}` bytes",
        "",
        "## Unidades",
        "",
    ]
    for item in report["drives"]:
        lines.append(f"- `{item['root']}` total={item['total_bytes']} usado={item['used_bytes']} livre={item['free_bytes']}")
    lines.extend(
        [
            "",
            "## Estado atual do CEREBRO VIVO",
            "",
            f"- Localizacao atual: `{vault['path']}`",
            f"- Status da auditoria: `{vault['status']}`",
            f"- Motivo de parada: `{vault['stopped_reason']}`",
            f"- Existe: `{vault['exists']}`",
            f"- Pasta .obsidian: `{vault['has_obsidian_dir']}`",
            f"- Tamanho total: `{vault['total_bytes']}` bytes",
            f"- Quantidade de arquivos: `{vault['total_files']}`",
            f"- Quantidade de pastas: `{vault['total_dirs']}`",
            f"- Markdown: `{vault['markdown_files']}`",
            f"- Anexos: `{vault['attachments']}`",
            f"- Tamanho dos anexos: `{vault['attachment_bytes']}` bytes",
            f"- Links internos encontrados: `{vault['links_count']}`",
            f"- Arquivos com YAML frontmatter: `{vault['frontmatter_files']}`",
            "",
            "## Plugins encontrados",
            "",
        ]
    )
    lines.extend([f"- `{plugin}`" for plugin in vault["plugins"]] or ["- Nenhum plugin comunitario identificado."])
    lines.extend(["", "## Projetos identificados", ""])
    lines.extend([f"- {project}" for project in vault["projects_identified"]] or ["- Nenhum projeto identificado por regra simples."])
    lines.extend(["", "## Extensoes", ""])
    lines.extend([f"- `{ext}`: {count}" for ext, count in vault["extensions"].items()])
    lines.extend(["", "## Categorias Markdown", ""])
    lines.extend([f"- {cat}: {count}" for cat, count in vault["categories"].items()] or ["- Nenhuma categoria detectada."])
    lines.extend(["", "## Tags principais", ""])
    lines.extend([f"- #{tag}: {count}" for tag, count in vault["tags_top"][:20]] or ["- Nenhuma tag detectada."])
    lines.extend(["", "## Problemas", ""])
    lines.extend([f"- `{err['path']}`: {err['error']}" for err in vault["errors"][:50]] or ["- Nenhum erro de leitura registrado."])
    lines.extend(
        [
            "",
            "## Riscos",
            "",
            "- Nao migrar por recorte direto.",
            "- Nao apagar o cofre original.",
            "- Nao alterar Markdown, links ou plugins na Fase 1.",
            "- Validar hashes antes de qualquer troca de cofre.",
            "- Reservar espaco no SSD para modelos, banco vetorial, logs, backups e cache.",
            "",
            "## Duplicidades",
            "",
            f"- Grupos por mesmo tamanho: `{vault['duplicate_size_groups']}`",
            f"- Nomes duplicados listados: `{len(vault['duplicate_names'])}`",
            "",
            "## Recomendacoes",
            "",
            "- Confirmar manualmente que `D:` e o SSD dedicado da ISIS.",
            "- Confirmar que `E:` e o HD de origem do CEREBRO VIVO.",
            "- Fechar Obsidian antes da futura migracao.",
            "- Criar backup completo antes de copiar.",
            "- Usar manifestos com hashes na Fase 3/4.",
            "",
            "## Plano de migracao",
            "",
            "1. Confirmar origem e destino.",
            "2. Verificar Obsidian fechado.",
            "3. Criar backup completo.",
            "4. Gerar manifesto com hashes.",
            "5. Copiar para SSD sem apagar origem.",
            "6. Recalcular hashes no destino.",
            "7. Comparar origem/destino.",
            "8. Validar links, anexos e plugins.",
            "9. Somente entao apontar Obsidian para o novo cofre.",
            "",
            "## Plano de implementacao",
            "",
            "1. Fase 2: criar estrutura SSD.",
            "2. Fase 3: backup inicial.",
            "3. Fase 4: migracao segura.",
            "4. Fase 5: validacao.",
            "5. Fase 6: configuracao central.",
            "",
            "## Observacao",
            "",
            "Nenhum arquivo do CEREBRO VIVO foi movido, apagado ou modificado nesta auditoria.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def count_project(path: Path) -> dict[str, Any]:
    files = 0
    total = 0
    for root, _, names in os.walk(path):
        for name in names:
            p = Path(root) / name
            try:
                files += 1
                total += p.stat().st_size
            except OSError:
                pass
    return {"path": str(path), "exists": path.exists(), "files": files, "bytes": total}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--isis-project", default=r"D:\ISIS_IA\AURORA")
    parser.add_argument("--vault", default=r"E:\Projetos\CEREBRO_VIVO")
    parser.add_argument("--report-dir", default=r"D:\ISIS_IA\AURORA\reports")
    parser.add_argument("--max-seconds", type=int, default=90)
    parser.add_argument("--max-files", type=int, default=20000)
    args = parser.parse_args()

    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "isis_project": count_project(Path(args.isis_project)),
        "cerebro_vivo": audit_vault(Path(args.vault), args.max_seconds, max_files=args.max_files),
        "drives": [drive_usage(Path(root)) for root in ["C:\\", "D:\\", "E:\\", "H:\\", "K:\\"] if Path(root).exists()],
    }
    json_path = report_dir / "phase1_audit.json"
    md_path = report_dir / "phase1_audit.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, md_path)
    print(json.dumps({"json": str(json_path), "markdown": str(md_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
