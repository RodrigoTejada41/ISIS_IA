from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

from aurora.core.assistant import IsisAssistantCore
from aurora.core.conversations import ConversationStore, StoredMessage
from aurora.core.runtime import AuroraRuntime
from aurora.ui.hud_dashboard import build_hud_snapshot, hud_response_text, speech_excerpt
from aurora.voice.factory import build_voice_session
from aurora.voice.tts.piper_engine import AudioCache
from aurora.voice.voice_manager import VoiceManager


class ChatJobManager:
    def __init__(self, server: "HudWebServer") -> None:
        self.server = server
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()

    def start(self, prompt: str, conversation_id: str | None = None, project_id: str | None = None) -> dict:
        job_id = str(uuid.uuid4())
        conv_id = conversation_id or self.server.store.start_conversation(prompt, project_id)
        job = {
            "job_id": job_id,
            "conversation_id": conv_id,
            "status": "analisando",
            "status_text": "Analisando sua solicitacao",
            "started_at": time.time(),
            "finished_at": None,
            "ok": None,
            "response": "",
            "speech_text": "",
            "audio_url": None,
            "error": "",
            "model": "",
            "duration_ms": 0,
        }
        with self._lock:
            self._jobs[job_id] = job
        self.server.store.add_message(conv_id, StoredMessage("user", prompt))
        threading.Thread(target=self._run, args=(job_id, prompt, conv_id), daemon=True).start()
        return self.get(job_id) or job

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.get("finished_at"):
                return False
            job["status"] = "cancelado"
            job["status_text"] = "Resposta interrompida"
            job["finished_at"] = time.time()
            job["ok"] = False
            return True

    def _patch(self, job_id: str, **fields: object) -> None:
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(fields)

    def _is_cancelled(self, job_id: str) -> bool:
        with self._lock:
            return self._jobs.get(job_id, {}).get("status") == "cancelado"

    def _run(self, job_id: str, prompt: str, conversation_id: str) -> None:
        started = time.time()
        try:
            self._patch(job_id, status="gerando", status_text="Gerando resposta")
            result = self.server.core.generate_text(prompt)
            if self._is_cancelled(job_id):
                return
            response = hud_response_text(result)
            model = str(result.get("model") or "")
            speech_text = speech_excerpt(response)
            self.server.store.add_message(
                conversation_id,
                StoredMessage("assistant", response, model=model, metadata={"provider": result.get("provider"), "duration_ms": result.get("duration_ms")}),
            )
            self._patch(job_id, status="voz", status_text="Preparando voz")
            audio_url = self.server._synthesize_url(speech_text)
            if self._is_cancelled(job_id):
                return
            duration_ms = int((time.time() - started) * 1000)
            self._patch(
                job_id,
                status="concluido",
                status_text="Resposta concluida",
                finished_at=time.time(),
                ok=True,
                response=response,
                speech_text=speech_text,
                audio_url=audio_url,
                model=model,
                duration_ms=duration_ms,
            )
        except Exception as exc:
            duration_ms = int((time.time() - started) * 1000)
            self.server.store.add_message(conversation_id, StoredMessage("assistant", f"Erro: {exc}", metadata={"error": str(exc)}))
            self._patch(
                job_id,
                status="erro",
                status_text="Ocorreu um erro",
                finished_at=time.time(),
                ok=False,
                error=str(exc),
                duration_ms=duration_ms,
            )


