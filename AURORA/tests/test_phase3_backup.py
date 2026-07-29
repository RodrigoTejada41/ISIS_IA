from scripts.phase3_backup_cerebro_vivo import robocopy_totals, run_backup


def test_phase3_backup_copies_and_validates_small_vault(tmp_path):
    source = tmp_path / "CEREBRO_VIVO"
    backup_root = tmp_path / "ISIS" / "backups" / "manual"
    (source / ".obsidian").mkdir(parents=True)
    (source / "nota.md").write_text("conteudo", encoding="utf-8")

    manifest = run_backup(source, backup_root, min_free_gb=0, allow_open_obsidian=True)

    assert manifest["status"] == "validated"
    assert manifest["source_totals"]["files"] == manifest["destination_totals"]["files"]
    assert manifest["source_totals"]["bytes"] == manifest["destination_totals"]["bytes"]


def test_robocopy_totals_reads_file_count(tmp_path):
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    source.mkdir()
    (source / "a.txt").write_text("a", encoding="utf-8")

    totals = robocopy_totals(source, dest)

    assert totals["files"] == 1
