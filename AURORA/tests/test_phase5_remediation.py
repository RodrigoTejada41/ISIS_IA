from scripts.phase5_remediate_links import remediate_links


def test_remediate_trailing_qx_when_target_exists(tmp_path):
    vault = tmp_path / "vault"
    backup = tmp_path / "backup"
    (vault / "07_INDICES").mkdir(parents=True)
    (vault / "07_INDICES" / "indice-geral.md").write_text("ok", encoding="utf-8")
    note = vault / "README.md"
    note.write_text("[[07_INDICES/indice-geralQX|Alias]]", encoding="utf-8")

    report = remediate_links(vault, backup)

    assert report["replacements"] == 1
    assert "[[07_INDICES/indice-geral|Alias]]" in note.read_text(encoding="utf-8")
    assert any((backup / item).is_dir() for item in [p.name for p in backup.iterdir()])


def test_remediate_placeholder_to_alias_when_alias_exists(tmp_path):
    vault = tmp_path / "vault"
    backup = tmp_path / "backup"
    vault.mkdir()
    (vault / "Destino.md").write_text("ok", encoding="utf-8")
    note = vault / "README.md"
    note.write_text("[[QXTECHTOKENQX|Destino]]", encoding="utf-8")

    report = remediate_links(vault, backup)

    assert report["replacements"] == 1
    assert "[[Destino|Destino]]" in note.read_text(encoding="utf-8")
