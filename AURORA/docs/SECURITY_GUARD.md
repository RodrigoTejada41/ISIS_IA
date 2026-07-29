# Seguranca e Permissoes - Fase 15

Modulo:

```text
aurora.core.security.SecurityGuard
```

Estados:

- `ALLOWED`
- `DENIED`
- `ASK_ALWAYS`
- `ALLOWED_ONCE`
- `ALLOWED_SESSION`
- `ALLOWED_PERMANENT`

Validacoes:

- Caminho permitido.
- Pasta protegida.
- Comando bloqueado.
- Estado de permissao por chave.

CLI:

```powershell
python -m aurora.cli security-status
```

Estado atual:

- Pastas permitidas: `D:\ISIS_IA`.
- Pastas protegidas: `C:\Users`.
- Comandos bloqueados: `format`, `diskpart`, `reg delete`.

Limite:

Ainda nao intercepta toda execucao de sistema. Nesta fase, o guard foi conectado ao nucleo e exposto como ferramenta.
