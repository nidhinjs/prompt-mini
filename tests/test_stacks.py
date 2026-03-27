"""
tests/test_stacks.py
─────────────────────
Validates that stacks.md entries follow the required schema.
Catches missing fields before they cause forged prompts to be incomplete.

Run from repo root:
    python3 -m pytest tests/test_stacks.py -v

What this tests:
  - stacks.md is parseable
  - Each framework entry has the required schema fields
  - No entry is empty
  - use-cases tags are from the approved list
  - Minimum framework coverage is met
"""

import re
from pathlib import Path

STACKS = Path(__file__).parent.parent / "skills" / "prompt-mini" / "references" / "stacks.md"

REQUIRED_FIELDS = ["use-cases", "detect", "prompt-context", "pitfalls", "scope-anchors", "stop-conditions"]

VALID_USE_CASES = {
    "webapp", "saas", "mobile", "desktop", "extension", "backend",
    "ai-app", "database", "auth", "deploy", "cross-platform",
    "ios", "android", "legacy", "fullstack", "edge", "cli",
    "browser-extension", "chrome-extension", "vscode-extension",
    "enterprise", "landing-page", "blog", "docs", "spa", "dashboard",
}

MINIMUM_FRAMEWORKS = [
    "Next.js App Router",
    "React Native",
    "Chrome MV3",
    "FastAPI",
    "Supabase",
    "Prisma",
    "Tailwind",
    "Vercel AI SDK",
    "Tauri",
    "Electron",
]


def parse_framework_entries(content: str) -> dict[str, str]:
    """Parse stacks.md into {framework_name: section_content} dict."""
    entries = {}
    # Match ### headings as framework entry starts
    parts = re.split(r"^### (.+)$", content, flags=re.MULTILINE)
    # parts[0] = preamble, then alternating [name, content, name, content...]
    it = iter(parts[1:])
    for name, body in zip(it, it):
        entries[name.strip()] = body.strip()
    return entries


class TestStacksMd:
    def setup_method(self):
        self.content = STACKS.read_text(encoding="utf-8")
        self.entries = parse_framework_entries(self.content)

    def test_file_is_readable(self):
        assert len(self.content) > 1000

    def test_has_table_of_contents(self):
        assert "Table of Contents" in self.content

    def test_minimum_framework_count(self):
        assert len(self.entries) >= 20, (
            f"Expected at least 20 framework entries, found {len(self.entries)}"
        )

    def test_minimum_required_frameworks_present(self):
        for framework in MINIMUM_FRAMEWORKS:
            found = any(framework.lower() in name.lower() for name in self.entries)
            assert found, f"Required framework '{framework}' not found in stacks.md"

    def test_each_entry_has_required_fields(self):
        missing = {}
        for name, body in self.entries.items():
            entry_missing = [f for f in REQUIRED_FIELDS if f not in body]
            if entry_missing:
                missing[name] = entry_missing
        assert not missing, (
            f"Entries missing required fields:\n" +
            "\n".join(f"  {k}: missing {v}" for k, v in missing.items())
        )

    def test_each_entry_has_nonempty_body(self):
        short = {n: len(b) for n, b in self.entries.items() if len(b) < 50}
        assert not short, f"These entries have suspiciously short bodies: {short}"

    def test_use_cases_are_from_approved_list(self):
        invalid = {}
        for name, body in self.entries.items():
            match = re.search(r"use-cases:\s*(.+)", body)
            if not match:
                continue
            tags = [t.strip() for t in match.group(1).split(",")]
            bad_tags = [t for t in tags if t not in VALID_USE_CASES]
            if bad_tags:
                invalid[name] = bad_tags
        assert not invalid, (
            f"Invalid use-case tags found:\n" +
            "\n".join(f"  {k}: {v}" for k, v in invalid.items())
        )

    def test_stop_conditions_are_specific(self):
        """Stop conditions must not be vague — check for 'be careful' anti-pattern."""
        vague = []
        for name, body in self.entries.items():
            if "be careful" in body.lower() or "use caution" in body.lower():
                vague.append(name)
        assert not vague, f"These entries have vague stop conditions: {vague}"

    def test_scope_anchors_look_like_paths(self):
        """Scope anchors should contain / characters indicating real file paths."""
        no_paths = []
        for name, body in self.entries.items():
            match = re.search(r"scope-anchors:\s*(.+)", body)
            if match and "/" not in match.group(1):
                no_paths.append(name)
        assert not no_paths, (
            f"These entries have scope-anchors without file paths: {no_paths}"
        )
