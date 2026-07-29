from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_STATUSES = {"planejamento", "em desenvolvimento", "em testes", "pausado", "concluido", "arquivado"}


@dataclass(frozen=True, slots=True)
class StoredMessage:
    role: str
    content: str
    model: str = ""
    metadata: dict[str, Any] | None = None


class ConversationStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _init(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                  id TEXT PRIMARY KEY,
                  name TEXT NOT NULL UNIQUE,
                  description TEXT NOT NULL DEFAULT '',
                  objective TEXT NOT NULL DEFAULT '',
                  status TEXT NOT NULL DEFAULT 'em desenvolvimento',
                  local_dir TEXT NOT NULL DEFAULT '',
                  git_repo TEXT NOT NULL DEFAULT '',
                  technologies TEXT NOT NULL DEFAULT '',
                  rules TEXT NOT NULL DEFAULT '',
                  decisions TEXT NOT NULL DEFAULT '',
                  pending_tasks TEXT NOT NULL DEFAULT '',
                  completed_tasks TEXT NOT NULL DEFAULT '',
                  errors TEXT NOT NULL DEFAULT '',
                  solutions TEXT NOT NULL DEFAULT '',
                  permission_level TEXT NOT NULL DEFAULT 'MEDIUM',
                  favorite INTEGER NOT NULL DEFAULT 0,
                  archived INTEGER NOT NULL DEFAULT 0,
                  created_at REAL NOT NULL,
                  updated_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                  id TEXT PRIMARY KEY,
                  title TEXT NOT NULL,
                  project_id TEXT,
                  summary TEXT NOT NULL DEFAULT '',
                  topics TEXT NOT NULL DEFAULT '',
                  favorite INTEGER NOT NULL DEFAULT 0,
                  archived INTEGER NOT NULL DEFAULT 0,
                  deleted INTEGER NOT NULL DEFAULT 0,
                  created_at REAL NOT NULL,
                  updated_at REAL NOT NULL,
                  model TEXT NOT NULL DEFAULT '',
                  message_count INTEGER NOT NULL DEFAULT 0,
                  attachments_count INTEGER NOT NULL DEFAULT 0,
                  tools_count INTEGER NOT NULL DEFAULT 0,
                  FOREIGN KEY(project_id) REFERENCES projects(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                  id TEXT PRIMARY KEY,
                  conversation_id TEXT NOT NULL,
                  role TEXT NOT NULL,
                  content TEXT NOT NULL,
                  model TEXT NOT NULL DEFAULT '',
                  metadata_json TEXT NOT NULL DEFAULT '{}',
                  created_at REAL NOT NULL,
                  FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at)")
            self.ensure_project("ISIS", description="Assistente local offline-first.", objective="Operar HUD, voz, memoria e projetos locais.", local_dir=r"D:\ISIS_IA\AURORA")

    def ensure_project(self, name: str, **fields: Any) -> str:
        now = time.time()
        clean_name = (name or "ISIS").strip()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT id FROM projects WHERE name = ?", (clean_name,)).fetchone()
            if row:
                return str(row[0])
            project_id = str(uuid.uuid4())
            status = str(fields.get("status") or "em desenvolvimento")
            if status not in PROJECT_STATUSES:
                status = "em desenvolvimento"
            conn.execute(
                """
                INSERT INTO projects
                (id, name, description, objective, status, local_dir, git_repo, technologies, rules, decisions,
                 pending_tasks, completed_tasks, errors, solutions, permission_level, favorite, archived, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?)
                """,
                (
                    project_id,
                    clean_name,
                    str(fields.get("description") or ""),
                    str(fields.get("objective") or ""),
                    status,
                    str(fields.get("local_dir") or ""),
                    str(fields.get("git_repo") or ""),
                    str(fields.get("technologies") or ""),
                    str(fields.get("rules") or ""),
                    str(fields.get("decisions") or ""),
                    str(fields.get("pending_tasks") or ""),
                    str(fields.get("completed_tasks") or ""),
                    str(fields.get("errors") or ""),
                    str(fields.get("solutions") or ""),
                    str(fields.get("permission_level") or "MEDIUM"),
                    now,
                    now,
                ),
            )
            return project_id

    def start_conversation(self, prompt: str, project_id: str | None = None, model: str = "") -> str:
        now = time.time()
        title = self._title_from_prompt(prompt)
        final_project_id = project_id or self.ensure_project("ISIS")
        conversation_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO conversations
                (id, title, project_id, created_at, updated_at, model, message_count)
                VALUES (?, ?, ?, ?, ?, ?, 0)
                """,
                (conversation_id, title, final_project_id, now, now, model),
            )
        return conversation_id

    def add_message(self, conversation_id: str, message: StoredMessage) -> None:
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    str(uuid.uuid4()),
                    conversation_id,
                    message.role,
                    message.content,
                    message.model,
                    json.dumps(message.metadata or {}, ensure_ascii=False),
                    now,
                ),
            )
            conn.execute(
                """
                UPDATE conversations
                SET updated_at = ?, model = COALESCE(NULLIF(?, ''), model),
                    message_count = (SELECT COUNT(*) FROM messages WHERE conversation_id = ?),
                    summary = ?
                WHERE id = ?
                """,
                (now, message.model, conversation_id, self._summary_for(conversation_id, message.content), conversation_id),
            )

    def list_projects(self, limit: int = 20) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT p.*, COUNT(c.id) AS conversations
                FROM projects p
                LEFT JOIN conversations c ON c.project_id = p.id AND c.deleted = 0
                WHERE p.archived = 0
                GROUP BY p.id
                ORDER BY p.favorite DESC, p.updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]

    def list_conversations(self, limit: int = 30, query: str = "") -> list[dict[str, Any]]:
        where = "deleted = 0"
        params: list[Any] = []
        if query:
            where += " AND title LIKE ?"
            params.append(f"%{query}%")
        params.append(limit)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                f"""
                SELECT c.*, p.name AS project_name
                FROM conversations c
                LEFT JOIN projects p ON p.id = c.project_id
                WHERE {where}
                ORDER BY c.favorite DESC, c.updated_at DESC
                LIMIT ?
                """,
                params,
            ).fetchall()
            return [dict(row) for row in rows]

    def get_conversation(self, conversation_id: str) -> dict[str, Any] | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            conv = conn.execute("SELECT * FROM conversations WHERE id = ? AND deleted = 0", (conversation_id,)).fetchone()
            if not conv:
                return None
            messages = conn.execute("SELECT role, content, model, metadata_json, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at", (conversation_id,)).fetchall()
            payload = dict(conv)
            payload["messages"] = [dict(row) for row in messages]
            return payload

    def search(self, query: str, limit: int = 20) -> dict[str, list[dict[str, Any]]]:
        like = f"%{query}%"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            conversations = conn.execute(
                "SELECT * FROM conversations WHERE deleted = 0 AND (title LIKE ? OR summary LIKE ?) ORDER BY updated_at DESC LIMIT ?",
                (like, like, limit),
            ).fetchall()
            messages = conn.execute(
                "SELECT conversation_id, role, content, model, created_at FROM messages WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?",
                (like, limit),
            ).fetchall()
            projects = conn.execute(
                "SELECT * FROM projects WHERE archived = 0 AND (name LIKE ? OR description LIKE ? OR objective LIKE ?) ORDER BY updated_at DESC LIMIT ?",
                (like, like, like, limit),
            ).fetchall()
            return {
                "projects": [dict(row) for row in projects],
                "conversations": [dict(row) for row in conversations],
                "messages": [dict(row) for row in messages],
            }

    def _title_from_prompt(self, prompt: str) -> str:
        title = " ".join((prompt or "Nova conversa").split())[:64].strip()
        return title or "Nova conversa"

    def _summary_for(self, conversation_id: str, latest: str) -> str:
        current = self.get_conversation(conversation_id)
        if not current:
            return " ".join(latest.split())[:240]
        first = current.get("summary") or ""
        text = " ".join([first, latest]).strip()
        return " ".join(text.split())[:500]
