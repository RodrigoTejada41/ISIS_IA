# KAT-Coder-V2.5-Dev

Fonte:

- `https://huggingface.co/Kwaipilot/KAT-Coder-V2.5-Dev`

Local:

- `D:\ISIS_IA\ISIS\models\huggingface\Kwaipilot\KAT-Coder-V2.5-Dev`

Estado:

- Download completo.
- Tamanho local: cerca de 64.59 GB.
- Formato: Hugging Face Transformers / safetensors.
- Arquivos principais: 13 shards `model-00000-of-00013.safetensors` a `model-00012-of-00013.safetensors`.
- Licenca: Apache 2.0.

Caracteristicas do card:

- MOE com 35B parametros totais.
- 3B parametros ativados.
- Text-only nesta release aberta.
- Compativel com Transformers, vLLM, SGLang e KTransformers.

Limite local:

- Nao foi colocado na rota ativa do AURORA.
- O card recomenda vLLM/SGLang com tensor parallel em 8 GPUs para endpoint padrao.
- A RTX 3060 local nao e alvo adequado para servir esse checkpoint diretamente.

Comando de status:

```powershell
cd D:\ISIS_IA\AURORA
.\scripts\hf_models_status.ps1
```

Proximo passo viavel:

- Procurar ou gerar uma variante GGUF/quantizada menor do KAT-Coder.
- Alternativa: configurar servidor Linux dedicado com vLLM/SGLang e GPU suficiente.
