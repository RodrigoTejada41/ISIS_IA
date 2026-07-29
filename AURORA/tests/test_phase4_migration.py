from scripts.phase4_migrate_cerebro_vivo import build_hash_index, compare_hashes, migrate


def test_hash_compare_detects_match_and_change(tmp_path):
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    source.mkdir()
    dest.mkdir()
    (source / "a.md").write_text("a", encoding="utf-8")
    (dest / "a.md").write_text("a", encoding="utf-8")

    assert compare_hashes(build_hash_index(source), build_hash_index(dest))["valid"] is True

    (dest / "a.md").write_text("b", encoding="utf-8")
    assert compare_hashes(build_hash_index(source), build_hash_index(dest))["valid"] is False


def test_phase4_migration_validates_small_vault(tmp_path):
    source = tmp_path / "source"
    backup = tmp_path / "backup"
    destination = tmp_path / "destination"
    logs = tmp_path / "logs"
    (source / ".obsidian").mkdir(parents=True)
    (backup / ".obsidian").mkdir(parents=True)
    (source / "note.md").write_text("[[x]]", encoding="utf-8")
    (backup / "note.md").write_text("[[x]]", encoding="utf-8")

    manifest = migrate(source, destination, backup, logs, min_free_gb=0, allow_open_obsidian=True)

    assert manifest["status"] == "validated"
    assert manifest["comparison"]["valid"] is True
    assert (logs / "migration_manifest.json").exists()
