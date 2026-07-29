# Seguranca Web

Protecoes implementadas:

- bloqueio de `file://`, `ftp://`, `data:` e esquemas nao HTTP;
- bloqueio de URLs com credenciais;
- bloqueio de portas fora de 80/443;
- protecao SSRF para redes privadas e localhost;
- validacao DNS antes do acesso;
- sanitizacao de consultas com possiveis tokens/senhas;
- deteccao inicial de prompt injection em paginas externas;
- downloads bloqueados por padrao;
- `DownloadManager` bloqueia executaveis/scripts antes de acessar a rede;
- execucao automatica bloqueada por regra fixa.

Navegador automatizado ainda nao foi ativado. O modo atual usa HTTP simples.