def build_hud_html(snapshot: dict) -> str:
    payload = json.dumps(snapshot, ensure_ascii=False)
    recent_projects = snapshot.get("recent_projects") or []
    recent_conversations = snapshot.get("recent_conversations") or []
    project_items = "\n".join(
        f'<button class="mini-item" data-project="{item["id"]}"><b>{item["name"]}</b><span>{item["status"]} | {item.get("conversations", 0)} conversas</span></button>'
        for item in recent_projects[:8]
    ) or '<div class="empty">Nenhum projeto salvo ainda.</div>'
    conversation_items = "\n".join(
        f'<button class="mini-item" data-conversation="{item["id"]}"><b>{item["title"]}</b><span>{item.get("project_name") or "Sem projeto"} | {item.get("message_count", 0)} mensagens</span></button>'
        for item in recent_conversations[:10]
    ) or '<div class="empty">Nenhuma conversa salva ainda.</div>'
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{snapshot["assistant_name"]} HUD</title>
<style>
:root {{ color-scheme: dark; --bg:#020506; --deep:#061016; --panel:rgba(8,20,28,.82); --panel2:rgba(6,16,24,.72); --cyan:#25e6ff; --blue:#2d7dff; --teal:#20ffc8; --gold:#d9ad52; --rose:#ff5fa2; --white:#f2fdff; --muted:#89a7b4; --warn:#ffb454; --memory:#b78cff; --line:rgba(37,230,255,.26); --glass:rgba(255,255,255,.045); }}
* {{ box-sizing:border-box; }}
*::-webkit-scrollbar {{ width:10px; height:10px; }}
*::-webkit-scrollbar-thumb {{ background:rgba(37,230,255,.25); border-radius:999px; }}
body {{ margin:0; min-height:100vh; background:
  radial-gradient(circle at 22% 0%, rgba(37,230,255,.18), transparent 28%),
  radial-gradient(circle at 82% 12%, rgba(32,255,200,.10), transparent 24%),
  linear-gradient(135deg, #020506 0%, #07141c 46%, #030607 100%);
  color:var(--white); font-family:"Segoe UI Variable","Segoe UI",Arial,sans-serif; overflow:hidden; }}
body:before {{ content:""; position:fixed; inset:0; pointer-events:none; opacity:.18; background-image:
  linear-gradient(rgba(37,230,255,.07) 1px, transparent 1px),
  linear-gradient(90deg, rgba(37,230,255,.06) 1px, transparent 1px);
  background-size:40px 40px; mask-image:radial-gradient(circle at center, #000 0 55%, transparent 80%); }}
button,input {{ font:inherit; }}
.app {{ position:relative; height:100vh; min-height:0; display:grid; grid-template-rows:78px minmax(0,1fr) 74px; gap:14px; padding:12px; overflow:hidden; }}
.top,.footer {{ display:flex; align-items:center; gap:10px; }}
.brand {{ flex:1; display:flex; align-items:center; gap:14px; }}
.brand:before {{ content:""; width:48px; height:48px; border:1px solid var(--cyan); border-radius:50%; background:radial-gradient(circle, #eaffff 0 5%, #40eaff 10%, #0a3750 42%, transparent 70%); box-shadow:0 0 32px rgba(37,230,255,.38); }}
.brand h1 {{ margin:0; color:var(--white); font-size:30px; letter-spacing:0; line-height:1; }}
.brand div,.eyebrow {{ color:var(--muted); font-size:11px; text-transform:uppercase; }}
.metric,.nav,.chat,.side,.bubble,.btn,.command-wrap,.module,.task,.choice {{ background:var(--panel); border:1px solid var(--line); box-shadow:0 0 24px rgba(37,230,255,.055), inset 0 0 18px rgba(37,230,255,.025); backdrop-filter:blur(14px); }}
.metric {{ padding:9px 12px; min-width:92px; border-radius:8px; }}
.metric b {{ display:block; color:var(--teal); font-size:14px; margin-top:4px; }}
.shell {{ display:grid; grid-template-columns:238px minmax(0,1fr) 340px; gap:14px; height:100%; min-height:0; overflow:hidden; }}
.nav,.side,.chat {{ border-radius:8px; }}
.nav,.side {{ padding:16px; min-height:0; overflow:auto; }}
.nav button {{ width:100%; position:relative; display:flex; align-items:center; gap:10px; color:var(--cyan); padding:12px; margin-top:8px; font-weight:750; text-align:left; background:transparent; border:1px solid transparent; border-radius:7px; cursor:pointer; }}
.nav button:before {{ content:""; width:7px; height:7px; border-radius:50%; background:currentColor; box-shadow:0 0 14px currentColor; }}
.nav button:hover,.nav button.active {{ background:rgba(37,230,255,.11); border-color:rgba(37,230,255,.36); }}
.nav button:nth-child(3n) {{ color:var(--memory); }}
.nav button:nth-child(4n) {{ color:var(--teal); }}
.nav-tools {{ display:grid; gap:8px; margin:12px 0 10px; }}
.side-search {{ width:100%; padding:10px; font-size:13px; }}
.mini-list {{ margin-top:12px; display:grid; gap:8px; }}
.mini-title {{ margin-top:14px; color:var(--muted); font-size:11px; text-transform:uppercase; }}
.mini-item {{ width:100%; border:1px solid rgba(37,230,255,.18); border-radius:7px; background:rgba(3,12,18,.72); color:var(--white); text-align:left; padding:9px; cursor:pointer; }}
.mini-item b,.mini-item span {{ display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.mini-item b {{ color:var(--cyan); font-size:12px; }}
.mini-item span,.empty {{ color:var(--muted); font-size:11px; margin-top:3px; }}
.nav-meta {{ margin-top:18px; padding-top:14px; border-top:1px solid rgba(37,230,255,.18); color:var(--muted); font-size:12px; line-height:1.55; }}
.chat {{ background:var(--panel2); padding:16px; display:flex; flex-direction:column; min-width:0; min-height:0; height:100%; overflow:hidden; }}
.channel-head {{ display:flex; align-items:center; justify-content:space-between; gap:10px; margin-bottom:12px; }}
.status {{ font-weight:750; font-size:14px; color:var(--teal); border:1px solid rgba(32,255,200,.32); padding:8px 12px; border-radius:999px; }}
.status.busy {{ color:var(--warn); border-color:rgba(255,180,84,.42); }}
.status.busy:after {{ content:""; display:inline-block; width:6px; height:6px; margin-left:8px; border-radius:50%; background:currentColor; animation:blink 1s infinite; }}
.workspace {{ overflow:hidden; flex:1; min-height:0; display:flex; }}
.messages {{ flex:1; min-height:0; overflow-y:auto; overflow-x:hidden; padding:0 6px 2px 0; scroll-behavior:smooth; }}
.panel {{ display:none; animation:rise .18s ease-out; min-height:0; height:100%; }}
.panel.active {{ display:block; width:100%; overflow:auto; padding-right:6px; }}
#conversa.panel.active {{ display:flex; flex:1; flex-direction:column; overflow:hidden; padding-right:0; }}
.bubble {{ position:relative; padding:14px 15px; margin:0 0 12px; border-color:var(--cyan); background:rgba(3,9,14,.72); white-space:pre-wrap; overflow-wrap:anywhere; line-height:1.48; border-radius:8px; }}
.bubble:after {{ content:""; position:absolute; left:0; top:12px; bottom:12px; width:2px; background:currentColor; box-shadow:0 0 18px currentColor; }}
.bubble b {{ display:block; color:var(--cyan); font-size:11px; margin-bottom:6px; }}
.bubble small {{ display:block; color:var(--muted); margin-top:8px; font-size:11px; }}
.bubble-actions {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }}
.bubble-actions button {{ border:1px solid rgba(37,230,255,.25); background:rgba(37,230,255,.06); color:var(--cyan); border-radius:6px; padding:6px 8px; cursor:pointer; font-size:12px; }}
.user {{ border-color:rgba(36,120,255,.55); }}
.user b {{ color:var(--blue); }}
.isis {{ border-color:rgba(32,255,200,.54); }}
.isis b {{ color:var(--teal); }}
.modules {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }}
.module {{ min-height:134px; border-radius:8px; padding:15px; background:rgba(3,12,18,.72); }}
.module h3 {{ margin:0 0 8px; font-size:16px; color:var(--white); }}
.module p,.task p {{ margin:0; color:var(--muted); line-height:1.45; }}
.task {{ border-radius:8px; padding:13px; margin-bottom:10px; display:flex; justify-content:space-between; gap:12px; }}
.task b {{ color:var(--cyan); }}
.task span {{ color:var(--teal); font-weight:750; white-space:nowrap; }}
.choice {{ width:100%; margin-top:10px; padding:12px; border-radius:8px; color:var(--white); background:rgba(3,12,18,.72); text-align:left; cursor:pointer; }}
.choice:hover {{ border-color:var(--cyan); background:rgba(37,230,255,.10); }}
.avatar {{ height:260px; display:grid; place-items:center; position:relative; }}
.core {{ position:relative; width:178px; height:178px; border:1px solid var(--cyan); border-radius:50%; display:grid; place-items:center; text-align:center; color:var(--white); background:radial-gradient(circle, #dfffff 0 3%, #52efff 8%, rgba(0,101,180,.48) 32%, rgba(0,0,0,.1) 66%); box-shadow:0 0 54px rgba(37,230,255,.32); animation:pulse 2.8s infinite; }}
.core:before,.core:after {{ content:""; position:absolute; inset:-24px; border-radius:50%; border:1px solid rgba(37,230,255,.48); border-left-color:transparent; border-right-color:rgba(217,173,82,.55); animation:spin 12s linear infinite; }}
.core:after {{ inset:-44px; animation-duration:18s; animation-direction:reverse; opacity:.72; }}
.wings {{ position:absolute; width:250px; height:118px; border-top:1px solid rgba(217,173,82,.55); border-bottom:1px solid rgba(37,230,255,.22); transform:skewY(-12deg); opacity:.7; }}
@keyframes pulse {{ 50% {{ transform:scale(1.04); box-shadow:0 0 80px rgba(32,255,200,.30); }} }}
@keyframes spin {{ to {{ transform:rotate(360deg); }} }}
@keyframes blink {{ 50% {{ opacity:.35; transform:scale(.72); }} }}
@keyframes rise {{ from {{ transform:translateY(5px); opacity:.65; }} to {{ transform:translateY(0); opacity:1; }} }}
.row {{ border-top:1px solid rgba(37,230,255,.18); padding:10px 0; }}
.row span {{ display:block; color:var(--muted); font-size:12px; }}
.row b {{ color:var(--cyan); font-size:13px; overflow-wrap:anywhere; }}
input {{ flex:1; min-width:0; background:rgba(3,10,16,.92); border:1px solid rgba(37,230,255,.26); color:var(--white); padding:14px; outline:none; border-radius:8px; }}
.btn {{ color:var(--cyan); padding:12px 14px; cursor:pointer; border-radius:8px; }}
.btn:hover {{ border-color:var(--cyan); background:rgba(37,230,255,.12); }}
.btn.active {{ border-color:var(--teal); color:var(--teal); background:rgba(32,255,200,.11); }}
.send {{ color:var(--blue); }}
.warn {{ color:var(--warn); }}
.hidden-input {{ display:none; }}
@media (max-width:1100px) {{ .shell {{ grid-template-columns:210px minmax(0,1fr); }} .side {{ display:none; }} }}
@media (max-width:760px) {{ body {{ overflow:auto; }} .app {{ height:auto; min-height:100vh; grid-template-rows:auto auto auto; overflow:visible; }} .top,.footer {{ flex-wrap:wrap; }} .shell {{ grid-template-columns:1fr; }} .nav {{ order:2; }} .modules {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main class="app">
  <header class="top">
    <div class="brand"><section><h1>{snapshot["assistant_name"]}</h1><div>AI COMMAND OS | NUCLEO LOCAL FEMININO</div></section></div>
    <div class="metric">RAM<b>{snapshot["ram_available_mb"]} MB</b></div>
    <div class="metric">VRAM<b>{snapshot["vram_available_mb"]} MB</b></div>
    <div class="metric">NET<b>{"ON" if snapshot["internet_enabled"] else "OFF"}</b></div>
    <div class="metric">MIC<b>{"ON" if snapshot["microphone_enabled"] else "OFF"}</b></div>
    <div class="metric">VOICE<b>{"ON" if snapshot["tts_ready"] else "OFF"}</b></div>
  </header>
  <section class="shell">
    <nav class="nav">
      <div class="eyebrow">Navegacao</div>
      <div class="nav-tools">
        <button id="newProject" type="button">Novo projeto</button>
        <input id="sideSearch" class="side-search" placeholder="Pesquisar projetos e conversas">
      </div>
      <button class="active" data-panel="conversa">Conversa</button>
      <button data-panel="memoria">Memoria</button>
      <button data-panel="projetos">Projetos</button>
      <button data-panel="documentos">Documentos</button>
      <button data-panel="automacoes">Automacoes</button>
      <button data-panel="agenda">Agenda</button>
      <button data-panel="configuracoes">Configuracoes</button>
      <div class="mini-title">Projetos recentes</div>
      <div class="mini-list" id="projectList">{project_items}</div>
      <div class="mini-title">Conversas recentes</div>
      <div class="mini-list" id="conversationList">{conversation_items}</div>
      <button data-panel="favoritos">Favoritos</button>
      <button data-panel="arquivados">Arquivados</button>
      <button data-panel="lixeira">Lixeira</button>
      <div class="nav-meta">MIC usa ditado do navegador. Voz natural usa vozes instaladas no Chrome/Windows; Piper local fica como fallback.</div>
    </nav>
    <section class="chat">
      <div class="channel-head"><div class="eyebrow">Canal principal</div><div id="status" class="status">Sistema local pronto</div></div>
      <div class="workspace">
        <div id="conversa" class="panel active"><div id="messages" class="messages"></div></div>
        <div id="memoria" class="panel">
          <div class="modules">
            <section class="module"><h3>Indice local</h3><p>{snapshot["project_notes_indexed"]} notas catalogadas no SSD.</p></section>
            <section class="module"><h3>Embeddings</h3><p>{snapshot["project_embeddings_indexed"]} indexadas; {snapshot["project_embeddings_pending"]} pendentes.</p></section>
            <section class="module"><h3>Busca</h3><p>Use comandos como: procurar projeto, listar decisoes, listar bugs.</p></section>
            <section class="module"><h3>Politica</h3><p>Obsidian permanece em modo leitura para proteger o cofre.</p></section>
          </div>
        </div>
        <div id="projetos" class="panel">
          <div class="task"><div><b>Catalogo local</b><p>Projetos/candidatos consolidados a partir do CEREBRO VIVO.</p></div><span>LOCAL</span></div>
          <button class="choice" data-command="liste meus projetos principais">Listar projetos principais</button>
          <button class="choice" data-command="resuma o estado atual do projeto ISIS">Resumir estado da ISIS</button>
        </div>
        <div id="documentos" class="panel">
          <div class="task"><div><b>Documentos indexados</b><p>Consulta local por notas, decisoes, bugs e requisitos.</p></div><span>{snapshot["project_notes_indexed"]}</span></div>
          <button class="choice" data-command="procure documentos sobre a interface HUD">Procurar documentos da HUD</button>
          <button class="choice" data-command="liste decisoes recentes do projeto">Listar decisoes recentes</button>
        </div>
        <div id="automacoes" class="panel">
          <div class="task"><div><b>Execucao real protegida</b><p>Automacao real continua bloqueada por politica; simulacao e auditoria estao disponiveis.</p></div><span>SEGURO</span></div>
          <button class="choice" data-command="mostre o status das permissoes de automacao">Status das permissoes</button>
          <button class="choice" data-command="planeje uma automacao segura de tela">Planejar automacao segura</button>
        </div>
        <div id="agenda" class="panel">
          <div class="task"><div><b>Agenda local</b><p>Nao ha conector de calendario ativo neste projeto.</p></div><span>OFFLINE</span></div>
          <button class="choice" data-command="crie uma lista de proximas tarefas tecnicas da ISIS">Gerar proximas tarefas</button>
        </div>
        <div id="configuracoes" class="panel">
          <div class="modules">
            <section class="module"><h3>Voz</h3><p id="voiceInfo">{snapshot["tts_engine"]} / {snapshot["tts_voice"]}</p></section>
            <section class="module"><h3>Microfone</h3><p id="micInfo">Ditado web aguardando permissao do navegador.</p></section>
            <section class="module"><h3>Modelo</h3><p>{snapshot["coding_model"]}</p></section>
            <section class="module"><h3>Rede</h3><p>{"Ativa" if snapshot["internet_enabled"] else "Offline por politica"}</p></section>
            <section class="module"><h3>Configuracoes de Voz</h3><p id="voiceSettings">Carregue o diagnostico para ver motor, cache, interrupcao e dispositivos.</p></section>
            <section class="module"><h3>Acoes de Voz</h3><button class="choice" id="voiceDiag" type="button">Verificar modelos</button><button class="choice" id="clearVoiceCache" type="button">Limpar cache</button></section>
          </div>
        </div>
        <div id="favoritos" class="panel"><div class="task"><div><b>Favoritos</b><p>Estrutura preparada para projetos e conversas favoritas.</p></div><span>LOCAL</span></div></div>
        <div id="arquivados" class="panel"><div class="task"><div><b>Arquivados</b><p>Itens arquivados permanecem no banco local e podem ser restaurados futuramente.</p></div><span>SEGURO</span></div></div>
        <div id="lixeira" class="panel"><div class="task"><div><b>Lixeira</b><p>Exclusao definitiva exige confirmacao e ainda nao e acionada pela HUD.</p></div><span>PROTEGIDO</span></div></div>
      </div>
    </section>
    <aside class="side">
      <div class="eyebrow">Nucleo IA</div>
      <div class="avatar"><div class="wings"></div><div class="core">ISIS<br><small>ONLINE LOCAL</small></div></div>
      <div class="row"><span>Modelo codigo</span><b>{snapshot["coding_model"]}</b></div>
      <div class="row"><span>Embeddings</span><b>{snapshot["embedding_model"]}</b></div>
      <div class="row"><span>Voz</span><b>{snapshot["tts_engine"]} / {snapshot["tts_voice"]}</b></div>
      <div class="row"><span>Notas</span><b>{snapshot["project_notes_indexed"]}</b></div>
      <div class="row"><span>Embeddings pendentes</span><b>{snapshot["project_embeddings_pending"]}</b></div>
    </aside>
  </section>
  <footer class="footer">
    <input id="prompt" placeholder="Digite um comando para ISIS..." autocomplete="off">
    <button class="btn" id="voice">VOZ NATURAL</button>
    <button class="btn" id="mic">MIC</button>
    <button class="btn" id="attach">ANEXO</button>
    <button class="btn send" id="send">ENVIAR</button>
    <button class="btn warn" id="stop">PARAR</button>
    <input class="hidden-input" id="fileInput" type="file" multiple>
  </footer>
</main>
<script>
const snapshot = {payload};
const messages = document.getElementById("messages");
const statusEl = document.getElementById("status");
const input = document.getElementById("prompt");
const micBtn = document.getElementById("mic");
const fileInput = document.getElementById("fileInput");
let stopped = false;
let sending = false;
let activeJobId = null;
let activeConversationId = null;
let lastPrompt = "";
let recognition = null;
let listening = false;
let naturalVoice = null;
function unlockInput() {{
  sending = false;
  window.setTimeout(() => input.focus(), 0);
}}
function setStatus(text, busy=false) {{
  statusEl.textContent = text;
  statusEl.classList.toggle("busy", busy);
}}
function scrollMessagesToBottom() {{
  window.requestAnimationFrame(() => {{
    messages.scrollTop = messages.scrollHeight;
  }});
}}
function add(author, text, cls="", meta=null) {{
  const div = document.createElement("div");
  div.className = "bubble " + cls;
  div.innerHTML = "<b></b><span></span>";
  div.querySelector("b").textContent = author.toUpperCase();
  div.querySelector("span").textContent = text;
  if (meta) {{
    const small = document.createElement("small");
    small.textContent = meta;
    div.appendChild(small);
  }}
  if (cls.includes("isis")) {{
    const actions = document.createElement("div");
    actions.className = "bubble-actions";
    actions.innerHTML = '<button data-action="copy">Copiar</button><button data-action="retry">Tentar novamente</button><button data-action="edit">Editar pergunta</button>';
    actions.onclick = event => {{
      const action = event.target && event.target.dataset ? event.target.dataset.action : "";
      if (action === "copy") navigator.clipboard?.writeText(text);
      if (action === "retry" && lastPrompt) {{ input.value = lastPrompt; sendPrompt(); }}
      if (action === "edit" && lastPrompt) {{ input.value = lastPrompt; input.focus(); }}
    }};
    div.appendChild(actions);
  }}
  messages.appendChild(div);
  scrollMessagesToBottom();
}}
function selectPanel(name) {{
  document.querySelectorAll(".panel").forEach(panel => panel.classList.toggle("active", panel.id === name));
  document.querySelectorAll(".nav button[data-panel]").forEach(btn => btn.classList.toggle("active", btn.dataset.panel === name));
  if (name === "conversa") scrollMessagesToBottom();
}}
function play(url) {{
  if (!url) return;
  new Audio(url).play().catch(() => setStatus("Audio gerado; autoplay bloqueado pelo navegador"));
}}
function loadNaturalVoice() {{
  const voices = window.speechSynthesis ? speechSynthesis.getVoices() : [];
  naturalVoice = voices.find(v => /pt-BR/i.test(v.lang) && /Maria|Francisca|female|Helena|Luciana/i.test(v.name))
    || voices.find(v => /pt-BR/i.test(v.lang))
    || voices.find(v => /^pt/i.test(v.lang))
    || null;
  const label = naturalVoice ? `${{naturalVoice.name}} (${{naturalVoice.lang}})` : "Voz natural indisponivel; Piper local sera usado";
  const info = document.getElementById("voiceInfo");
  if (info) info.textContent = label;
}}
function speakNatural(text, fallbackUrl=null) {{
  if (!("speechSynthesis" in window)) {{ play(fallbackUrl); return; }}
  loadNaturalVoice();
  if (!naturalVoice) {{ play(fallbackUrl); return; }}
  speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text.slice(0, 900));
  utterance.lang = naturalVoice.lang || "pt-BR";
  utterance.voice = naturalVoice;
  utterance.rate = 0.92;
  utterance.pitch = 1.08;
  utterance.volume = 1;
  utterance.onerror = () => play(fallbackUrl);
  speechSynthesis.speak(utterance);
}}
function setupMic() {{
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const info = document.getElementById("micInfo");
  if (!SpeechRecognition) {{
    if (info) info.textContent = "Chrome nao disponibilizou Web Speech Recognition neste ambiente.";
    return false;
  }}
  recognition = new SpeechRecognition();
  recognition.lang = "pt-BR";
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.onstart = () => {{
    listening = true;
    micBtn.classList.add("active");
    setStatus("Ouvindo pelo microfone do navegador...");
    if (info) info.textContent = "Ouvindo. Fale o comando e aguarde a transcricao.";
  }};
  recognition.onresult = event => {{
    let finalText = "";
    let interim = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {{
      const text = event.results[i][0].transcript;
      if (event.results[i].isFinal) finalText += text;
      else interim += text;
    }}
    input.value = (finalText || interim).trim();
    if (finalText) {{
      setStatus("Comando capturado pelo microfone; enviando...");
      window.setTimeout(() => sendPrompt(), 150);
    }}
  }};
  recognition.onerror = event => {{
    setStatus("Microfone bloqueado ou indisponivel: " + event.error);
    if (info) info.textContent = "Permita o microfone no Chrome e tente novamente.";
  }};
  recognition.onend = () => {{
    listening = false;
    micBtn.classList.remove("active");
    if (input.value.trim()) setStatus("Transcricao pronta");
  }};
  if (info) info.textContent = "Web Speech Recognition pronto para pt-BR.";
  return true;
}}
async function sendPrompt() {{
  if (sending) return;
  const prompt = input.value.trim();
  if (!prompt) return;
  sending = true;
  stopped = false;
  lastPrompt = prompt;
  selectPanel("conversa");
  input.value = "";
  add("Voce", prompt, "user");
  setStatus("Analisando sua solicitacao", true);
  try {{
    const res = await fetch("/api/chat", {{ method:"POST", headers:{{"content-type":"application/json"}}, body:JSON.stringify({{prompt, conversation_id: activeConversationId}}) }});
    const data = await res.json();
    if (!data.job_id) throw new Error(data.error || "Falha ao iniciar job");
    activeJobId = data.job_id;
    activeConversationId = data.conversation_id || activeConversationId;
    pollJob(data.job_id);
  }} catch (error) {{
    add("ISIS", String(error.message || error), "isis");
    setStatus("Ocorreu um erro");
    sending = false;
  }}
}}
async function pollJob(jobId) {{
  try {{
    const res = await fetch(`/api/chat-status?id=${{encodeURIComponent(jobId)}}`);
    const data = await res.json();
    if (stopped) {{
      await fetch("/api/chat-cancel", {{ method:"POST", headers:{{"content-type":"application/json"}}, body:JSON.stringify({{job_id:jobId}}) }});
      setStatus("Resposta interrompida");
      unlockInput();
      return;
    }}
    setStatus(data.status_text || "Gerando resposta", !data.finished_at);
    if (!data.finished_at) {{
      window.setTimeout(() => pollJob(jobId), 650);
      return;
    }}
    const meta = data.model ? `Modelo: ${{data.model}} | ${{Math.round((data.duration_ms || 0) / 100) / 10}}s` : `${{Math.round((data.duration_ms || 0) / 100) / 10}}s`;
    add("ISIS", data.response || data.error || "", "isis", meta);
    setStatus(data.ok ? "Resposta concluida" : "Ocorreu um erro");
    if (data.ok) speakNatural(data.speech_text || data.response || "", data.audio_url);
    else play(data.audio_url);
    unlockInput();
  }} catch (error) {{
    add("ISIS", String(error.message || error), "isis");
    setStatus("Ocorreu um erro");
    unlockInput();
  }}
}}
add("Sistema", "Ollama local ativo. Modelo de codigo: " + snapshot.coding_model);
add("Memoria", "Memoria local pronta para consulta. Indexacao semantica segue em segundo plano.");
add("ISIS", "Pronta para comandos locais. Use MIC para ditar no navegador e VOZ NATURAL para testar a voz do sistema.", "isis");
document.getElementById("send").onclick = sendPrompt;
input.onkeydown = e => {{ if (e.key === "Enter") sendPrompt(); }};
document.getElementById("voice").onclick = async () => {{
  setStatus("Testando voz natural...");
  const res = await fetch("/api/voice-test", {{ method:"POST" }});
  const data = await res.json();
  setStatus(data.ok ? "Voz natural acionada; Piper fica como fallback" : data.error);
  speakNatural("ISIS voz natural ativa no navegador. Piper local permanece como reserva.", data.audio_url);
}};
document.getElementById("voiceDiag").onclick = async () => {{
  const res = await fetch("/api/voice-status");
  const data = await res.json();
  const engines = (data.engines || []).map(item => `${{item.name}}=${{item.available ? "ok" : "off"}}`).join(", ");
  document.getElementById("voiceSettings").textContent = `Motor: ${{data.tts_engine}} | STT: ${{data.stt_engine}} | Cache: ${{data.audio_cache_enabled ? "on" : "off"}} | Interrupcao: ${{data.allow_interruption ? "on" : "off"}} | ${{engines}}`;
  setStatus(data.ok === false ? "Falha no diagnostico de voz" : "Diagnostico de voz atualizado");
}};
document.getElementById("clearVoiceCache").onclick = async () => {{
  const res = await fetch("/api/voice-cache-clear", {{ method:"POST" }});
  const data = await res.json();
  setStatus(data.ok ? `Cache de voz limpo: ${{data.removed}} arquivos` : (data.error || "Falha ao limpar cache"));
}};
document.getElementById("mic").onclick = () => {{
  if (!recognition && !setupMic()) {{ setStatus("Microfone do navegador indisponivel"); return; }}
  if (listening) recognition.stop();
  else recognition.start();
}};
document.getElementById("attach").onclick = () => fileInput.click();
fileInput.onchange = () => {{
  const names = Array.from(fileInput.files || []).map(file => `${{file.name}} (${{Math.ceil(file.size / 1024)}} KB)`);
  if (!names.length) return;
  selectPanel("conversa");
  add("Anexo", names.join("\\n"), "user");
  setStatus("Anexo selecionado localmente; envio ao modelo ainda nao habilitado");
}};
document.getElementById("stop").onclick = () => {{
  stopped = true;
  if ("speechSynthesis" in window) speechSynthesis.cancel();
  if (recognition && listening) recognition.stop();
  if (activeJobId) fetch("/api/chat-cancel", {{ method:"POST", headers:{{"content-type":"application/json"}}, body:JSON.stringify({{job_id:activeJobId}}) }});
  setStatus("Parada solicitada");
}};
document.querySelectorAll(".nav button[data-panel]").forEach(btn => btn.onclick = () => selectPanel(btn.dataset.panel));
document.querySelectorAll(".choice[data-command]").forEach(btn => btn.onclick = () => {{
  input.value = btn.dataset.command;
  selectPanel("conversa");
  input.focus();
}});
document.getElementById("newProject").onclick = async () => {{
  const name = prompt("Nome do projeto");
  if (!name) return;
  const res = await fetch("/api/projects", {{ method:"POST", headers:{{"content-type":"application/json"}}, body:JSON.stringify({{name}}) }});
  const data = await res.json();
  setStatus(data.ok ? "Projeto criado" : (data.error || "Falha ao criar projeto"));
  if (data.ok) location.reload();
}};
document.querySelectorAll("[data-conversation]").forEach(btn => btn.onclick = async () => {{
  const id = btn.dataset.conversation;
  const res = await fetch(`/api/conversation?id=${{encodeURIComponent(id)}}`);
  const data = await res.json();
  if (!data.ok) {{ setStatus(data.error || "Conversa nao encontrada"); return; }}
  activeConversationId = id;
  messages.innerHTML = "";
  (data.conversation.messages || []).forEach(msg => add(msg.role === "user" ? "Voce" : "ISIS", msg.content, msg.role === "user" ? "user" : "isis", msg.model ? `Modelo: ${{msg.model}}` : null));
  selectPanel("conversa");
  scrollMessagesToBottom();
  setStatus("Conversa carregada");
}});
document.getElementById("sideSearch").onkeydown = async e => {{
  if (e.key !== "Enter") return;
  const query = e.target.value.trim();
  if (!query) return;
  const res = await fetch(`/api/search?q=${{encodeURIComponent(query)}}`);
  const data = await res.json();
  setStatus(data.ok ? `Busca local: ${{data.results.conversations.length}} conversas` : "Falha na busca");
}};
if ("speechSynthesis" in window) {{
  speechSynthesis.onvoiceschanged = loadNaturalVoice;
  loadNaturalVoice();
}}
setupMic();
</script>
</body>
</html>"""


class HudWebServer:
    def __init__(self, runtime: AuroraRuntime) -> None:
        self.runtime = runtime
        self.core = IsisAssistantCore(runtime.root)
        self.core.initialize()
        self.temp_dir = Path(runtime.config.paths.isis_root) / "data" / "temporary"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.store = ConversationStore(Path(runtime.config.paths.isis_root) / "data" / "databases" / "hud_conversations.sqlite")
        self.jobs = ChatJobManager(self)

    def serve(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        state = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                parsed = urlparse(self.path)
                if parsed.path == "/":
                    self._send_html(build_hud_html(state._hud_payload()))
                    return
                if parsed.path == "/api/snapshot":
                    self._send_json(state._hud_payload())
                    return
                if parsed.path == "/api/audio":
                    self._send_audio(parse_qs(parsed.query).get("name", [""])[0])
                    return
                if parsed.path == "/api/chat-status":
                    self._chat_status(parse_qs(parsed.query).get("id", [""])[0])
                    return
                if parsed.path == "/api/voice-status":
                    self._voice_status()
                    return
                if parsed.path == "/api/conversations":
                    self._send_json({"ok": True, "conversations": state.store.list_conversations()})
                    return
                if parsed.path == "/api/conversation":
                    self._conversation(parse_qs(parsed.query).get("id", [""])[0])
                    return
                if parsed.path == "/api/projects":
                    self._send_json({"ok": True, "projects": state.store.list_projects()})
                    return
                if parsed.path == "/api/search":
                    self._send_json({"ok": True, "results": state.store.search(parse_qs(parsed.query).get("q", [""])[0])})
                    return
                self.send_error(HTTPStatus.NOT_FOUND)

            def do_POST(self) -> None:
                if self.path == "/api/chat":
                    self._chat()
                    return
                if self.path == "/api/chat-cancel":
                    self._chat_cancel()
                    return
                if self.path == "/api/voice-test":
                    self._voice_test()
                    return
                if self.path == "/api/voice-cache-clear":
                    self._voice_cache_clear()
                    return
                if self.path == "/api/projects":
                    self._create_project()
                    return
                self.send_error(HTTPStatus.NOT_FOUND)

            def _chat(self) -> None:
                try:
                    data = self._read_json()
                    prompt = str(data.get("prompt", "")).strip()
                    if not prompt:
                        self._send_json({"ok": False, "error": "prompt vazio"}, HTTPStatus.BAD_REQUEST)
                        return
                    job = state.jobs.start(
                        prompt,
                        conversation_id=str(data.get("conversation_id") or "") or None,
                        project_id=str(data.get("project_id") or "") or None,
                    )
                    self._send_json({"ok": True, **job})
                except Exception as exc:
                    self._send_json({"ok": False, "error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

            def _chat_status(self, job_id: str) -> None:
                job = state.jobs.get(job_id)
                if not job:
                    self._send_json({"ok": False, "error": "job nao encontrado"}, HTTPStatus.NOT_FOUND)
                    return
                self._send_json({"ok": True, **job})

            def _chat_cancel(self) -> None:
                data = self._read_json()
                cancelled = state.jobs.cancel(str(data.get("job_id") or ""))
                self._send_json({"ok": cancelled})

            def _conversation(self, conversation_id: str) -> None:
                conversation = state.store.get_conversation(conversation_id)
                if not conversation:
                    self._send_json({"ok": False, "error": "conversa nao encontrada"}, HTTPStatus.NOT_FOUND)
                    return
                self._send_json({"ok": True, "conversation": conversation})

            def _create_project(self) -> None:
                data = self._read_json()
                name = str(data.get("name") or "").strip()
                if not name:
                    self._send_json({"ok": False, "error": "nome obrigatorio"}, HTTPStatus.BAD_REQUEST)
                    return
                project_id = state.store.ensure_project(
                    name,
                    description=str(data.get("description") or ""),
                    objective=str(data.get("objective") or ""),
                    local_dir=str(data.get("local_dir") or ""),
                )
                self._send_json({"ok": True, "project_id": project_id})

            def _voice_test(self) -> None:
                try:
                    audio_url = state._synthesize_url("ISIS voz local ativa. Interface web operacional.")
                    self._send_json({"ok": True, "audio_url": audio_url})
                except Exception as exc:
                    self._send_json({"ok": False, "error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

            def _voice_status(self) -> None:
                try:
                    self._send_json({"ok": True, **VoiceManager(state.runtime.config, state.runtime.audit).status()})
                except Exception as exc:
                    self._send_json({"ok": False, "error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

            def _voice_cache_clear(self) -> None:
                try:
                    cache = AudioCache(Path(state.runtime.config.paths.cache_dir) / "audio", max_files=state.runtime.config.voice.audio_cache_max_files)
                    self._send_json({"ok": True, "removed": cache.clear(), "cache_dir": str(cache.cache_dir)})
                except Exception as exc:
                    self._send_json({"ok": False, "error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

            def _read_json(self) -> dict:
                length = int(self.headers.get("content-length", "0"))
                return json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

            def _send_html(self, html: str) -> None:
                body = html.encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("content-type", "text/html; charset=utf-8")
                self.send_header("cache-control", "no-store")
                self.send_header("content-length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                self.send_header("content-type", "application/json; charset=utf-8")
                self.send_header("content-length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _send_audio(self, name: str) -> None:
                path = state.temp_dir / Path(name).name
                if not path.exists() or path.suffix.lower() != ".wav":
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                body = path.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("content-type", "audio/wav")
                self.send_header("content-length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:
                return

        server = ThreadingHTTPServer((host, port), Handler)
        try:
            print(f"HUD web: http://{host}:{port}")
            server.serve_forever()
        finally:
            self.core.shutdown("hud-web")

    def _synthesize_url(self, text: str) -> str | None:
        if self.runtime.config.voice.tts_engine != "piper":
            return None
        session = build_voice_session(self.runtime.config, self.runtime.audit, transcript="hud-web")
        output = session.tts.synthesize(speech_excerpt(text), self.runtime.config.voice.selected_voice)
        return "/api/audio?name=" + quote(output.name)

    def _hud_payload(self) -> dict:
        payload = asdict(build_hud_snapshot(self.runtime))
        payload["recent_projects"] = self.store.list_projects(8)
        payload["recent_conversations"] = self.store.list_conversations(10)
        return payload
