# Backup - Fase 3

Backup inicial criado:

```text
D:\ISIS_IA\ISIS\backups\manual\cerebro_vivo_backup_20260728_153131
```

Origem:

```text
E:\Projetos\CEREBRO_VIVO
```

Manifesto:

```text
D:\ISIS_IA\ISIS\backups\manual\cerebro_vivo_backup_20260728_153131\backup_manifest.json
```

Log:

```text
D:\ISIS_IA\ISIS\logs\migration\phase3_backup_20260728_153131.log
```

Resultado:

- Arquivos origem: 203112.
- Arquivos destino: 203112.
- Bytes origem: 5286560147.
- Bytes destino: 5286560147.
- Diretorios origem: 12309.
- Diretorios destino: 12309.
- `robocopy` exit code: 1.
- Status: validado por contagem e tamanho.

Garantias:

- Nao usou `/MIR`.
- Nao apagou origem.
- Nao moveu origem.
- Nao alterou o cofre original.

Limite:

Validacao por hash completo ainda nao foi executada. Ela fica obrigatoria antes da migracao/ativacao do novo cofre.
