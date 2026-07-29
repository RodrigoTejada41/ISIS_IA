# Nucleo ISIS - Fase 7

Componentes implementados:

- `IsisAssistantCore`: inicializacao, comando, auditoria e shutdown.
- `EventBus`: publicacao e historico de eventos.
- `CommandRouter`: comandos locais e roteamento para modelos/memoria.
- `ToolRegistry`: registro e execucao de ferramentas com permissao.
- `HealthMonitor`: validacao local de configuracao, recursos e modo Obsidian.

Entrada CLI:

```powershell
cd D:\ISIS_IA\AURORA
python -m aurora.cli core status
python -m aurora.cli core "corrija este codigo em python"
python -m aurora.cli core "memoria: ISIS"
```

Garantias:

- Nucleo nao habilita internet.
- Nucleo nao altera Obsidian.
- Ferramentas passam por politica de permissao.
- Eventos e comandos sao auditados.
- Shutdown salva configuracao atual.

Limitacoes:

- Geracao real depende de Ollama/llama.cpp/LM Studio com modelo instalado.
- UI grafica ainda nao implementada.

## Fase 8

- `generate_text()` conecta roteamento com `ModelProviderRegistry`.
- CLI `python -m aurora.cli generate "texto"` executa geracao mock enquanto nao houver modelo local instalado.
