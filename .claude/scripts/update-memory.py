#!/usr/bin/env python3
"""Auto-update Memory Bank on git commit.

This script is called by Claude Code hooks after successful commits.
It updates timestamps and can extract patterns from new code.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def update_timestamp(file_path: Path) -> None:
    """Update last_updated timestamp in JSON file."""
    if not file_path.exists():
        return

    with open(file_path) as f:
        data = json.load(f)

    data["last_updated"] = datetime.now(timezone.utc).isoformat()

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main() -> int:
    """Update Memory Bank files."""
    memory_dir = Path(__file__).parent.parent / "memory"

    if not memory_dir.exists():
        print("Memory directory not found, skipping update")
        return 0

    files_to_update = [
        memory_dir / "feature-backlog.json",
        memory_dir / "feature-completed.json",
        memory_dir / "decisions.json",
        memory_dir / "test-patterns.json",
    ]

    for file_path in files_to_update:
        if file_path.exists():
            try:
                update_timestamp(file_path)
                print(f"Updated: {file_path.name}")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not update {file_path.name}: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
