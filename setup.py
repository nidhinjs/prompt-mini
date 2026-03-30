#!/usr/bin/env python3
"""
setup.py — Install the prompt-mini UserPromptSubmit hook into ~/.claude/settings.json

Run once after cloning:
    python setup.py

Uses the current Python executable — works on Windows, macOS, and Linux.
Safe to run multiple times — idempotent.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.resolve()
SCRIPT = REPO_ROOT / "scripts" / "evaluate-prompt.py"
SETTINGS = Path.home() / ".claude" / "settings.json"


def main():
    if SETTINGS.exists():
        # utf-8-sig strips the BOM that Windows tools (Notepad, some editors) write
        with open(SETTINGS, encoding="utf-8-sig") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = {}
    else:
        settings = {}
        SETTINGS.parent.mkdir(parents=True, exist_ok=True)

    python_exe = sys.executable
    script_path = str(SCRIPT)
    command = f'"{python_exe}" "{script_path}"'

    new_entry = {
        "hooks": [
            {
                "type": "command",
                "command": command,
                "description": "prompt-mini -- forges vague prompts before execution"
            }
        ]
    }

    settings.setdefault("hooks", {}).setdefault("UserPromptSubmit", [])

    # Remove any existing prompt-mini entries (idempotent)
    settings["hooks"]["UserPromptSubmit"] = [
        entry for entry in settings["hooks"]["UserPromptSubmit"]
        if not any(
            "evaluate-prompt" in hook.get("command", "")
            or "prompt-mini.py" in hook.get("command", "")
            or "prompt-mini" in hook.get("command", "")
            for hook in entry.get("hooks", [])
        )
    ]

    settings["hooks"]["UserPromptSubmit"].append(new_entry)

    with open(SETTINGS, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

    print(f"[OK] Hook registered in {SETTINGS}")
    print(f"     Python : {python_exe}")
    print(f"     Script : {script_path}")
    print()
    print("Restart Claude Code for the hook to take effect.")
    print()
    print("To verify: open Claude Code, type /hooks, click UserPromptSubmit")
    print("You should see: prompt-mini -- forges vague prompts before execution")


if __name__ == "__main__":
    main()
