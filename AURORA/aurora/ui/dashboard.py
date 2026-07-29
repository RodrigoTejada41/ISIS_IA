from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from tkinter import BOTH, LEFT, StringVar, Tk, messagebox, simpledialog, ttk

from aurora.automation.action_audit import UIActionAuditLogger
from aurora.core.runtime import AuroraRuntime
from aurora.ui.privileges import PrivilegeControlService
from aurora.ui.memory_panel import MemoryPanelService
from aurora.ui.skills_panel import SkillPanelService
from aurora.ui.audit_panel import AuditPanelService


@dataclass(slots=True)
class DashboardSnapshot:
    assistant_name: str
    profile: str
    offline_mode: bool
    internet_enabled: bool
    microphone_enabled: bool
    screen_analysis_enabled: bool
    real_screen_capture_enabled: bool
    real_ui_execution_enabled: bool
    obsidian_mode: str
    memory_records: int
    project_notes_indexed: int
    last_ui_actions: int
    ram_available_mb: int
    vram_available_mb: int


def build_dashboard_snapshot(runtime: AuroraRuntime) -> DashboardSnapshot:
    snap = runtime.resources.snapshot()
    isis_root = Path(runtime.config.paths.isis_root)
    return DashboardSnapshot(
        assistant_name=runtime.config.assistant_name,
        profile=runtime.policy.profile.value,
        offline_mode=runtime.config.privacy.offline_mode,
        internet_enabled=runtime.config.privacy.internet_enabled,
        microphone_enabled=runtime.config.privacy.microphone_enabled,
        screen_analysis_enabled=runtime.config.privacy.screen_analysis_enabled,
        real_screen_capture_enabled=False,
        real_ui_execution_enabled=False,
        obsidian_mode=runtime.config.obsidian.integration_mode,
        memory_records=_count_sqlite_rows(runtime.root / "data" / "memory" / "memory.sqlite", "memory_records"),
        project_notes_indexed=_count_sqlite_rows(isis_root / "data" / "databases" / "project_memory.sqlite", "indexed_notes"),
        last_ui_actions=len(UIActionAuditLogger(isis_root / "logs" / "automation" / "ui_actions.jsonl").tail(50)),
        ram_available_mb=snap.ram_available_mb,
        vram_available_mb=snap.vram_available_mb,
    )


