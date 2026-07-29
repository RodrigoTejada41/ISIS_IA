from aurora.core.audit import AuditLogger
from aurora.integrations.obsidian import ObsidianConnector, ObsidianMetadataStore, parse_frontmatter


def test_parse_frontmatter_simple_yaml():
    data, body = parse_frontmatter("---\ntags: [isis, teste]\nactive: true\n---\ntexto")

    assert data["tags"] == ["isis", "teste"]
    assert data["active"] is True
    assert body.strip() == "texto"


def test_parse_frontmatter_recovers_list_after_empty_key():
    data, _ = parse_frontmatter("---\nitems:\n  - a\n  - b\n---\ntexto")

    assert data["items"] == ["a", "b"]


def test_obsidian_connector_extracts_metadata_and_backlinks(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "A.md").write_text("---\ntags: [front]\n---\n#body [[B]]\n- [x] feito\n- [ ] aberto", encoding="utf-8")
    (vault / "B.md").write_text("volta", encoding="utf-8")
    audit = AuditLogger(tmp_path / "audit.jsonl")

    notes = ObsidianConnector(vault, audit).scan()
    by_title = {note.title: note for note in notes}

    assert by_title["A"].tags == ["body", "front"]
    assert by_title["A"].links == ["B"]
    assert by_title["A"].checklist_total == 2
    assert by_title["A"].checklist_done == 1
    assert by_title["A"].path in by_title["B"].backlinks


def test_obsidian_metadata_store_versions(tmp_path):
    vault = tmp_path / "vault"
    note = vault / "A.md"
    vault.mkdir()
    note.write_text("v1", encoding="utf-8")
    audit = AuditLogger(tmp_path / "audit.jsonl")
    connector = ObsidianConnector(vault, audit)
    store = ObsidianMetadataStore(tmp_path / "obsidian.sqlite", audit)

    assert store.upsert_many(connector.scan())["created"] == 1
    assert store.upsert_many(connector.scan())["unchanged"] == 1
    note.write_text("v2 [[A]]", encoding="utf-8")
    assert store.upsert_many(connector.scan())["updated"] == 1
    assert store.stats()["notes"] == 1
