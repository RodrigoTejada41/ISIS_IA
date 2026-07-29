from scripts.phase2_create_ssd_structure import ISIS_DIRS, create_structure


def test_create_structure_is_idempotent(tmp_path):
    root = tmp_path / "ISIS"

    first = create_structure(root, min_free_gb=0)
    second = create_structure(root, min_free_gb=0)

    assert first["created_count"] == len(ISIS_DIRS)
    assert second["created_count"] == 0
    assert (root / "app" / "core").is_dir()
    assert (root / "brain" / "cerebro_vivo").is_dir()
    assert (root / "config" / "phase2_structure_manifest.json").exists()
