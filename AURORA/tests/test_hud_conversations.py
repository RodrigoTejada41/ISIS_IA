from aurora.core.conversations import ConversationStore, StoredMessage


def test_conversation_store_persists_project_conversation_and_messages(tmp_path):
    store = ConversationStore(tmp_path / "hud.sqlite")
    project_id = store.ensure_project("Projeto X", objective="Construir interface")
    conversation_id = store.start_conversation("Criar tela de projetos", project_id=project_id, model="qwen3-coder:30b")

    store.add_message(conversation_id, StoredMessage("user", "Criar tela de projetos"))
    store.add_message(conversation_id, StoredMessage("assistant", "Tela criada.", model="qwen3-coder:30b", metadata={"duration_ms": 10}))

    projects = store.list_projects()
    conversations = store.list_conversations()
    conversation = store.get_conversation(conversation_id)

    assert projects[0]["name"] == "Projeto X"
    assert conversations[0]["message_count"] == 2
    assert conversation is not None
    assert conversation["messages"][1]["model"] == "qwen3-coder:30b"


def test_conversation_store_searches_projects_conversations_and_messages(tmp_path):
    store = ConversationStore(tmp_path / "hud.sqlite")
    project_id = store.ensure_project("ISIS HUD", description="Interface local")
    conversation_id = store.start_conversation("Corrigir travamento", project_id=project_id)
    store.add_message(conversation_id, StoredMessage("assistant", "Corrigido com job assincrono."))

    result = store.search("assincrono")

    assert result["messages"]
    assert result["conversations"]
