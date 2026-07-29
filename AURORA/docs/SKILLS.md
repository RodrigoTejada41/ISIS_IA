# Habilidades

Estrutura:

```text
data/skills/nome_da_habilidade/
  skill.json
  main.py
  permissions.json
  README.md
  CHANGELOG.md
  tests/
  versions/
```

Manifesto validado por Pydantic:

- id
- name
- display_name
- description
- version
- author
- entrypoint
- inputs
- outputs
- supported_platforms
- minimum_aurora_version
- permissions
- risk_level
- requires_confirmation
- timeout_seconds
- enabled
- checksum

Habilidades iniciais:

- `installed_programs`
- `system_info`
- `file_search`
- `project_list`
- `read_text_file`
- `ollama_status`
- `local_models`
- `document_summary`
- `note_create`
- `note_search`
