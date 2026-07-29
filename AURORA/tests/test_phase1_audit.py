import json

from scripts.phase1_audit import audit_vault, main


def test_audit_vault_detects_obsidian_metadata(tmp_path):
    vault = tmp_path / "CEREBRO_VIVO"
    (vault / ".obsidian").mkdir(parents=True)
    (vault / ".obsidian" / "community-plugins.json").write_text('["dataview"]', encoding="utf-8")
    (vault / "Projeto.md").write_text("---\ntags: [isis]\n---\n#projeto [[Decisao]] bug solucao", encoding="utf-8")
    (vault / "image.png").write_bytes(b"png")

    report = audit_vault(vault)

    assert report["has_obsidian_dir"] is True
    assert report["markdown_files"] == 1
    assert report["attachments"] == 1
    assert report["plugins"] == ["dataview"]
    assert report["links_count"] == 1


def test_phase1_main_writes_reports(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    project = tmp_path / "isis"
    vault.mkdir()
    project.mkdir()
    (vault / ".obsidian").mkdir()
    (vault / "note.md").write_text("conteudo", encoding="utf-8")
    report_dir = tmp_path / "reports"

    monkeypatch.setattr(
        "sys.argv",
        [
            "phase1_audit.py",
            "--isis-project",
            str(project),
            "--vault",
            str(vault),
            "--report-dir",
            str(report_dir),
        ],
    )

    assert main() == 0
    assert json.loads((report_dir / "phase1_audit.json").read_text(encoding="utf-8"))["cerebro_vivo"]["total_files"] == 1
    assert (report_dir / "phase1_audit.md").exists()
