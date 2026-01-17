#!/usr/bin/env python3
"""
Memory Bank v2 Hook
Handles SessionStart (load context) and Stop (checkpoint)
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path


def get_project_dir():
    """Get project directory from env or current dir."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def get_memory_path():
    """Get path to memory.json."""
    return get_project_dir() / "memory-bank" / "memory.json"


def load_memory():
    """Load memory.json or return empty structure."""
    path = get_memory_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None


def format_context(memory):
    """Format memory for Claude context."""
    if not memory:
        return "Memory Bank: не инициализирован. Используй /memory для просмотра."

    lines = ["=== MEMORY BANK ==="]

    # Meta
    meta = memory.get("meta", {})
    if meta.get("project"):
        lines.append(f"Проект: {meta['project']}")

    # Focus
    focus = memory.get("focus")
    if focus:
        lines.append(f"Фокус: {focus}")

    # Recent log entries (last 10)
    log = memory.get("log", [])
    if log:
        lines.append("")
        lines.append("Последние записи:")
        for entry in log[-10:]:
            type_emoji = {
                "task": "✓",
                "decision": "→",
                "bug": "✗",
                "note": "•"
            }.get(entry.get("type", "note"), "•")
            text = entry.get("text", "")
            date = entry.get("date", "")
            lines.append(f"  {type_emoji} [{date}] {text}")
            if entry.get("reason"):
                lines.append(f"      Причина: {entry['reason']}")

    lines.append("=== END MEMORY ===")
    return "\n".join(lines)


def handle_session_start(input_data):
    """Handle SessionStart hook - load memory into context."""
    memory = load_memory()
    context = format_context(memory)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context
        }
    }
    print(json.dumps(output))
    return 0


def handle_stop(input_data):
    """Handle Stop hook - simple checkpoint, no blocking."""
    # Update lastSession timestamp
    memory = load_memory()
    if memory:
        memory["meta"]["lastSession"] = datetime.now().strftime("%Y-%m-%d")
        try:
            with open(get_memory_path(), "w", encoding="utf-8") as f:
                json.dump(memory, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    # Don't block, just exit successfully
    return 0


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    hook_event = input_data.get("hook_event_name", "")

    if hook_event == "SessionStart":
        return handle_session_start(input_data)
    elif hook_event == "Stop":
        return handle_stop(input_data)
    else:
        # Unknown hook, just pass through
        return 0


if __name__ == "__main__":
    sys.exit(main())
