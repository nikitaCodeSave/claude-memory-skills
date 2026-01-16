#!/usr/bin/env python3
"""
Скрипт синхронизации Memory Bank для Claude Code

Команды:
    --load              Загрузить snapshot в контекст (для SessionStart)
    --save              Сохранить прогресс и обновить snapshot (для PreCompact/SessionEnd)
    --checkpoint        Лёгкое сохранение timestamp (для Stop hook)
    --init              Инициализировать структуру memory bank
    --status            Вывести статус памяти
    --archive           Архивировать текущий progress и начать новый
    --refresh-snapshot-if-needed FILE
                        Обновить snapshot если FILE в memory-bank/ (для PostToolUse)

Параметры:
    --session-id ID     ID сессии для отслеживания
    --reason REASON     Причина сохранения (precompact/sessionend/manual)
"""

import json
import os
import sys
import argparse
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Конфигурация
MEMORY_BANK_DIR = "memory-bank"
ARCHIVE_DIR = "memory-bank/archive"

# Файлы по уровням
TIER1_FILES = ["projectbrief.md", "techContext.md", "systemPatterns.md"]
TIER1_5_FILES = ["decisions.md"]
TIER2_FILES = ["activeContext.md", "backlog.json"]
TIER3_FILES = ["progress.json"]
SNAPSHOT_FILE = "snapshot.md"


def get_project_dir() -> Path:
    """Получить директорию проекта."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def get_memory_dir() -> Path:
    """Получить директорию memory bank."""
    return get_project_dir() / MEMORY_BANK_DIR


def load_json(filepath: Path) -> Optional[Dict]:
    """Загрузить JSON файл."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_json(filepath: Path, data: Dict) -> bool:
    """Сохранить JSON файл."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return False


def read_md(filepath: Path) -> Optional[str]:
    """Прочитать markdown файл."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None


def write_md(filepath: Path, content: str) -> bool:
    """Записать markdown файл."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False


def extract_section(content: str, header: str) -> str:
    """Извлечь секцию из markdown по заголовку."""
    if not content or header not in content:
        return ""
    start = content.find(header)
    # Найти следующий заголовок того же или выше уровня
    level = len(header) - len(header.lstrip('#'))
    end = len(content)
    for i, line in enumerate(content[start+len(header):].split('\n')[1:], 1):
        if line.startswith('#'):
            line_level = len(line) - len(line.lstrip('#'))
            if line_level <= level:
                end = start + len(header) + sum(len(l)+1 for l in content[start+len(header):].split('\n')[:i])
                break
    return content[start:end].strip()


def generate_snapshot(memory_dir: Path) -> str:
    """Генерировать оптимизированный snapshot для контекста."""
    now = datetime.now().isoformat()
    
    # Извлекаем данные из Tier1
    project_name = "Не инициализировано"
    tech_stack = "Не определён"
    
    brief = read_md(memory_dir / "projectbrief.md")
    if brief:
        for line in brief.split('\n'):
            if "**Название проекта**:" in line:
                project_name = line.split(":", 1)[1].strip() or project_name
                break
    
    tech = read_md(memory_dir / "techContext.md")
    if tech:
        for line in tech.split('\n'):
            if "- Основной:" in line:
                tech_stack = line.split(":", 1)[1].strip() or tech_stack
                break
    
    # Извлекаем данные из Tier2
    sprint = "—"
    goal = "—"
    active_tasks = []
    blockers = []
    
    active = read_md(memory_dir / "activeContext.md")
    if active:
        for line in active.split('\n'):
            if "**Спринт/Итерация**:" in line:
                val = line.split(":", 1)[1].strip()
                if val and not val.startswith("["):
                    sprint = val
            elif "**Цель**:" in line:
                val = line.split(":", 1)[1].strip()
                if val and not val.startswith("["):
                    goal = val
    
    backlog = load_json(memory_dir / "backlog.json")
    if backlog and backlog.get("items"):
        for item in backlog["items"]:
            if item.get("status") == "in-progress":
                active_tasks.append(f"- [{item.get('id', '?')}] {item.get('title', '?')}")
            if item.get("status") == "blocked":
                blockers.append(f"- [{item.get('id', '?')}] {item.get('title', '?')}")
    
    # Извлекаем данные из Tier3
    last_session = "—"
    completed = "—"
    next_steps = "—"
    
    progress = load_json(memory_dir / "progress.json")
    if progress:
        session = progress.get("session", {})
        if session.get("lastActivity"):
            last_session = session["lastActivity"][:10]  # Только дата
        
        completed_list = progress.get("completedInSession", [])
        if completed_list:
            completed = ", ".join(completed_list[:3])
            if len(completed_list) > 3:
                completed += f" (+{len(completed_list)-3})"
        
        steps = progress.get("nextSteps", [])
        if steps:
            next_steps = "; ".join(steps[:3])
    
    # Формируем snapshot
    active_tasks_str = "\n".join(active_tasks) if active_tasks else "_Нет активных задач_"
    blockers_str = "\n".join(blockers) if blockers else "_Нет блокеров_"
    
    snapshot = f"""# Memory Snapshot
