from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aurora.core.audit import AuditLogger
from aurora.integrations.obsidian import ObsidianConnector, ObsidianMetadataStore


def write_report(payload: dict, path: Path) -> None:
    lines = [
        "# Fase 10 - Integracao Obsidian READ_ONLY",
        "",
        f"Cofre: `{payload['vault']}`",
        f"Banco: `{payload['database']}`",
        f"Arquivos escaneados: `{payload['scan']['notes']}`",
        f"Criados: `{payload['store']['created']}`",
        f"Atualizados: `{payload['store']['updated']}`",
        f"Inalterados: `{payload['store']['unchanged']}`",
        f"Checklists: `{payload['stats']['checklist_total']}`",
        f"Checklists concluidos: `{payload['stats']['checklist_done']}`",
        f"Status: `{payload['status']}`",
        "",
        "Garantia: leitura do cofre, escrita apenas no banco/relatorios da ISIS.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", default=r"D:\ISIS_IA\ISIS\brain\cerebro_vivo")
    parser.add_argument("--database", default=r"D:\ISIS_IA\ISIS\data\databases\obsidian_readonly.sqlite")
    parser.add_argument("--audit", default=r"D:\ISIS_IA\ISIS\logs\audit\obsidian_readonly.jsonl")
    parser.add_argument("--report", default=r"D:\ISIS_IA\AURORA\reports\phase10_obsidian_readonly.md")
    parser.add_argument("--json-report", default=r"D:\ISIS_IA\AURORA\reports\phase10_obsidian_readonly.json")
    parser.add_argument("--max-files", type=int)
    args = parser.parse_args()
    audit = AuditLogger(args.audit)
    notes = ObsidianConnector(args.vault, audit).scan(args.max_files)
    store = ObsidianMetadataStore(args.database, audit)
    store_result = store.upsert_many(notes)
    payload = {
        "vault": args.vault,
        "database": args.database,
        "scan": {"notes": len(notes)},
        "store": store_result,
        "stats": store.stats(),
        "status": "indexed",
    }
    Path(args.json_report).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(payload, Path(args.report))
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
