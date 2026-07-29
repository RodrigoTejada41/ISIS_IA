from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from tkinter import BOTH, BOTTOM, END, LEFT, RIGHT, TOP, Button, Canvas, Entry, Frame, Label, StringVar, Tk

from aurora.core.assistant import IsisAssistantCore
from aurora.core.embeddings import ProjectEmbeddingIndex
from aurora.core.runtime import AuroraRuntime
from aurora.ui.dashboard import build_dashboard_snapshot
from aurora.voice.factory import build_voice_session
from aurora.voice.text import prepare_text_for_speech


BG = "#050505"
PANEL = "#0b1117"
PANEL_2 = "#0f1820"
CYAN = "#18d7ff"
BLUE = "#2f7dff"
TEAL = "#1df5c3"
WHITE = "#e8f7ff"
MUTED = "#7f98a6"
WARN = "#ffb454"
MEMORY = "#b78cff"


def hud_response_text(result: dict) -> str:
    return str(result.get("text") or result.get("output") or result)


def speech_excerpt(text: str, limit: int = 800) -> str:
    return prepare_text_for_speech(text, limit=limit)


@dataclass(frozen=True, slots=True)
class HudSnapshot:
    assistant_name: str
    profile: str
    offline_mode: bool
    internet_enabled: bool
    microphone_enabled: bool
    ram_available_mb: int
    vram_available_mb: int
    project_notes_indexed: int
    project_embeddings_indexed: int
    project_embeddings_pending: int
    coding_model: str
    embedding_model: str
    tts_engine: str
    tts_voice: str
    stt_engine: str
    tts_ready: bool
    ollama_models: list[str]


def build_hud_snapshot(runtime: AuroraRuntime) -> HudSnapshot:
    base = build_dashboard_snapshot(runtime)
    progress = ProjectEmbeddingIndex(
        Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_memory.sqlite",
        Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_note_embeddings.sqlite",
        runtime.audit,
    ).progress()
    models = [model.model_id for model in runtime.router.models if model.enabled]
    coding_model = next((model.model_id for model in runtime.router.models if model.enabled and any(profile.value == "CODING" for profile in model.profiles)), "")
    embedding_model = next((model.model_id for model in runtime.router.models if model.enabled and any(profile.value == "EMBEDDING" for profile in model.profiles)), "")
    return HudSnapshot(
        assistant_name=base.assistant_name,
        profile=base.profile,
        offline_mode=base.offline_mode,
        internet_enabled=base.internet_enabled,
        microphone_enabled=base.microphone_enabled,
        ram_available_mb=base.ram_available_mb,
        vram_available_mb=base.vram_available_mb,
        project_notes_indexed=base.project_notes_indexed,
        project_embeddings_indexed=int(progress["indexed"]),
        project_embeddings_pending=int(progress["pending"]),
        coding_model=coding_model,
        embedding_model=embedding_model,
        tts_engine=runtime.config.voice.tts_engine,
        tts_voice=runtime.config.voice.selected_voice,
        stt_engine=runtime.config.voice.stt_engine,
        tts_ready=Path(runtime.config.voice.piper_binary_path).exists() and Path(runtime.config.voice.piper_voice_path).exists() if runtime.config.voice.tts_engine == "piper" else True,
        ollama_models=models,
    )


