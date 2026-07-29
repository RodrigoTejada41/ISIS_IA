# Painel de Habilidades

## Estado

- Fase 24 implementada.
- UI local lista habilidades instaladas.
- Execucao passa pelo sandbox existente.
- Habilidade sem permissao adequada e bloqueada.
- Habilidade com confirmacao exige aprovacao.

## CLI

```powershell
python -m aurora.cli ui-skills-snapshot
python -m aurora.cli ui-skill-run project_list --arg root=D:/ISIS_IA --approve
```

## Regras

- Nao executa habilidade inexistente.
- Nao executa habilidade desativada.
- Usa `SkillManager.validate_permissions`.
- Usa `SkillManager.run_in_sandbox`.

## Pendente

- Botao de execucao direto na UI.
- Formulario dinamico por `inputs`.
- Visualizacao do stdout/stderr no painel.
