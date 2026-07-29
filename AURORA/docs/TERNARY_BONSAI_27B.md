# Ternary Bonsai 27B

Fonte: `https://huggingface.co/prism-ml/Ternary-Bonsai-27B-gguf`.

Arquivo baixado:

- `D:\ISIS_IA\ISIS\models\huggingface\prism-ml\Ternary-Bonsai-27B-gguf\Ternary-Bonsai-27B-Q2_0.gguf`

Resumo tecnico:

- Modelo GGUF de classe 27B.
- Pesos ternarios em formato `Q2_0_g128`.
- Foco: raciocinio local com footprint baixo.
- Tamanho local do arquivo baixado: cerca de 7.17 GB.
- Licenca: Apache 2.0.

Uso recomendado:

- Usar com runtime `llama.cpp` compativel com os kernels de baixo bit da PrismML.
- Parametros sugeridos pelo card:
  - temperature: `0.7`
  - top-p: `0.95`
  - top-k: `20`

Limites atuais no AURORA:

- O arquivo esta baixado localmente.
- Runtime `llama.cpp` foi instalado em `D:\ISIS_IA\ISIS\runtime\llama.cpp`.
- Tentativa de importacao no Ollama falhou com `tensor "output.weight" size overflow`.
- Tentativa de carga no `llama.cpp` b10173 falhou com offset inconsistente em `output_norm.weight`.
- SHA-256 local confere com o Hugging Face: `868c11714cf8fe47f5ec9eeb2be0ab1a337112886f92ee0ede6b855c4fa31757`.
- Status operacional: baixado e registrado, mas bloqueado por compatibilidade do GGUF/runtime atual.
- Ollama pode puxar variantes HF, mas o card oficial aponta `F16` para Ollama; a variante baixada `Q2_0` e mais adequada ao hardware, porem depende de compatibilidade do runtime.

Logs:

- `D:\ISIS_IA\ISIS\logs\models\ollama_create_ternary_bonsai_27b_q2.log`
- `D:\ISIS_IA\ISIS\logs\models\llamacpp_ternary_bonsai_smoke.log`
