# Modelos Locais - Fase 39

Adaptadores implementados:

- `MockModelProvider`: fallback offline para testes.
- `OllamaModelProvider`: API local `http://127.0.0.1:11434`.
- `LlamaCppModelProvider`: binario local configurado.
- `LmStudioModelProvider`: API local `http://127.0.0.1:1234/v1`.
- `ModelProviderRegistry`: escolhe provider disponivel.

Estado local detectado:

- Ollama instalado: sim.
- Runtime Ollama do projeto: `D:\ISIS_IA\ISIS\runtime\ollama`.
- Modelos Ollama do projeto: `D:\ISIS_IA\ISIS\models\ollama`.
- Modelos Ollama instalados:
  - `qwen3-coder:30b`: codigo avancado/MoE.
  - `qwen2.5-coder:14b`: codigo e desenvolvimento.
  - `llama3.1:8b`: geral, rapido, resumo e classificacao.
  - `deepseek-r1:8b`: raciocinio.
  - `nomic-embed-text:latest`: embeddings.
  - `llama3:latest`: modelo anterior migrado junto.
- Hugging Face GGUF:
- `D:\ISIS_IA\ISIS\models\huggingface\prism-ml\Ternary-Bonsai-27B-gguf\Ternary-Bonsai-27B-Q2_0.gguf`.

Rotas atuais:

- `CODING`: `qwen3-coder:30b`.
- `CODING` fallback: `qwen2.5-coder:14b`.
- NVIDIA: RTX 3060.
- VRAM total: 12288 MB.
- Perfil operacional: `MEDIUM`.

Comandos:

```powershell
cd D:\ISIS_IA\AURORA
.\scripts\start_ollama_project.ps1
.\scripts\ollama_project_status.ps1
python -m aurora.cli generate "corrija este codigo"
python -m aurora.cli generate "responda apenas OK"
ollama list
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits
```

Limites:

- AURORA usa Ollama antes do mock quando o modelo roteado existe localmente.
- Mock permanece como fallback para testes e modo degradado.
- Modelos reais dependem do servico local do Ollama.
- `Ternary-Bonsai-27B-Q2_0.gguf` foi baixado, mas exige runtime `llama.cpp` compativel com o formato Q2_0_g128 para melhor uso.
- Sem servico online automatico.

Proxima fase:

Fase 40: ampliar uso real de embeddings na memoria permanente.
