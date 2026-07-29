from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from aurora.core.memory import MemoryRecord, MemoryStatus, MemoryType
from aurora.core.memory_audit import MemoryAuditLogger
from aurora.core.audit_report import AuditReportService
from aurora.core.report_integrity import ReportIntegrityService
from aurora.core.report_maintenance import ReportMaintenanceService
from aurora.core.local_signature import LocalSignatureService
from aurora.core.key_acl import KeyAclInspector, KeyAclManager
from aurora.core.auth import LocalAuthenticator
from aurora.core.permissions import PrivilegeProfile
from aurora.core.privilege_audit import PrivilegeAuditLogger
from aurora.core.project_memory import ObsidianReadOnlyIndexer, ProjectMemoryIndex
from aurora.core.project_catalog import ProjectCatalog
from aurora.core.hybrid_search import HybridSearchService
from aurora.core.embeddings import MemoryEmbeddingIndex, ProjectEmbeddingIndex, read_project_embedding_worker_history
from aurora.core.knowledge_records import KnowledgeRecordStore
from aurora.core.routing import RouteRequest
from aurora.core.runtime import AuroraRuntime
from aurora.core.assistant import IsisAssistantCore
from aurora.internet.download_manager import DownloadManager
from aurora.internet.internet_manager import InternetManager
from aurora.permissions.permission_engine import ActionContext, PermissionEngine
from aurora.permissions.profile_manager import PermissionProfileManager
from aurora.permissions.rule_activation import RuleActivationService
from aurora.permissions.rule_parser import RuleParser
from aurora.automation.ui import UIAutomationService
from aurora.automation.action_audit import PermissionPanelSnapshot, UIActionAuditLogger
from aurora.automation.screen_bridge import ScreenAutomationBridge
from aurora.perception.screen import MockScreenProvider, ScreenAnalyzer, ScreenPrivacyPolicy, ScreenVisionService
from aurora.ui.dashboard import LocalDashboard, build_dashboard_snapshot
from aurora.ui.hud_dashboard import HudDashboard, build_hud_snapshot
from aurora.ui.hud_web import HudWebServer
from aurora.ui.audit_panel import AuditPanelService
from aurora.ui.memory_panel import MemoryPanelService
from aurora.ui.privileges import PrivilegeControlService
from aurora.ui.skills_panel import SkillPanelService, parse_skill_kv_args
from aurora.voice.audio import AudioInputManager, AudioOutputManager
from aurora.voice.factory import build_voice_session
from aurora.voice.providers import MockSpeechToTextProvider, MockTextToSpeechProvider, MockWakeWordProvider
from aurora.voice.session import VoiceSessionManager
from aurora.voice.tts.piper_engine import AudioCache
from aurora.voice.voice_manager import VoiceManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aurora")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status")
    core = sub.add_parser("core")
    core.add_argument("text", nargs="?", default="status")
    generate = sub.add_parser("generate")
    generate.add_argument("prompt")
    index = sub.add_parser("index-obsidian")
    index.add_argument("--max-files", type=int)
    search_project = sub.add_parser("project-search")
    search_project.add_argument("query")
    project_embed = sub.add_parser("project-embed")
    project_embed.add_argument("--limit", type=int, default=50)
    project_embed.add_argument("--project")
    project_embed.add_argument("--category")
    project_embed_batch = sub.add_parser("project-embed-batch")
    project_embed_batch.add_argument("--batch-size", type=int, default=50)
    project_embed_batch.add_argument("--max-batches", type=int, default=1)
    project_embed_batch.add_argument("--project")
    project_embed_batch.add_argument("--category")
    project_embed_progress = sub.add_parser("project-embed-progress")
    project_embed_progress.add_argument("--project")
    project_embed_progress.add_argument("--category")
    project_embed_worker = sub.add_parser("project-embed-worker")
    project_embed_worker.add_argument("--batch-size", type=int, default=25)
    project_embed_worker.add_argument("--max-batches", type=int, default=10)
    project_embed_worker.add_argument("--max-seconds", type=int, default=300)
    project_embed_worker.add_argument("--project")
    project_embed_worker.add_argument("--category")
    project_embed_history = sub.add_parser("project-embed-history")
    project_embed_history.add_argument("--limit", type=int, default=20)
    project_semantic = sub.add_parser("project-semantic-search")
    project_semantic.add_argument("query")
    project_semantic.add_argument("--limit", type=int, default=10)
    project_semantic.add_argument("--project")
    project_semantic.add_argument("--category")
    hybrid = sub.add_parser("search")
    hybrid.add_argument("query")
    hybrid.add_argument("--limit", type=int, default=10)
    hybrid.add_argument("--project")
    hybrid.add_argument("--category")
    consolidate = sub.add_parser("consolidate-projects")
    consolidate.add_argument("--min-notes", type=int, default=3)
    list_projects = sub.add_parser("projects")
    list_projects.add_argument("--limit", type=int, default=20)
    import_records = sub.add_parser("import-knowledge-records")
    import_records.add_argument("--limit", type=int)
    decisions = sub.add_parser("decisions")
    decisions.add_argument("query", nargs="?", default="")
    bugs = sub.add_parser("bugs")
    bugs.add_argument("query", nargs="?", default="")
    sub.add_parser("security-status")
    sub.add_parser("screen-status")
    screen_mock = sub.add_parser("screen-mock")
    screen_mock.add_argument("--text", default="Menu Arquivo Editar\nCampo email\nBotao salvar\nErro login invalido")
    screen_mock.add_argument("--app", default="mock-app")
    ui_plan = sub.add_parser("ui-plan")
    ui_plan.add_argument("instruction")
    ui_action = sub.add_parser("ui-mock-action")
    ui_action.add_argument("instruction")
    ui_action.add_argument("--approve", action="store_true")
    bridge = sub.add_parser("screen-ui-suggest")
    bridge.add_argument("instruction")
    bridge.add_argument("--text", default="Campo email\nBotao salvar")
    bridge.add_argument("--approve", action="store_true")
    sub.add_parser("ui-permissions-status")
    ui_audit = sub.add_parser("ui-action-audit")
    ui_audit.add_argument("--limit", type=int, default=20)
    sub.add_parser("ui-snapshot")
    sub.add_parser("ui-hud-snapshot")
    sub.add_parser("ui-audit-snapshot")
    sub.add_parser("ui-dashboard")
    sub.add_parser("ui-hud")
    hud_web = sub.add_parser("ui-hud-web")
    hud_web.add_argument("--host", default="127.0.0.1")
    hud_web.add_argument("--port", type=int, default=8765)
    sub.add_parser("ui-privileges-status")
    sub.add_parser("emergency-stop")
    privilege_audit = sub.add_parser("privilege-audit")
    privilege_audit.add_argument("--limit", type=int, default=20)
    sub.add_parser("ui-skills-snapshot")
    ui_skill_run = sub.add_parser("ui-skill-run")
    ui_skill_run.add_argument("name")
    ui_skill_run.add_argument("--args", default="{}")
    ui_skill_run.add_argument("--arg", action="append", default=[])
    ui_skill_run.add_argument("--approve", action="store_true")
    ui_memory_list = sub.add_parser("ui-memory-list")
    ui_memory_list.add_argument("--status")
    ui_memory_list.add_argument("--limit", type=int, default=20)
    ui_memory_propose = sub.add_parser("ui-memory-propose")
    ui_memory_propose.add_argument("content")
    ui_memory_propose.add_argument("--type", default=MemoryType.PROJECT_KNOWLEDGE.value)
    ui_memory_propose.add_argument("--project")
    ui_memory_propose.add_argument("--tags", default="")
    ui_memory_status = sub.add_parser("ui-memory-status")
    ui_memory_status.add_argument("id")
    ui_memory_status.add_argument("status", choices=[item.value for item in MemoryStatus])
    ui_memory_export = sub.add_parser("ui-memory-export")
    ui_memory_export.add_argument("output")
    ui_memory_export.add_argument("--status")
    ui_memory_export.add_argument("--limit", type=int, default=100)
    ui_memory_export.add_argument("--format", choices=["json", "md"], default="json")
    memory_audit = sub.add_parser("memory-approval-audit")
    memory_audit.add_argument("--limit", type=int, default=20)
    audit_report = sub.add_parser("audit-report")
    audit_report.add_argument("output")
    audit_report.add_argument("--limit", type=int, default=100)
    audit_report.add_argument("--format", choices=["json", "md"], default="json")
    sub.add_parser("reports-regenerate")
    reports_history = sub.add_parser("reports-history")
    reports_history.add_argument("--limit", type=int, default=20)
    report_manifest = sub.add_parser("report-integrity")
    report_manifest.add_argument("output")
    report_verify = sub.add_parser("report-integrity-verify")
    report_verify.add_argument("manifest")
    sub.add_parser("signature-key-status")
    sign_report = sub.add_parser("sign-report")
    sign_report.add_argument("file")
    sign_report.add_argument("output")
    verify_signature = sub.add_parser("verify-signature")
    verify_signature.add_argument("file")
    verify_signature.add_argument("signature")
    sub.add_parser("signature-key-rotate")
    sub.add_parser("signature-key-acl-status")
    key_acl_apply = sub.add_parser("signature-key-acl-apply")
    key_acl_apply.add_argument("--apply", action="store_true")
    key_acl_rollback = sub.add_parser("signature-key-acl-rollback")
    key_acl_rollback.add_argument("backup")
    key_acl_rollback.add_argument("--apply", action="store_true")
    sub.add_parser("internet-status")
    sub.add_parser("internet-test")
    internet_search = sub.add_parser("internet-search")
    internet_search.add_argument("query")
    internet_search.add_argument("--mode", choices=["quick", "deep"], default="quick")
    internet_search.add_argument("--approve", action="store_true")
    internet_download = sub.add_parser("internet-download")
    internet_download.add_argument("url")
    internet_download.add_argument("--approve", action="store_true")
    sub.add_parser("internet-cache-clear")
    research_history = sub.add_parser("research-history")
    research_history.add_argument("--limit", type=int, default=20)
    rule_parse = sub.add_parser("rules-parse")
    rule_parse.add_argument("text")
    rule_apply = sub.add_parser("rules-apply")
    rule_apply.add_argument("text")
    rule_apply.add_argument("--approve", action="store_true")
    rules_history = sub.add_parser("rules-history")
    rules_history.add_argument("--limit", type=int, default=20)
    permission_sim = sub.add_parser("permission-simulate")
    permission_sim.add_argument("action")
    permission_sim.add_argument("--resource", default="")
    permission_sim.add_argument("--approve", action="store_true")
    temp_auth = sub.add_parser("permission-temp-add")
    temp_auth.add_argument("action")
    temp_auth.add_argument("--resource", default="")
    temp_auth.add_argument("--minutes", type=int, default=60)
    temp_auth.add_argument("--max-uses", type=int, default=1)
    sub.add_parser("permission-summary")
    sub.add_parser("permission-profiles")
    sub.add_parser("permission-emergency-block")
    sub.add_parser("auth-status")
    auth_bootstrap = sub.add_parser("auth-bootstrap")
    auth_bootstrap.add_argument("--overwrite", action="store_true")
    profile_set = sub.add_parser("profile-set")
    profile_set.add_argument("profile", choices=[item.value for item in PrivilegeProfile])

    route = sub.add_parser("route")
    route.add_argument("prompt")
    route.add_argument("--image", action="store_true")
    route.add_argument("--manual-model")

    mem_add = sub.add_parser("memory-add")
    mem_add.add_argument("content")
    mem_add.add_argument("--type", default=MemoryType.PROJECT_KNOWLEDGE.value)
    mem_add.add_argument("--confirm", action="store_true")

    mem_search = sub.add_parser("memory-search")
    mem_search.add_argument("query")
    mem_embed = sub.add_parser("memory-embed")
    mem_embed.add_argument("--limit", type=int, default=100)
    mem_semantic = sub.add_parser("memory-semantic-search")
    mem_semantic.add_argument("query")
    mem_semantic.add_argument("--limit", type=int, default=5)

    skill_list = sub.add_parser("skills")
    skill_list.add_argument("--json", action="store_true")

    skill_run = sub.add_parser("skill-run")
    skill_run.add_argument("name")
    skill_run.add_argument("--args", default="{}")

    voice = sub.add_parser("voice-mock")
    voice.add_argument("--transcript", default="qual o status da aurora")
    voice_core = sub.add_parser("voice-core")
    voice_core.add_argument("--transcript", default="status")
    voice_speak = sub.add_parser("voice-speak")
    voice_speak.add_argument("text")
    voice_speak.add_argument("--play", action="store_true")
    sub.add_parser("voice-status")
    voice_test = sub.add_parser("voice-test")
    voice_test.add_argument("text", nargs="?", default="Bom dia, Rodrigo. Estou pronta para ajudar.")
    voice_test.add_argument("--play", action="store_true")
    sub.add_parser("voice-cache-clear")
    sub.add_parser("voice-benchmark")

    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    runtime = AuroraRuntime(args.root)

    if args.command == "status":
        snap = runtime.resources.snapshot()
        print(
            json.dumps(
                {
                    "profile": runtime.policy.profile.value,
                    "online_enabled": runtime.config.online_enabled,
                    "ram_available_mb": snap.ram_available_mb,
                    "vram_available_mb": snap.vram_available_mb,
                    "models": len(runtime.config.models),
                },
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "core":
        core = IsisAssistantCore(args.root)
        core.initialize()
        result = core.handle_text(args.text)
        core.shutdown("cli")
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0

    if args.command == "generate":
        core = IsisAssistantCore(args.root)
        core.initialize()
        result = core.generate_text(args.prompt)
        core.shutdown("cli")
        print(json.dumps(result, ensure_ascii=False))
        return 0

    if args.command == "index-obsidian":
        index = ProjectMemoryIndex(Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_memory.sqlite", runtime.audit)
        result = ObsidianReadOnlyIndexer(runtime.config.obsidian.migrated_path, index, runtime.audit).index_markdown(args.max_files)
        print(json.dumps(result, ensure_ascii=False))
        return 0

    if args.command == "project-search":
        index = ProjectMemoryIndex(Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_memory.sqlite", runtime.audit)
        print(json.dumps(index.search(args.query), ensure_ascii=False))
        return 0

    if args.command == "project-embed":
        index = ProjectEmbeddingIndex(
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_memory.sqlite",
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_note_embeddings.sqlite",
            runtime.audit,
        )
        print(json.dumps(index.index_notes(args.limit, args.project, args.category), ensure_ascii=False))
        return 0

    if args.command == "project-embed-batch":
        index = ProjectEmbeddingIndex(
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_memory.sqlite",
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_note_embeddings.sqlite",
            runtime.audit,
        )
        print(json.dumps(index.index_batches(args.batch_size, args.max_batches, args.project, args.category), ensure_ascii=False))
        return 0

    if args.command == "project-embed-progress":
        index = ProjectEmbeddingIndex(
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_memory.sqlite",
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_note_embeddings.sqlite",
            runtime.audit,
        )
        print(json.dumps(index.progress(args.project, args.category), ensure_ascii=False))
        return 0

    if args.command == "project-embed-worker":
        index = ProjectEmbeddingIndex(
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_memory.sqlite",
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_note_embeddings.sqlite",
            runtime.audit,
        )
        history_path = Path(runtime.config.paths.isis_root) / "logs" / "memory" / "project_embedding_worker.jsonl"
        print(json.dumps(index.run_worker(args.batch_size, args.max_batches, args.max_seconds, args.project, args.category, history_path=history_path), ensure_ascii=False))
        return 0

    if args.command == "project-embed-history":
        history_path = Path(runtime.config.paths.isis_root) / "logs" / "memory" / "project_embedding_worker.jsonl"
        print(json.dumps(read_project_embedding_worker_history(history_path, args.limit), ensure_ascii=False))
        return 0

    if args.command == "project-semantic-search":
        index = ProjectEmbeddingIndex(
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_memory.sqlite",
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_note_embeddings.sqlite",
            runtime.audit,
        )
        print(json.dumps([asdict(item) for item in index.search(args.query, args.limit, args.project, args.category)], ensure_ascii=False))
        return 0

    if args.command == "search":
        service = HybridSearchService(
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_memory.sqlite",
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "obsidian_readonly.sqlite",
            runtime.audit,
        )
        print(json.dumps([asdict(item) for item in service.search(args.query, args.limit, args.project, args.category)], ensure_ascii=False))
        return 0

    if args.command == "consolidate-projects":
        catalog = ProjectCatalog(Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_catalog.sqlite", runtime.audit)
        result = catalog.consolidate_from_project_memory(Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_memory.sqlite", args.min_notes)
        print(json.dumps(result, ensure_ascii=False))
        return 0

    if args.command == "projects":
        catalog = ProjectCatalog(Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_catalog.sqlite", runtime.audit)
        print(json.dumps(catalog.list_projects(args.limit), ensure_ascii=False))
        return 0

    if args.command == "import-knowledge-records":
        store = KnowledgeRecordStore(Path(runtime.config.paths.isis_root) / "data" / "databases" / "knowledge_records.sqlite", runtime.audit)
        result = store.import_from_project_memory(Path(runtime.config.paths.isis_root) / "data" / "databases" / "project_memory.sqlite", args.limit)
        print(json.dumps(result, ensure_ascii=False))
        return 0

    if args.command == "decisions":
        store = KnowledgeRecordStore(Path(runtime.config.paths.isis_root) / "data" / "databases" / "knowledge_records.sqlite", runtime.audit)
        print(json.dumps(store.search_decisions(args.query), ensure_ascii=False))
        return 0

    if args.command == "bugs":
        store = KnowledgeRecordStore(Path(runtime.config.paths.isis_root) / "data" / "databases" / "knowledge_records.sqlite", runtime.audit)
        print(json.dumps(store.search_bugs(args.query), ensure_ascii=False))
        return 0

    if args.command == "security-status":
        core = IsisAssistantCore(args.root)
        core.initialize()
        result = core.tools.execute("security_status", {})
        core.shutdown("cli")
        print(json.dumps(result, ensure_ascii=False))
        return 0

    if args.command == "screen-status":
        policy = ScreenPrivacyPolicy(screen_analysis_enabled=runtime.config.privacy.screen_analysis_enabled)
        print(
            json.dumps(
                {
                    "screen_analysis_enabled": policy.screen_analysis_enabled,
                    "manual_only": True,
                    "real_capture_enabled": False,
                    "store_images": policy.store_images,
                    "allowed_modes": [mode.value for mode in policy.allowed_modes],
                    "blocked_apps": sorted(policy.blocked_apps),
                },
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "screen-mock":
        policy = ScreenPrivacyPolicy(screen_analysis_enabled=False)
        service = ScreenVisionService(MockScreenProvider(args.text), ScreenAnalyzer(policy), policy)
        result = service.capture_and_analyze(manual_confirmed=True, app_name=args.app)
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0

    if args.command == "ui-plan":
        actions = UIAutomationService().plan_from_instruction(args.instruction)
        print(json.dumps([asdict(action) for action in actions], ensure_ascii=False))
        return 0

    if args.command == "ui-mock-action":
        service = UIAutomationService()
        action = service.plan_from_instruction(args.instruction)[0]
        result = service.execute(action, approved=args.approve)
        audit_path = Path(runtime.config.paths.isis_root) / "logs" / "automation" / "ui_actions.jsonl"
        UIActionAuditLogger(audit_path).record(result, approved=args.approve, real_execution=False)
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0 if result.status.value == "EXECUTED" else 2

    if args.command == "screen-ui-suggest":
        frame = MockScreenProvider(args.text).capture()
        bridge = ScreenAutomationBridge()
        suggestion = bridge.suggest(frame, args.instruction)
        result = bridge.suggest_and_execute_mock(frame, args.instruction, approved=args.approve)
        audit_path = Path(runtime.config.paths.isis_root) / "logs" / "automation" / "ui_actions.jsonl"
        UIActionAuditLogger(audit_path).record(result, approved=args.approve, real_execution=False)
        print(json.dumps({"suggestion": asdict(suggestion), "result": asdict(result)}, ensure_ascii=False))
        return 0 if result.status.value == "EXECUTED" else 2

    if args.command == "ui-permissions-status":
        policy = UIAutomationService().policy
        snapshot = PermissionPanelSnapshot(
            real_ui_execution_enabled=policy.real_execution_enabled,
            approval_per_action=policy.require_approval_per_action,
            screen_real_capture_enabled=False,
            screen_storage_enabled=False,
            blocked_targets=sorted(policy.blocked_targets),
        )
        print(json.dumps(asdict(snapshot), ensure_ascii=False))
        return 0

    if args.command == "ui-action-audit":
        audit_path = Path(runtime.config.paths.isis_root) / "logs" / "automation" / "ui_actions.jsonl"
        print(json.dumps(UIActionAuditLogger(audit_path).tail(args.limit), ensure_ascii=False))
        return 0

    if args.command == "ui-snapshot":
        print(json.dumps(asdict(build_dashboard_snapshot(runtime)), ensure_ascii=False))
        return 0

    if args.command == "ui-hud-snapshot":
        print(json.dumps(asdict(build_hud_snapshot(runtime)), ensure_ascii=False))
        return 0

    if args.command == "ui-audit-snapshot":
        print(json.dumps(asdict(AuditPanelService(runtime).snapshot()), ensure_ascii=False))
        return 0

    if args.command == "ui-dashboard":
        LocalDashboard(build_dashboard_snapshot(runtime), runtime).run()
        return 0

    if args.command == "ui-hud":
        HudDashboard(runtime).run()
        return 0

    if args.command == "ui-hud-web":
        HudWebServer(runtime).serve(args.host, args.port)
        return 0

    if args.command == "ui-privileges-status":
        print(json.dumps(asdict(PrivilegeControlService(runtime).state()), ensure_ascii=False))
        return 0

    if args.command == "emergency-stop":
        result = PrivilegeControlService(runtime).emergency_stop()
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0

    if args.command == "privilege-audit":
        audit_path = Path(runtime.config.paths.isis_root) / "logs" / "security" / "privileges.jsonl"
        print(json.dumps(PrivilegeAuditLogger(audit_path).tail(args.limit), ensure_ascii=False))
        return 0

    if args.command == "ui-skills-snapshot":
        print(json.dumps([asdict(item) for item in SkillPanelService(runtime).list_skills()], ensure_ascii=False))
        return 0

    if args.command == "ui-skill-run":
        try:
            args_json = json.dumps(parse_skill_kv_args(args.arg), ensure_ascii=False) if args.arg else args.args
        except ValueError as exc:
            print(json.dumps({"executed": False, "reason": str(exc), "result": None}, ensure_ascii=False))
            return 2
        result = SkillPanelService(runtime).run_skill(args.name, args_json, approved=args.approve)
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0 if result.executed else 2

    if args.command == "ui-memory-list":
        print(json.dumps([asdict(item) for item in MemoryPanelService(runtime).list_records(args.status, args.limit)], ensure_ascii=False))
        return 0

    if args.command == "ui-memory-propose":
        result = MemoryPanelService(runtime).propose(args.content, args.type, args.project, args.tags)
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0 if result.ok else 2

    if args.command == "ui-memory-status":
        result = MemoryPanelService(runtime).set_status(args.id, args.status)
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0 if result.ok else 2

    if args.command == "ui-memory-export":
        result = MemoryPanelService(runtime).export_report(args.output, args.status, args.limit, args.format)
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0 if result.ok else 2

    if args.command == "memory-approval-audit":
        audit_path = Path(runtime.config.paths.isis_root) / "logs" / "security" / "memory_approvals.jsonl"
        print(json.dumps(MemoryAuditLogger(audit_path).tail(args.limit), ensure_ascii=False))
        return 0

    if args.command == "audit-report":
        result = AuditReportService(runtime.config.paths.isis_root).build(args.output, args.limit, args.format)
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0

    if args.command == "reports-regenerate":
        result = ReportMaintenanceService(runtime.config.paths.isis_root).regenerate()
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0 if result.signature_ok else 2

    if args.command == "reports-history":
        print(json.dumps(ReportMaintenanceService(runtime.config.paths.isis_root).history(args.limit), ensure_ascii=False))
        return 0

    if args.command == "report-integrity":
        reports_root = Path(runtime.config.paths.isis_root) / "reports"
        manifest = ReportIntegrityService(reports_root).build_manifest(args.output)
        print(json.dumps(asdict(manifest), ensure_ascii=False))
        return 0

    if args.command == "report-integrity-verify":
        reports_root = Path(runtime.config.paths.isis_root) / "reports"
        ok = ReportIntegrityService(reports_root).verify_manifest(args.manifest)
        print(json.dumps({"ok": ok}, ensure_ascii=False))
        return 0 if ok else 2

    if args.command == "signature-key-status":
        key_path = Path(runtime.config.paths.isis_root) / "config" / "report_signing_key.json"
        print(json.dumps(asdict(LocalSignatureService(key_path).status()), ensure_ascii=False))
        return 0

    if args.command == "signature-key-rotate":
        key_path = Path(runtime.config.paths.isis_root) / "config" / "report_signing_key.json"
        print(json.dumps(asdict(LocalSignatureService(key_path).rotate_key()), ensure_ascii=False))
        return 0

    if args.command == "signature-key-acl-status":
        key_path = Path(runtime.config.paths.isis_root) / "config" / "report_signing_key.json"
        print(json.dumps(asdict(KeyAclInspector().inspect(key_path)), ensure_ascii=False))
        return 0

    if args.command == "signature-key-acl-apply":
        key_path = Path(runtime.config.paths.isis_root) / "config" / "report_signing_key.json"
        result = KeyAclManager().apply_restricted(key_path, apply=args.apply)
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0 if result.success else 2

    if args.command == "signature-key-acl-rollback":
        key_path = Path(runtime.config.paths.isis_root) / "config" / "report_signing_key.json"
        result = KeyAclManager().rollback(key_path, args.backup, apply=args.apply)
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0 if result.success else 2

    if args.command == "sign-report":
        key_path = Path(runtime.config.paths.isis_root) / "config" / "report_signing_key.json"
        result = LocalSignatureService(key_path).sign_file(args.file, args.output)
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0

    if args.command == "verify-signature":
        key_path = Path(runtime.config.paths.isis_root) / "config" / "report_signing_key.json"
        ok = LocalSignatureService(key_path).verify_file(args.file, args.signature)
        print(json.dumps({"ok": ok}, ensure_ascii=False))
        return 0 if ok else 2

    if args.command == "auth-status":
        auth = LocalAuthenticator(Path(runtime.config.paths.isis_root) / "config" / "auth.json")
        print(json.dumps(asdict(auth.status()), ensure_ascii=False))
        return 0

    if args.command == "auth-bootstrap":
        auth = LocalAuthenticator(Path(runtime.config.paths.isis_root) / "config" / "auth.json")
        print(json.dumps(asdict(auth.bootstrap_from_env(overwrite=args.overwrite)), ensure_ascii=False))
        return 0

    if args.command == "profile-set":
        auth = LocalAuthenticator(Path(runtime.config.paths.isis_root) / "config" / "auth.json")
        if not auth.verify_env():
            print(json.dumps({"changed": False, "reason": "authentication failed"}, ensure_ascii=False))
            return 2
        runtime.policy.set_profile(PrivilegeProfile(args.profile), authenticated=True)
        runtime.save_config()
        print(json.dumps({"changed": True, "profile": runtime.policy.profile.value}, ensure_ascii=False))
        return 0

    if args.command == "route":
        decision = runtime.router.route(RouteRequest(args.prompt, has_image=args.image, manual_model_id=args.manual_model))
        print(
            json.dumps(
                {
                    "profile": decision.profile.value,
                    "model": decision.model.model_id if decision.model else None,
                    "reason": decision.reason,
                    "fallback_used": decision.fallback_used,
                    "available": decision.available,
                    "resource_reason": decision.resource_reason,
                },
                ensure_ascii=False,
            )
        )
        return 0 if decision.available else 2

    if args.command == "memory-add":
        memory_id = runtime.memory.add(
            MemoryRecord(
                content=args.content,
                type=MemoryType(args.type),
                origin="cli",
                user="local",
                status=MemoryStatus.CONFIRMED if args.confirm else MemoryStatus.PROPOSED,
            )
        )
        print(json.dumps({"id": memory_id}, ensure_ascii=False))
        return 0

    if args.command == "memory-search":
        print(json.dumps(runtime.memory.search_text(args.query), ensure_ascii=False))
        return 0

    if args.command == "memory-embed":
        index = MemoryEmbeddingIndex(
            runtime.root / "data" / "memory" / "memory.sqlite",
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "memory_embeddings.sqlite",
            runtime.audit,
        )
        print(json.dumps(index.index_confirmed(args.limit), ensure_ascii=False))
        return 0

    if args.command == "memory-semantic-search":
        index = MemoryEmbeddingIndex(
            runtime.root / "data" / "memory" / "memory.sqlite",
            Path(runtime.config.paths.isis_root) / "data" / "databases" / "memory_embeddings.sqlite",
            runtime.audit,
        )
        print(json.dumps([asdict(item) for item in index.search(args.query, args.limit)], ensure_ascii=False))
        return 0

    if args.command == "internet-status":
        manager = InternetManager(runtime.config, Path(runtime.config.paths.isis_root))
        print(json.dumps(manager.status(), ensure_ascii=False))
        return 0

    if args.command == "internet-test":
        manager = InternetManager(runtime.config, Path(runtime.config.paths.isis_root))
        print(json.dumps(manager.test_connection(), ensure_ascii=False))
        return 0

    if args.command == "internet-search":
        manager = InternetManager(runtime.config, Path(runtime.config.paths.isis_root))
        result = manager.agent.research(args.query, mode=args.mode, confirmed=args.approve)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result.get("ok") else 2

    if args.command == "internet-cache-clear":
        manager = InternetManager(runtime.config, Path(runtime.config.paths.isis_root))
        print(json.dumps({"removed": manager.agent.cache.clear()}, ensure_ascii=False))
        return 0

    if args.command == "internet-download":
        result = DownloadManager(runtime.config, Path(runtime.config.paths.isis_root)).download(args.url, confirmed=args.approve)
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0 if result.ok else 2

    if args.command == "research-history":
        manager = InternetManager(runtime.config, Path(runtime.config.paths.isis_root))
        print(json.dumps(manager.agent.history.list(args.limit), ensure_ascii=False))
        return 0

    if args.command == "rules-parse":
        parsed = RuleParser().parse(args.text)
        print(json.dumps(asdict(parsed), ensure_ascii=False))
        return 0

    if args.command == "rules-apply":
        service = RuleActivationService(runtime.config, runtime.config_store, Path(runtime.config.paths.isis_root) / "config" / "permissions")
        result = service.apply_text(args.text, confirmed=args.approve)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result.get("ok") else 2

    if args.command == "rules-history":
        service = RuleActivationService(runtime.config, runtime.config_store, Path(runtime.config.paths.isis_root) / "config" / "permissions")
        print(json.dumps(service.history(args.limit), ensure_ascii=False))
        return 0

    if args.command == "permission-simulate":
        engine = PermissionEngine(runtime.config, Path(runtime.config.paths.isis_root) / "config" / "permissions")
        print(json.dumps(engine.simulate(ActionContext(args.action, args.resource, confirmed=args.approve)), ensure_ascii=False))
        return 0

    if args.command == "permission-temp-add":
        engine = PermissionEngine(runtime.config, Path(runtime.config.paths.isis_root) / "config" / "permissions")
        auth = engine.add_temporary(args.action, args.resource, args.minutes, args.max_uses)
        print(json.dumps(asdict(auth), ensure_ascii=False))
        return 0

    if args.command == "permission-summary":
        engine = PermissionEngine(runtime.config, Path(runtime.config.paths.isis_root) / "config" / "permissions")
        print(json.dumps(engine.summary(), ensure_ascii=False))
        return 0

    if args.command == "permission-profiles":
        profiles = PermissionProfileManager(Path(runtime.config.paths.isis_root) / "config" / "permissions").list_profiles()
        print(json.dumps(profiles, ensure_ascii=False))
        return 0

    if args.command == "permission-emergency-block":
        engine = PermissionEngine(runtime.config, Path(runtime.config.paths.isis_root) / "config" / "permissions")
        result = engine.emergency_block_all()
        runtime.config_store.save(runtime.config)
        print(json.dumps(result, ensure_ascii=False))
        return 0

    if args.command == "skills":
        manifests = [runtime.skills.load_manifest(path) for path in runtime.skills.skills_dir.iterdir() if path.is_dir() and (path / "skill.json").exists()]
        payload = [{"name": m.name, "version": m.version, "risk": m.risk_level.value, "enabled": m.enabled} for m in manifests]
        print(json.dumps(payload, ensure_ascii=False) if args.json else "\n".join(item["name"] for item in payload))
        return 0

    if args.command == "skill-run":
        result = runtime.skills.run_in_sandbox(runtime.skills.skills_dir / args.name, json.loads(args.args))
        print(json.dumps(result.__dict__, ensure_ascii=False))
        return result.exit_code

    if args.command == "voice-mock":
        session = VoiceSessionManager(
            MockWakeWordProvider(),
            MockSpeechToTextProvider(args.transcript),
            MockTextToSpeechProvider(runtime.root / "data" / "tmp"),
            AudioInputManager(),
            AudioOutputManager(),
            runtime.audit,
        )
        transcript, response, output = session.run_once(lambda text: f"Recebido: {text}", click_to_talk=True)
        print(json.dumps({"transcript": transcript, "response": response, "audio": str(output) if output else None}, ensure_ascii=False))
        return 0

    if args.command == "voice-core":
        core = IsisAssistantCore(args.root)
        core.initialize()
        result = core.run_voice_once(args.transcript, click_to_talk=True)
        core.shutdown("cli")
        print(json.dumps(result, ensure_ascii=False))
        return 0

    if args.command == "voice-status":
        manager = VoiceManager(runtime.config, runtime.audit)
        status = manager.status()
        piper_binary = Path(runtime.config.voice.piper_binary_path)
        piper_voice = Path(runtime.config.voice.piper_voice_path)
        status["piper_binary_exists"] = piper_binary.exists()
        status["piper_voice_exists"] = piper_voice.exists()
        status["microphone_enabled"] = runtime.config.privacy.microphone_enabled
        status["response_mode"] = runtime.config.voice.response_mode
        print(json.dumps(status, ensure_ascii=False))
        return 0

    if args.command == "voice-speak":
        session = build_voice_session(runtime.config, runtime.audit, transcript=args.text)
        output = session.tts.synthesize(args.text, runtime.config.voice.selected_voice)
        if args.play:
            session.audio_out.enqueue(output)
            session.audio_out.play_next()
        print(json.dumps({"audio_path": str(output), "tts_engine": runtime.config.voice.tts_engine, "played": args.play}, ensure_ascii=False))
        return 0

    if args.command == "voice-test":
        manager = VoiceManager(runtime.config, runtime.audit)
        print(json.dumps(manager.speak(args.text, play=args.play), ensure_ascii=False))
        return 0

    if args.command == "voice-cache-clear":
        cache = AudioCache(Path(runtime.config.paths.cache_dir) / "audio", max_files=runtime.config.voice.audio_cache_max_files)
        print(json.dumps({"removed": cache.clear(), "cache_dir": str(cache.cache_dir)}, ensure_ascii=False))
        return 0

    if args.command == "voice-benchmark":
        manager = VoiceManager(runtime.config, runtime.audit)
        rows = []
        for engine in manager.router.engines:
            info = engine.info()
            row = {"engine": info.name, "voice": info.voice, "available": info.available, "status": "unavailable", "error": info.error}
            if info.available:
                result = manager.router.synthesize("Bom dia, Rodrigo. Estou pronta para ajudar.", emotion="friendly")
                if result:
                    row.update({"status": "ok", "elapsed_ms": result.elapsed_ms, "audio_path": str(result.audio_path), "cached": result.cached})
            rows.append(row)
        logs = Path(runtime.config.paths.logs_dir)
        logs.mkdir(parents=True, exist_ok=True)
        (logs / "voice_benchmark.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        md = ["# Voice benchmark", "", "| Motor | Voz | Disponivel | Status | Tempo ms | Erro |", "|---|---|---:|---|---:|---|"]
        for row in rows:
            md.append(f"| {row.get('engine','')} | {row.get('voice','')} | {row.get('available')} | {row.get('status','')} | {row.get('elapsed_ms','')} | {row.get('error','')} |")
        (logs / "voice_benchmark.md").write_text("\n".join(md), encoding="utf-8")
        print(json.dumps({"rows": rows, "json": str(logs / "voice_benchmark.json"), "markdown": str(logs / "voice_benchmark.md")}, ensure_ascii=False))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