<!-- Автогенерируемый файл. Не редактировать вручную. -->

## Проект
**Название**: {project_name}
**Стек**: {tech_stack}

## Текущий фокус
- **Спринт**: {sprint}
- **Цель**: {goal}

## Активные задачи
{active_tasks_str}

## Последняя сессия
- **Дата**: {last_session}
- **Сделано**: {completed}
- **Следующие шаги**: {next_steps}

## Блокеры
{blockers_str}

---
*Сгенерировано: {now}*
"""
    return snapshot


def cmd_load(session_id: Optional[str] = None) -> None:
    """Загрузить snapshot и вывести для инъекции в контекст."""
    memory_dir = get_memory_dir()
    
    # Генерируем свежий snapshot
    snapshot = generate_snapshot(memory_dir)
    
    # Сохраняем snapshot на диск
    write_md(memory_dir / SNAPSHOT_FILE, snapshot)
    
    # Обновляем session id если передан
    if session_id:
        progress_file = memory_dir / "progress.json"
        progress = load_json(progress_file) or {"version": "1.0.0", "session": {}}
        progress["session"]["id"] = session_id
        progress["session"]["startedAt"] = datetime.now().isoformat()
        save_json(progress_file, progress)
    
    # Выводим для hookSpecificOutput
    # Берём только ключевую информацию для additionalContext
    lines = snapshot.split('\n')
    brief_snapshot = '\n'.join([l for l in lines if l.strip() and not l.startswith('<!--') and not l.startswith('*') and not l.startswith('---')][:15])
    
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"=== MEMORY BANK SNAPSHOT ===\n{brief_snapshot}\n=== END SNAPSHOT ==="
        }
    }
    print(json.dumps(output, ensure_ascii=False))


def cmd_save(session_id: Optional[str] = None, reason: str = "manual") -> None:
    """Сохранить прогресс и обновить snapshot."""
    memory_dir = get_memory_dir()
    now = datetime.now().isoformat()
    
    # Обновляем progress.json
    progress_file = memory_dir / "progress.json"
    progress = load_json(progress_file) or {
        "version": "1.0.0",
        "session": {},
        "track": {},
        "currentTask": {},
        "completedInSession": [],
        "workLog": [],
        "insights": [],
        "nextSteps": [],
        "handoffNotes": ""
    }
    
    progress["session"]["lastActivity"] = now
    if session_id:
        progress["session"]["id"] = session_id
    
    # Добавляем запись в workLog
    progress["workLog"].append({
        "timestamp": now,
        "action": f"auto-save ({reason})",
        "details": f"Автосохранение по событию: {reason}",
        "outcome": "saved"
    })
    
    # Ограничиваем workLog последними 20 записями
    if len(progress["workLog"]) > 20:
        progress["workLog"] = progress["workLog"][-20:]
    
    save_json(progress_file, progress)
    
    # Регенерируем snapshot
    snapshot = generate_snapshot(memory_dir)
    write_md(memory_dir / SNAPSHOT_FILE, snapshot)
    
    print(json.dumps({
        "saved": True,
        "reason": reason,
        "timestamp": now,
        "snapshot_updated": True
    }))


def cmd_checkpoint() -> None:
    """Лёгкое сохранение - только timestamp (для Stop hook)."""
    memory_dir = get_memory_dir()
    progress_file = memory_dir / "progress.json"
    
    progress = load_json(progress_file)
    if progress:
        progress["session"]["lastActivity"] = datetime.now().isoformat()
        save_json(progress_file, progress)
    
    # Тихий вывод для Stop hook
    print(json.dumps({"checkpoint": True, "suppressOutput": True}))


def cmd_archive() -> None:
    """Архивировать текущий progress и начать новый."""
    memory_dir = get_memory_dir()
    archive_dir = get_project_dir() / ARCHIVE_DIR
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    progress_file = memory_dir / "progress.json"
    progress = load_json(progress_file)
    
    if progress:
        # Архивируем с датой
        date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
        archive_file = archive_dir / f"progress-{date_str}.json"
        shutil.copy(progress_file, archive_file)
        
        # Создаём новый чистый progress
        new_progress = {
            "version": "1.0.0",
            "session": {"startedAt": datetime.now().isoformat()},
            "track": {},
            "currentTask": {},
            "completedInSession": [],
            "workLog": [],
            "insights": [],
            "nextSteps": [],
            "handoffNotes": ""
        }
        save_json(progress_file, new_progress)
        
        print(json.dumps({
            "archived": True,
            "archive_file": str(archive_file),
            "new_progress_created": True
        }, ensure_ascii=False))
    else:
        print(json.dumps({"archived": False, "error": "progress.json не найден"}))


def cmd_refresh_if_needed(file_path: str) -> None:
    """Обновить snapshot если изменён файл memory-bank (для PostToolUse hook)."""
    if not file_path:
        print(json.dumps({"skipped": True, "reason": "no file path provided"}))
        return

    # Проверяем, относится ли файл к memory-bank
    if "memory-bank" not in file_path:
        print(json.dumps({"skipped": True, "reason": "not memory-bank file"}))
        return

    # Не обновляем snapshot при изменении самого snapshot
    if file_path.endswith("snapshot.md"):
        print(json.dumps({"skipped": True, "reason": "snapshot file itself"}))
        return

    # Валидация JSON если нужно
    if file_path.endswith('.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            print("✅ JSON valid")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return
        except FileNotFoundError:
            print(json.dumps({"skipped": True, "reason": "file not found"}))
            return

    # Регенерация snapshot
    memory_dir = get_memory_dir()
    snapshot = generate_snapshot(memory_dir)
    write_md(memory_dir / SNAPSHOT_FILE, snapshot)
    print(json.dumps({"snapshot_updated": True, "trigger": file_path}))


def cmd_init() -> None:
    """Инициализировать структуру memory bank."""
    memory_dir = get_memory_dir()
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаём archive директорию
    (get_project_dir() / ARCHIVE_DIR).mkdir(parents=True, exist_ok=True)
    
    created = []
    skipped = []
    
    all_files = TIER1_FILES + TIER1_5_FILES + TIER2_FILES + TIER3_FILES + [SNAPSHOT_FILE]
    
    for filename in all_files:
        filepath = memory_dir / filename
        if filepath.exists():
            skipped.append(filename)
        else:
            if filename.endswith('.json'):
                if "backlog" in filename:
                    save_json(filepath, {
                        "version": "1.0.0",
                        "lastUpdated": datetime.now().isoformat(),
                        "items": []
                    })
                elif "progress" in filename:
                    save_json(filepath, {
                        "version": "1.0.0",
                        "session": {"startedAt": datetime.now().isoformat()},
                        "currentTask": {},
                        "completedInSession": [],
                        "workLog": [],
                        "insights": [],
                        "nextSteps": []
                    })
            else:
                write_md(filepath, f"# {filename.replace('.md', '').replace('-', ' ').title()}\n\n<!-- Заполни эту секцию -->\n")
            created.append(filename)
    
    # Генерируем начальный snapshot
    snapshot = generate_snapshot(memory_dir)
    write_md(memory_dir / SNAPSHOT_FILE, snapshot)
    
    print(json.dumps({
        "initialized": True,
        "memory_dir": str(memory_dir),
        "created": created,
        "skipped": skipped
    }, indent=2, ensure_ascii=False))


def cmd_status() -> None:
    """Вывести статус memory bank."""
    memory_dir = get_memory_dir()
    
    def estimate_tokens(text: str) -> int:
        return len(text) // 4
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "memory_dir": str(memory_dir),
        "tiers": {
            "tier1": {"files": [], "tokens": 0},
            "tier1_5": {"files": [], "tokens": 0},
            "tier2": {"files": [], "tokens": 0},
            "tier3": {"files": [], "tokens": 0}
        },
        "snapshot": {"exists": False, "tokens": 0},
        "total_tokens": 0
    }
    
    # Tier 1
    for f in TIER1_FILES:
        content = read_md(memory_dir / f)
        if content:
            tokens = estimate_tokens(content)
            status["tiers"]["tier1"]["files"].append({"name": f, "tokens": tokens})
            status["tiers"]["tier1"]["tokens"] += tokens
    
    # Tier 1.5
    for f in TIER1_5_FILES:
        content = read_md(memory_dir / f)
        if content:
            tokens = estimate_tokens(content)
            status["tiers"]["tier1_5"]["files"].append({"name": f, "tokens": tokens})
            status["tiers"]["tier1_5"]["tokens"] += tokens
    
    # Tier 2
    for f in TIER2_FILES:
        filepath = memory_dir / f
        if f.endswith('.json'):
            data = load_json(filepath)
            if data:
                tokens = estimate_tokens(json.dumps(data))
                status["tiers"]["tier2"]["files"].append({"name": f, "tokens": tokens})
                status["tiers"]["tier2"]["tokens"] += tokens
        else:
            content = read_md(filepath)
            if content:
                tokens = estimate_tokens(content)
                status["tiers"]["tier2"]["files"].append({"name": f, "tokens": tokens})
                status["tiers"]["tier2"]["tokens"] += tokens
    
    # Tier 3
    for f in TIER3_FILES:
        data = load_json(memory_dir / f)
        if data:
            tokens = estimate_tokens(json.dumps(data))
            status["tiers"]["tier3"]["files"].append({"name": f, "tokens": tokens})
            status["tiers"]["tier3"]["tokens"] += tokens
    
    # Snapshot
    snapshot_content = read_md(memory_dir / SNAPSHOT_FILE)
    if snapshot_content:
        status["snapshot"]["exists"] = True
        status["snapshot"]["tokens"] = estimate_tokens(snapshot_content)
    
    # Total
    status["total_tokens"] = sum(t["tokens"] for t in status["tiers"].values()) + status["snapshot"]["tokens"]
    
    # Budgets check
    budgets = {
        "tier1": 15000,
        "tier1_5": 5000,
        "tier2": 20000,
        "tier3": 10000
    }
    
    status["budget_warnings"] = []
    for tier, budget in budgets.items():
        used = status["tiers"][tier]["tokens"]
        if used > budget * 0.8:
            status["budget_warnings"].append(f"{tier}: {used}/{budget} токенов (>{80}%)")
    
    print(json.dumps(status, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Memory Bank Sync для Claude Code")
    parser.add_argument("--load", action="store_true", help="Загрузить snapshot в контекст")
    parser.add_argument("--save", action="store_true", help="Сохранить прогресс и обновить snapshot")
    parser.add_argument("--checkpoint", action="store_true", help="Лёгкое сохранение timestamp")
    parser.add_argument("--init", action="store_true", help="Инициализировать memory bank")
    parser.add_argument("--status", action="store_true", help="Показать статус")
    parser.add_argument("--archive", action="store_true", help="Архивировать progress и начать новый")
    parser.add_argument("--refresh-snapshot-if-needed", type=str, metavar="FILE",
                        help="Обновить snapshot если FILE в memory-bank/")
    parser.add_argument("--session-id", type=str, help="ID сессии")
    parser.add_argument("--reason", type=str, default="manual", help="Причина сохранения")

    args = parser.parse_args()

    if args.load:
        cmd_load(args.session_id)
    elif args.save:
        cmd_save(args.session_id, args.reason)
    elif args.checkpoint:
        cmd_checkpoint()
    elif args.init:
        cmd_init()
    elif args.status:
        cmd_status()
    elif args.archive:
        cmd_archive()
    elif args.refresh_snapshot_if_needed:
        cmd_refresh_if_needed(args.refresh_snapshot_if_needed)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
