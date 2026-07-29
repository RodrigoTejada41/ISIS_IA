import json

from scripts.phase5_validate_migrated_vault import validate_migration


def test_phase5_validates_basic_vault(tmp_path):
    vault = tmp_path / "vault"
    manifest = tmp_path / "manifest.json"
    (vault / ".obsidian").mkdir(parents=True)
    (vault / ".obsidian" / "community-plugins.json").write_text("[]", encoding="utf-8")
    (vault / "Nota.md").write_text("[[Outra]]", encoding="utf-8")
    (vault / "Outra.md").write_text("ok", encoding="utf-8")
    (vault / "anexo.png").write_bytes(b"x")
    manifest.write_text(json.dumps({"status": "validated", "comparison": {"valid": True}}), encoding="utf-8")

    report = validate_migration(vault, manifest)

    assert report["status"] == "validated"
    assert report["links"]["unresolved_count_sampled"] == 0
    assert report["attachments"]["attachments"] == 1


def test_phase5_reports_unresolved_link_as_warning(tmp_path):
    vault = tmp_path / "vault"
    manifest = tmp_path / "manifest.json"
    (vault / ".obsidian").mkdir(parents=True)
    (vault / "Nota.md").write_text("[[Ausente]]", encoding="utf-8")
    manifest.write_text(json.dumps({"status": "validated", "comparison": {"valid": True}}), encoding="utf-8")

    report = validate_migration(vault, manifest)

    assert report["status"] == "warning"
    assert report["links"]["unresolved_count_sampled"] == 1


def test_phase5_resolves_relative_folder_links(tmp_path):
    vault = tmp_path / "vault"
    manifest = tmp_path / "manifest.json"
    (vault / ".obsidian").mkdir(parents=True)
    (vault / "00_PAINEL").mkdir()
    (vault / "03_SNIPPETS").mkdir()
    (vault / "00_PAINEL" / "INICIO.md").write_text("[[../03_SNIPPETS|Snippets]]", encoding="utf-8")
    manifest.write_text(json.dumps({"status": "validated", "comparison": {"valid": True}}), encoding="utf-8")

    report = validate_migration(vault, manifest)

    assert report["links"]["unresolved_count_sampled"] == 0
