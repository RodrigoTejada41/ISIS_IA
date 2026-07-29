# Configuracao

Arquivo gerado automaticamente:

```text
data/config.json
```

Campos principais:

- `profile`: perfil ativo.
- `voice`: idioma, wake word, engine STT/TTS e caminhos locais.
- `resource_limits`: RAM, VRAM, modelos simultaneos, tempo de permanencia.
- `models`: mapeamento de modelos para perfis.
- `allowed_folders`: pastas permitidas.
- `protected_folders`: pastas protegidas.
- `blocked_commands`: comandos bloqueados.
- `online_enabled`: deve permanecer `false` por padrao.

Nao armazene senhas, tokens ou chaves neste arquivo.