class LocalDashboard:
    def __init__(self, snapshot: DashboardSnapshot, runtime: AuroraRuntime | None = None) -> None:
        self.snapshot = snapshot
        self.runtime = runtime

    def run(self) -> None:
        root = Tk()
        root.title("ISIS Local Dashboard")
        root.geometry("760x460")
        root.minsize(640, 420)

        container = ttk.Frame(root, padding=16)
        container.pack(fill=BOTH, expand=True)

        title = ttk.Label(container, text=f"{self.snapshot.assistant_name} - Local Dashboard", font=("Segoe UI", 16, "bold"))
        title.pack(anchor="w")

        notebook = ttk.Notebook(container)
        notebook.pack(fill=BOTH, expand=True, pady=(12, 0))

        self._add_tab(notebook, "Status", self._status_rows())
        self._add_permissions_tab(notebook)
        self._add_memory_tab(notebook)
        self._add_skills_tab(notebook)
        self._add_audit_tab(notebook)

        root.mainloop()

    def _add_tab(self, notebook: ttk.Notebook, title: str, rows: list[tuple[str, str]]) -> None:
        frame = ttk.Frame(notebook, padding=12)
        notebook.add(frame, text=title)
        for label, value in rows:
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=label, width=28).pack(side=LEFT)
            ttk.Label(row, text=value).pack(side=LEFT)
        ttk.Button(frame, text="Regenerate reports", command=lambda: self._regenerate_reports()).pack(anchor="w", pady=(16, 0))

    def _regenerate_reports(self) -> None:
        if not self.runtime:
            return
        result = AuditPanelService(self.runtime).regenerate_reports()
        messagebox.showinfo("Audit", "Reports regenerated" if result.signature_ok else "Reports regenerated with signature failure")

    def _add_permissions_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=12)
        notebook.add(frame, text="Permissions")
        for label, value in self._permission_rows():
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=label, width=28).pack(side=LEFT)
            ttk.Label(row, text=value).pack(side=LEFT)
        if not self.runtime:
            return
        service = PrivilegeControlService(self.runtime)
        state = service.state()
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(16, 4))
        ttk.Label(row, text="Profile control", width=28).pack(side=LEFT)
        selected = StringVar(value=state.current_profile)
        combo = ttk.Combobox(row, values=state.available_profiles, textvariable=selected, state="readonly" if state.editable else "disabled")
        combo.pack(side=LEFT)
        button = ttk.Button(row, text="Apply", command=lambda: self._apply_profile(service, selected.get()))
        button.pack(side=LEFT, padx=(8, 0))
        if not state.editable:
            button.state(["disabled"])
            ttk.Label(frame, text=state.reason).pack(anchor="w", pady=(4, 0))
        emergency = ttk.Button(frame, text="Emergency stop", command=lambda: self._emergency_stop(service))
        emergency.pack(anchor="w", pady=(16, 0))

    def _apply_profile(self, service: PrivilegeControlService, profile: str) -> None:
        password = simpledialog.askstring("Authentication", "Local admin password", show="*")
        if password is None:
            return
        result = service.change_profile(profile, password)
        if result.changed:
            messagebox.showinfo("Profile", f"Profile changed to {result.profile}")
        else:
            messagebox.showerror("Profile", result.reason)

    def _emergency_stop(self, service: PrivilegeControlService) -> None:
        result = service.emergency_stop()
        messagebox.showinfo("Emergency", result.reason)

    def _status_rows(self) -> list[tuple[str, str]]:
        return [
            ("Profile", self.snapshot.profile),
            ("Offline mode", _yes_no(self.snapshot.offline_mode)),
            ("Obsidian mode", self.snapshot.obsidian_mode),
            ("RAM available MB", str(self.snapshot.ram_available_mb)),
            ("VRAM available MB", str(self.snapshot.vram_available_mb)),
        ]

    def _permission_rows(self) -> list[tuple[str, str]]:
        return [
            ("Internet enabled", _yes_no(self.snapshot.internet_enabled)),
            ("Microphone enabled", _yes_no(self.snapshot.microphone_enabled)),
            ("Screen analysis enabled", _yes_no(self.snapshot.screen_analysis_enabled)),
            ("Real screen capture", _yes_no(self.snapshot.real_screen_capture_enabled)),
            ("Real UI execution", _yes_no(self.snapshot.real_ui_execution_enabled)),
        ]

    def _memory_rows(self) -> list[tuple[str, str]]:
        return [
            ("Local memory records", str(self.snapshot.memory_records)),
            ("Project notes indexed", str(self.snapshot.project_notes_indexed)),
            ("Recent UI actions", str(self.snapshot.last_ui_actions)),
        ]

    def _add_memory_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=12)
        notebook.add(frame, text="Memory")
        for label, value in self._memory_rows():
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=label, width=28).pack(side=LEFT)
            ttk.Label(row, text=value).pack(side=LEFT)
        if not self.runtime:
            return
        service = MemoryPanelService(self.runtime)
        filter_row = ttk.Frame(frame)
        filter_row.pack(fill="x", pady=(8, 0))
        ttk.Label(filter_row, text="Status filter", width=28).pack(side=LEFT)
        selected_status = StringVar(value="ALL")
        ttk.Combobox(filter_row, values=["ALL", "PROPOSED", "CONFIRMED", "REJECTED", "ARCHIVED"], textvariable=selected_status, state="readonly").pack(side=LEFT)
        tree = ttk.Treeview(frame, columns=("id", "type", "status", "content"), show="headings", height=8)
        tree.heading("id", text="ID")
        tree.heading("type", text="Type")
        tree.heading("status", text="Status")
        tree.heading("content", text="Content")
        tree.pack(fill=BOTH, expand=True, pady=(12, 0))
        tree.column("id", width=90)
        self._populate_memory_tree(tree, service, selected_status.get())
        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Confirm", command=lambda: self._memory_action(tree, service, "CONFIRMED")).pack(side=LEFT)
        ttk.Button(actions, text="Reject", command=lambda: self._memory_action(tree, service, "REJECTED")).pack(side=LEFT, padx=(8, 0))
        ttk.Button(actions, text="Refresh", command=lambda: self._populate_memory_tree(tree, service, selected_status.get())).pack(side=LEFT, padx=(8, 0))

    def _populate_memory_tree(self, tree: ttk.Treeview, service: MemoryPanelService, status: str) -> None:
        for item in tree.get_children():
            tree.delete(item)
        status_filter = None if status == "ALL" else status
        for item in service.list_records(status_filter, limit=20):
            tree.insert("", "end", values=(item.id, item.type, item.status, item.content_preview))

    def _memory_action(self, tree: ttk.Treeview, service: MemoryPanelService, status: str) -> None:
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Memory", "Select a memory record")
            return
        values = tree.item(selected[0], "values")
        result = service.set_status(str(values[0]), status)
        if result.ok:
            messagebox.showinfo("Memory", result.reason)
        else:
            messagebox.showerror("Memory", result.reason)

    def _add_skills_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=12)
        notebook.add(frame, text="Skills")
        if not self.runtime:
            ttk.Label(frame, text="Runtime unavailable").pack(anchor="w")
            return
        tree = ttk.Treeview(frame, columns=("version", "risk", "auth"), show="headings", height=12)
        tree.heading("version", text="Version")
        tree.heading("risk", text="Risk")
        tree.heading("auth", text="Authorization")
        tree.pack(fill=BOTH, expand=True)
        tree.column("version", width=90)
        tree.column("risk", width=110)
        tree.column("auth", width=180)
        for item in SkillPanelService(self.runtime).list_skills():
            tree.insert("", "end", values=(f"{item.display_name} {item.version}", item.risk, item.authorization))

    def _add_audit_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=12)
        notebook.add(frame, text="Audit")
        if not self.runtime:
            ttk.Label(frame, text="Runtime unavailable").pack(anchor="w")
            return
        snapshot = AuditPanelService(self.runtime).snapshot()
        rows = [
            ("UI actions", str(snapshot.ui_actions)),
            ("Privilege events", str(snapshot.privilege_events)),
            ("Memory events", str(snapshot.memory_events)),
            ("Report integrity", _yes_no(snapshot.report_integrity_ok)),
            ("Signature key restricted", _yes_no(snapshot.signature_key_restricted)),
            ("Report history count", str(snapshot.report_history_count)),
            ("Last report generated", snapshot.last_report_generated_at or ""),
            ("Reports root", snapshot.reports_root),
        ]
        for label, value in rows:
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=label, width=28).pack(side=LEFT)
            ttk.Label(row, text=value).pack(side=LEFT)


def _count_sqlite_rows(db_path: Path, table: str) -> int:
    if not db_path.exists():
        return 0
    try:
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        return int(row[0]) if row else 0
    except sqlite3.Error:
        return 0


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"
