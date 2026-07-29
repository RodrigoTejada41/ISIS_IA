# Arquitetura de Internet

- Modulo: `aurora.internet`.
- Gerenciador: `InternetManager`.
- Agente: `ResearchAgent`.
- Provedor gratuito padrao: `duckduckgo_html+bing_html`.
- Leitura de paginas: HTTP simples por `urllib`, sem navegador automatizado.
- Cache: `D:\ISIS_IA\ISIS\data\cache\research`.
- Historico: `D:\ISIS_IA\ISIS\data\databases\research_history.sqlite`.

Fluxo:

1. Detectar se a pergunta exige pesquisa.
2. Sanitizar consulta.
3. Consultar `PermissionEngine`.
4. Buscar resultados.
5. Validar URL, dominio e SSRF.
6. Ler paginas permitidas.
7. Pontuar fontes.
8. Responder com fontes e data.
