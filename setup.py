#!/usr/bin/env python3
"""
prompt-mini setup — registers the UserPromptSubmit hook in ~/.claude/settings.json
Run once after installing the plugin:
    python3 setup.py
"""
import json
import os
import sys
import shutil
from pathlib import Path

HOOK_NAME = "prompt-mini"
SCRIPT_NAME = "prompt-mini.py"
CLAUDE_DIR = Path.home() / ".claude"
HOOKS_DIR = CLAUDE_DIR / "hooks"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"
SOURCE_SCRIPT = Path(__file__).parent / "scripts" / "evaluate-prompt.py"
DEST_SCRIPT = HOOKS_DIR / SCRIPT_NAME


def main():
    print("prompt-mini setup")
    print("-" * 40)

    # Step 1 — Copy hook script to ~/.claude/hooks/
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_SCRIPT, DEST_SCRIPT)
    print(f"✓ Copied hook script to {DEST_SCRIPT}")

    # Step 2 — Load or create settings.json
    if SETTINGS_FILE.exists():
        try:
            settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            settings = {}
    else:
        settings = {}

    # Step 3 — Build the hook entry
    python_cmd = "python3" if shutil.which("python3") else "python"
    hook_command = f'{python_cmd} "{DEST_SCRIPT}"'

    hook_entry = {
        "hooks": [
            {
                "type": "command",
                "command": hook_command,
                "description": "prompt-mini — forges vague prompts before execution"
            }
        ]
    }

    # Step 4 — Add to UserPromptSubmit, avoid duplicates
    hooks = settings.setdefault("hooks", {})
    existing = hooks.setdefault("UserPromptSubmit", [])

    # Remove any old prompt-mini entry
    existing[:] = [
        h for h in existing
        if not any(HOOK_NAME in str(hook.get("command", "")) for hook in h.get("hooks", []))
    ]

    existing.append(hook_entry)
    settings["hooks"]["UserPromptSubmit"] = existing

    # Step 5 — Write settings.json
    SETTINGS_FILE.write_text(
        json.dumps(settings, indent=2),
        encoding="utf-8"
    )
    print(f"✓ Registered hook in {SETTINGS_FILE}")
    print()
    print("✅ Done. Restart Claude Code for the hook to take effect.")
    print()
    print("To verify: open Claude Code, type /hooks, click UserPromptSubmit")
    print("You should see: prompt-mini — forges vague prompts before execution")


if __name__ == "__main__":
    main()
