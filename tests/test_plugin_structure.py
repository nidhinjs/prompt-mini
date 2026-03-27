"""
tests/test_plugin_structure.py
───────────────────────────────
Validates that the plugin structure matches Claude Code's official spec.
No Claude Code needed — runs pure Python against the file system.

Run from repo root:
    python3 -m pytest tests/test_plugin_structure.py -v

What this tests:
  - Required files exist in the right locations
  - plugin.json has all required fields and correct types
  - hooks.json uses the correct nested schema
  - marketplace.json points to the right source path
  - SKILL.md has valid frontmatter with required fields
  - SKILL.md is under 500 lines
  - Description is under 200 characters
  - Reference files exist and are non-empty
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent


# ── Plugin manifest ───────────────────────────────────────────────────────────

class TestPluginJson:
    def setup_method(self):
        self.path = ROOT / ".claude-plugin" / "plugin.json"
        self.data = json.loads(self.path.read_text())

    def test_file_exists(self):
        assert self.path.exists()

    def test_required_field_name(self):
        assert "name" in self.data
        assert isinstance(self.data["name"], str)
        assert len(self.data["name"]) > 0

    def test_required_field_description(self):
        assert "description" in self.data
        assert isinstance(self.data["description"], str)

    def test_required_field_version(self):
        assert "version" in self.data
        assert re.match(r"^\d+\.\d+\.\d+$", self.data["version"]), "version must be semver"

    def test_required_field_author(self):
        assert "author" in self.data
        assert "name" in self.data["author"]

    def test_required_field_license(self):
        assert "license" in self.data

    def test_no_extra_plugin_directories_inside_claude_plugin(self):
        """Only plugin.json should be inside .claude-plugin/ per official spec."""
        claude_plugin_dir = ROOT / ".claude-plugin"
        contents = list(claude_plugin_dir.iterdir())
        assert len(contents) == 1, (
            f".claude-plugin/ should only contain plugin.json — found: {[f.name for f in contents]}"
        )


# ── Hooks config ──────────────────────────────────────────────────────────────

class TestHooksJson:
    def setup_method(self):
        self.path = ROOT / "hooks" / "hooks.json"
        self.data = json.loads(self.path.read_text())

    def test_file_exists(self):
        assert self.path.exists()

    def test_top_level_hooks_key(self):
        assert "hooks" in self.data, "hooks.json must have top-level 'hooks' key"

    def test_user_prompt_submit_event_exists(self):
        assert "UserPromptSubmit" in self.data["hooks"]

    def test_nested_hooks_structure(self):
        """Official schema: hooks.UserPromptSubmit is a list of objects each with a hooks list."""
        event_hooks = self.data["hooks"]["UserPromptSubmit"]
        assert isinstance(event_hooks, list)
        assert len(event_hooks) > 0
        for item in event_hooks:
            assert "hooks" in item, "Each event entry must have a 'hooks' list"
            assert isinstance(item["hooks"], list)

    def test_hook_type_is_command(self):
        inner_hooks = self.data["hooks"]["UserPromptSubmit"][0]["hooks"]
        for hook in inner_hooks:
            assert hook.get("type") == "command"

    def test_command_references_script(self):
        inner_hooks = self.data["hooks"]["UserPromptSubmit"][0]["hooks"]
        for hook in inner_hooks:
            assert "evaluate-prompt.py" in hook.get("command", "")

    def test_command_has_python_fallback(self):
        """Windows compatibility — command should have || python fallback."""
        inner_hooks = self.data["hooks"]["UserPromptSubmit"][0]["hooks"]
        for hook in inner_hooks:
            cmd = hook.get("command", "")
            assert "python3" in cmd and "python" in cmd, (
                "Command should have 'python3 ... || python ...' for Windows compatibility"
            )


# ── Dev marketplace ───────────────────────────────────────────────────────────

class TestMarketplaceJson:
    def setup_method(self):
        self.path = ROOT / ".dev-marketplace" / ".claude-plugin" / "marketplace.json"
        self.data = json.loads(self.path.read_text())

    def test_file_exists(self):
        assert self.path.exists()

    def test_has_name(self):
        assert "name" in self.data

    def test_has_owner(self):
        assert "owner" in self.data
        assert "name" in self.data["owner"]

    def test_has_plugins_list(self):
        assert "plugins" in self.data
        assert isinstance(self.data["plugins"], list)
        assert len(self.data["plugins"]) > 0

    def test_plugin_has_source(self):
        for plugin in self.data["plugins"]:
            assert "source" in plugin

    def test_source_resolves_to_repo_root(self):
        """./../../ from .dev-marketplace/.claude-plugin/ should resolve to repo root."""
        source = self.data["plugins"][0]["source"]
        resolved = (self.path.parent / source).resolve()
        assert resolved == ROOT.resolve()


# ── SKILL.md structure ────────────────────────────────────────────────────────

class TestSkillMd:
    def setup_method(self):
        self.path = ROOT / "skills" / "prompt-mini" / "SKILL.md"
        self.content = self.path.read_text()
        self.lines = self.content.splitlines()

    def test_file_exists(self):
        assert self.path.exists()

    def test_has_frontmatter(self):
        assert self.content.startswith("---"), "SKILL.md must start with --- frontmatter"

    def test_frontmatter_has_name(self):
        assert re.search(r"^name:\s+\S+", self.content, re.MULTILINE)

    def test_frontmatter_has_description(self):
        assert re.search(r"^description:\s+\S+", self.content, re.MULTILINE)

    def test_description_under_200_chars(self):
        match = re.search(r"^description:\s+(.+)$", self.content, re.MULTILINE)
        assert match, "No description found in frontmatter"
        desc = match.group(1).strip()
        assert len(desc) <= 200, f"Description is {len(desc)} chars — must be ≤200"

    def test_under_500_lines(self):
        assert len(self.lines) <= 500, (
            f"SKILL.md is {len(self.lines)} lines — must be ≤500 per official spec"
        )

    def test_has_primacy_zone(self):
        assert "PRIMACY ZONE" in self.content

    def test_has_recency_zone(self):
        assert "RECENCY ZONE" in self.content

    def test_has_reference_files_table(self):
        assert "references/stacks.md" in self.content
        assert "references/templates.md" in self.content

    def test_never_rules_present(self):
        assert "NEVER" in self.content


# ── Reference files ───────────────────────────────────────────────────────────

class TestReferenceFiles:
    def setup_method(self):
        self.refs = ROOT / "skills" / "prompt-mini" / "references"

    def test_references_folder_exists(self):
        assert self.refs.exists() and self.refs.is_dir()

    def test_stacks_md_exists_and_nonempty(self):
        f = self.refs / "stacks.md"
        assert f.exists()
        assert len(f.read_text().strip()) > 100

    def test_question_patterns_md_exists(self):
        assert (self.refs / "question-patterns.md").exists()

    def test_templates_md_exists(self):
        assert (self.refs / "templates.md").exists()

    def test_patterns_md_exists(self):
        assert (self.refs / "patterns.md").exists()

    def test_no_old_files_remain(self):
        """prompt-template.md and intent-signals.md were deleted — confirm gone."""
        assert not (self.refs / "prompt-template.md").exists(), (
            "prompt-template.md should be deleted — content moved to templates.md"
        )
        assert not (self.refs / "intent-signals.md").exists(), (
            "intent-signals.md should be deleted — content folded into SKILL.md"
        )


# ── Evaluate-prompt.py ────────────────────────────────────────────────────────

class TestEvaluatePromptScript:
    def setup_method(self):
        self.path = ROOT / "scripts" / "evaluate-prompt.py"
        self.content = self.path.read_text()

    def test_file_exists(self):
        assert self.path.exists()

    def test_has_shebang(self):
        assert self.content.startswith("#!/usr/bin/env python3")

    def test_uses_correct_output_format(self):
        assert "hookSpecificOutput" in self.content
        assert "hookEventName" in self.content
        assert "additionalContext" in self.content

    def test_has_bypass_prefixes(self):
        assert '"*"' in self.content or "'*'" in self.content

    def test_has_vague_signals(self):
        assert "VAGUE" in self.content

    def test_has_clear_signals(self):
        assert "CLEAR" in self.content

    def test_never_uses_system_message(self):
        """systemMessage is not a valid field in the official spec."""
        assert "systemMessage" not in self.content