class HudDashboard:
    def __init__(self, runtime: AuroraRuntime, snapshot: HudSnapshot | None = None) -> None:
        self.runtime = runtime
        self.snapshot = snapshot or build_hud_snapshot(runtime)
        self.root: Tk | None = None
        self.avatar: Canvas | None = None
        self.status_text: StringVar | None = None
        self.input_text: StringVar | None = None
        self.convo: Frame | None = None
        self.core: IsisAssistantCore | None = None
        self._busy = False
        self._cancel_requested = False
        self._tick = 0

    def run(self) -> None:
        root = Tk()
        self.root = root
        self.status_text = StringVar(root, value="Sistema local pronto")
        self.input_text = StringVar(root)
        root.title(f"{self.snapshot.assistant_name} Command Interface")
        root.geometry("1280x760")
        root.minsize(1024, 640)
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", self._close)

        self._build(root)
        self._animate()
        root.mainloop()

    def _build(self, root: Tk) -> None:
        self._top_bar(root).pack(side=TOP, fill="x")
        shell = Frame(root, bg=BG)
        shell.pack(fill=BOTH, expand=True, padx=14, pady=(8, 10))
        self._left_nav(shell).pack(side=LEFT, fill="y", padx=(0, 10))
        self._center(shell).pack(side=LEFT, fill=BOTH, expand=True)
        self._right_panel(shell).pack(side=RIGHT, fill="y", padx=(10, 0))
        self._footer(root).pack(side=BOTTOM, fill="x", padx=14, pady=(0, 12))

    def _top_bar(self, root: Tk) -> Frame:
        frame = Frame(root, bg=BG, height=72)
        frame.pack_propagate(False)
        left = Frame(frame, bg=BG)
        left.pack(side=LEFT, fill="y", padx=16)
        Label(left, text=self.snapshot.assistant_name, fg=CYAN, bg=BG, font=("Segoe UI Semibold", 24)).pack(anchor="w")
        Label(left, text="LOCAL AI COMMAND SYSTEM", fg=MUTED, bg=BG, font=("Segoe UI", 9)).pack(anchor="w")
        metrics = Frame(frame, bg=BG)
        metrics.pack(side=RIGHT, padx=16)
        for label, value, color in [
            ("RAM", f"{self.snapshot.ram_available_mb} MB", TEAL),
            ("VRAM", f"{self.snapshot.vram_available_mb} MB", CYAN),
            ("NET", "OFF" if not self.snapshot.internet_enabled else "ON", WARN if not self.snapshot.internet_enabled else TEAL),
            ("MIC", "OFF" if not self.snapshot.microphone_enabled else "ON", WARN if not self.snapshot.microphone_enabled else TEAL),
            ("VOICE", "ON" if self.snapshot.tts_ready else "OFF", TEAL if self.snapshot.tts_ready else WARN),
            ("MODE", self.snapshot.profile, BLUE),
        ]:
            self._metric(metrics, label, value, color).pack(side=LEFT, padx=6)
        return frame

    def _metric(self, root: Frame, label: str, value: str, color: str) -> Frame:
        box = Frame(root, bg=PANEL, highlightbackground=color, highlightthickness=1, padx=10, pady=6)
        Label(box, text=label, fg=MUTED, bg=PANEL, font=("Segoe UI", 8)).pack(anchor="w")
        Label(box, text=value, fg=color, bg=PANEL, font=("Segoe UI Semibold", 10)).pack(anchor="w")
        return box

    def _left_nav(self, root: Frame) -> Frame:
        frame = Frame(root, bg=PANEL, width=178, padx=12, pady=14, highlightbackground="#12313d", highlightthickness=1)
        frame.pack_propagate(False)
        Label(frame, text="NAVEGACAO", fg=MUTED, bg=PANEL, font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 10))
        for text, color in [
            ("Conversa", CYAN),
            ("Memoria", MEMORY),
            ("Projetos", TEAL),
            ("Documentos", "#62ff94"),
            ("Automacoes", WARN),
            ("Agenda", CYAN),
            ("Configuracoes", WHITE),
        ]:
            Label(frame, text=text, fg=color, bg=PANEL, font=("Segoe UI Semibold", 11), pady=7).pack(anchor="w")
        return frame

    def _center(self, root: Frame) -> Frame:
        frame = Frame(root, bg=PANEL_2, padx=16, pady=14, highlightbackground="#17495a", highlightthickness=1)
        header = Frame(frame, bg=PANEL_2)
        header.pack(fill="x")
        Label(header, text="CANAL PRINCIPAL", fg=MUTED, bg=PANEL_2, font=("Segoe UI", 8)).pack(anchor="w")
        Label(header, textvariable=self.status_text, fg=WHITE, bg=PANEL_2, font=("Segoe UI Semibold", 13)).pack(anchor="w")
        self.convo = Frame(frame, bg=PANEL_2)
        self.convo.pack(fill=BOTH, expand=True, pady=(18, 0))
        self._add_message("Sistema", "Ollama local ativo. Modelo de codigo: " + self.snapshot.coding_model, CYAN)
        self._add_message("Memoria", "Memoria local pronta para consulta. Indexacao semantica segue em segundo plano.", MEMORY)
        self._add_message("ISIS", "Pronta para comandos locais. Internet e automacao real permanecem sob politica de seguranca.", TEAL)
        return frame

    def _bubble(self, root: Frame, author: str, text: str, color: str) -> Frame:
        box = Frame(root, bg="#081018", padx=12, pady=10, highlightbackground=color, highlightthickness=1)
        Label(box, text=author.upper(), fg=color, bg="#081018", font=("Segoe UI", 8)).pack(anchor="w")
        Label(box, text=text, fg=WHITE, bg="#081018", font=("Segoe UI", 11), wraplength=620, justify=LEFT).pack(anchor="w", pady=(4, 0))
        return box

    def _right_panel(self, root: Frame) -> Frame:
        frame = Frame(root, bg=PANEL, width=300, padx=12, pady=14, highlightbackground="#12313d", highlightthickness=1)
        frame.pack_propagate(False)
        Label(frame, text="NUCLEO IA", fg=MUTED, bg=PANEL, font=("Segoe UI", 8)).pack(anchor="w")
        self.avatar = Canvas(frame, width=220, height=220, bg=PANEL, highlightthickness=0)
        self.avatar.pack(pady=(8, 12))
        for label, value, color in [
            ("Modelo codigo", self.snapshot.coding_model, CYAN),
            ("Embeddings", self.snapshot.embedding_model, MEMORY),
            ("Voz", f"{self.snapshot.tts_engine} / {self.snapshot.tts_voice}", TEAL if self.snapshot.tts_ready else WARN),
            ("Notas indexadas", str(self.snapshot.project_notes_indexed), TEAL),
            ("Offline", "sim" if self.snapshot.offline_mode else "nao", WARN),
            ("Ollama models", str(len(self.snapshot.ollama_models)), BLUE),
        ]:
            self._intel_row(frame, label, value, color).pack(fill="x", pady=4)
        return frame

    def _intel_row(self, root: Frame, label: str, value: str, color: str) -> Frame:
        row = Frame(root, bg=PANEL)
        Label(row, text=label, fg=MUTED, bg=PANEL, font=("Segoe UI", 9)).pack(anchor="w")
        Label(row, text=value, fg=color, bg=PANEL, font=("Segoe UI Semibold", 10), wraplength=250, justify=LEFT).pack(anchor="w")
        return row

    def _footer(self, root: Tk) -> Frame:
        frame = Frame(root, bg=BG)
        entry = Entry(frame, textvariable=self.input_text, bg="#071018", fg=WHITE, insertbackground=CYAN, relief="flat", font=("Segoe UI", 12))
        entry.pack(side=LEFT, fill="x", expand=True, ipady=10)
        entry.insert(0, "Digite um comando para ISIS...")
        entry.bind("<FocusIn>", self._clear_placeholder)
        entry.bind("<Return>", lambda _: self._send_prompt())
        Button(frame, text="VOZ TESTE", command=self._speak_status, fg=TEAL, bg=PANEL, activebackground="#102530", activeforeground=WHITE, relief="flat", font=("Segoe UI Semibold", 10), padx=12, pady=9).pack(side=LEFT, padx=(8, 0))
        Button(frame, text="MIC", command=self._mic_status, fg=CYAN, bg=PANEL, activebackground="#102530", activeforeground=WHITE, relief="flat", font=("Segoe UI Semibold", 10), padx=14, pady=9).pack(side=LEFT, padx=(8, 0))
        Button(frame, text="ANEXO", command=self._attachment_status, fg=TEAL, bg=PANEL, activebackground="#102530", activeforeground=WHITE, relief="flat", font=("Segoe UI Semibold", 10), padx=14, pady=9).pack(side=LEFT, padx=(8, 0))
        Button(frame, text="ENVIAR", command=self._send_prompt, fg=BLUE, bg=PANEL, activebackground="#102530", activeforeground=WHITE, relief="flat", font=("Segoe UI Semibold", 10), padx=14, pady=9).pack(side=LEFT, padx=(8, 0))
        Button(frame, text="PARAR", command=self._stop_response, fg=WARN, bg=PANEL, activebackground="#102530", activeforeground=WHITE, relief="flat", font=("Segoe UI Semibold", 10), padx=14, pady=9).pack(side=LEFT, padx=(8, 0))
        return frame

    def _clear_placeholder(self, _: object) -> None:
        if self.input_text and self.input_text.get() == "Digite um comando para ISIS...":
            self.input_text.set("")

    def _add_message(self, author: str, text: str, color: str) -> None:
        if not self.convo:
            return
        self._bubble(self.convo, author, text, color).pack(fill="x", pady=6)

    def _set_status(self, text: str) -> None:
        if self.status_text:
            self.status_text.set(text)

    def _ensure_core(self) -> IsisAssistantCore:
        if not self.core:
            self.core = IsisAssistantCore(self.runtime.root)
            self.core.initialize()
        return self.core

    def _send_prompt(self) -> None:
        if self._busy or not self.input_text:
            return
        prompt = self.input_text.get().strip()
        if not prompt or prompt == "Digite um comando para ISIS...":
            self._set_status("Digite um comando valido")
            return
        self.input_text.set("")
        self._busy = True
        self._cancel_requested = False
        self._add_message("Voce", prompt, BLUE)
        self._set_status("Processando no modelo local...")
        threading.Thread(target=self._generate_worker, args=(prompt,), daemon=True).start()

    def _generate_worker(self, prompt: str) -> None:
        try:
            result = self._ensure_core().generate_text(prompt)
            response = hud_response_text(result)
        except Exception as exc:
            response = f"Falha ao gerar resposta: {exc}"
        if self.root:
            self.root.after(0, lambda: self._finish_response(response))

    def _finish_response(self, response: str) -> None:
        self._busy = False
        if self._cancel_requested:
            self._set_status("Resposta interrompida")
            return
        self._add_message("ISIS", response, TEAL)
        self._set_status("Resposta pronta")
        if self.snapshot.tts_ready:
            threading.Thread(target=self._speak_text, args=(response,), daemon=True).start()

    def _speak_text(self, text: str) -> None:
        try:
            session = build_voice_session(self.runtime.config, self.runtime.audit, transcript="hud")
            output = session.tts.synthesize(speech_excerpt(text), self.runtime.config.voice.selected_voice)
            session.audio_out.enqueue(output)
            session.audio_out.play_next()
        except Exception as exc:
            if self.root:
                self.root.after(0, lambda: self._set_status(f"Falha na voz: {exc}"))

    def _speak_status(self) -> None:
        try:
            session = build_voice_session(self.runtime.config, self.runtime.audit, transcript="status")
            output = session.tts.synthesize("ISIS voz local ativa. Interface de comando operacional.", self.runtime.config.voice.selected_voice)
            session.audio_out.enqueue(output)
            session.audio_out.play_next()
            self._set_status(f"Voz gerada: {output.name}")
        except Exception as exc:
            self._set_status(f"Falha na voz: {exc}")

    def _mic_status(self) -> None:
        self._set_status("Microfone real ainda desativado; STT atual: " + self.runtime.config.voice.stt_engine)

    def _attachment_status(self) -> None:
        self._set_status("Anexos ainda nao habilitados nesta HUD")

    def _stop_response(self) -> None:
        self._cancel_requested = True
        self._set_status("Parada solicitada")

    def _close(self) -> None:
        if self.core:
            self.core.shutdown("hud")
        if self.root:
            self.root.destroy()

    def _animate(self) -> None:
        if not self.root or not self.avatar:
            return
        canvas = self.avatar
        canvas.delete("all")
        cx = cy = 110
        phase = self._tick / 12
        for idx, radius in enumerate([34, 56, 78]):
            pulse = math.sin(phase + idx) * 4
            color = [CYAN, BLUE, TEAL][idx]
            canvas.create_oval(cx - radius - pulse, cy - radius - pulse, cx + radius + pulse, cy + radius + pulse, outline=color, width=2)
        for idx in range(18):
            angle = phase + idx * (math.pi * 2 / 18)
            inner = 82
            outer = 98 + math.sin(phase + idx) * 6
            canvas.create_line(cx + math.cos(angle) * inner, cy + math.sin(angle) * inner, cx + math.cos(angle) * outer, cy + math.sin(angle) * outer, fill=CYAN)
        canvas.create_text(cx, cy - 8, text="ISIS", fill=WHITE, font=("Segoe UI Semibold", 22))
        canvas.create_text(cx, cy + 18, text="ONLINE LOCAL", fill=TEAL, font=("Segoe UI", 8))
        self._tick += 1
        self.root.after(80, self._animate)
