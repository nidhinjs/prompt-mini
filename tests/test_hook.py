"""
tests/test_hook.py
──────────────────
Unit tests for evaluate-prompt.py — the UserPromptSubmit hook gate.

Run from repo root:
    python3 -m pytest tests/test_hook.py -v

What this tests:
  - Bypass prefixes (* / #) always pass through
  - Short/empty prompts always pass through
  - Clear prompts (file paths, specific functions) pass through
  - Vague prompts (framework names, no scope) trigger the skill
  - Output JSON structure is always valid
  - Script never crashes — even on malformed input
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "evaluate-prompt.py"


def run_hook(prompt: str) -> dict:
    """Run the hook script with a prompt, return parsed output."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps({"prompt": prompt}),
        capture_output=True,
        text=True,
    )
    # Script may exit silently with no output on bypass
    if not result.stdout.strip():
        return {}
    return json.loads(result.stdout.strip())


def is_triggered(output: dict) -> bool:
    """Return True if the skill was triggered (evaluation wrapper injected)."""
    ctx = output.get("hookSpecificOutput", {}).get("additionalContext", "")
    return "prompt-mini" in ctx or "EVALUATION" in ctx


# ── Bypass tests ──────────────────────────────────────────────────────────────

class TestBypass:
    def test_star_prefix_bypasses(self):
        out = run_hook("* just run this as-is: fix everything")
        assert not is_triggered(out)

    def test_slash_command_bypasses(self):
        out = run_hook("/help")
        assert not is_triggered(out)

    def test_hash_prefix_bypasses(self):
        out = run_hook("#remember my stack is Next.js")
        assert not is_triggered(out)

    def test_star_with_framework_still_bypasses(self):
        """Even vague content after * must bypass — user explicitly opted out."""
        out = run_hook("* build me a nextjs supabase app")
        assert not is_triggered(out)


# ── Short / empty prompt tests ────────────────────────────────────────────────

class TestShortPrompts:
    def test_empty_string(self):
        out = run_hook("")
        assert not is_triggered(out)

    def test_single_word(self):
        out = run_hook("ok")
        assert not is_triggered(out)

    def test_below_minimum_length(self):
        out = run_hook("fix it")
        assert not is_triggered(out)


# ── Clear prompt tests (should pass through) ──────────────────────────────────

class TestClearPrompts:
    def test_file_path_in_prompt(self):
        out = run_hook("fix the type error in src/components/Button.tsx line 42")
        assert not is_triggered(out)

    def test_specific_function_named(self):
        out = run_hook("refactor the useAuth hook in src/hooks/useAuth.ts to use useCallback")
        assert not is_triggered(out)

    def test_component_with_path(self):
        out = run_hook("add error boundary to app/dashboard/page.tsx")
        assert not is_triggered(out)

    def test_explicit_export_keyword(self):
        out = run_hook("update the export default function in lib/utils.ts")
        assert not is_triggered(out)

    def test_long_detailed_prompt_with_clear_signals(self):
        out = run_hook(
            "refactor handleSubmit in src/app/login/page.tsx to use React Hook Form "
            "instead of manual state, keep the existing Zod schema, do not change the "
            "component props or the form field names"
        )
        assert not is_triggered(out)


# ── Vague prompt tests (should trigger skill) ─────────────────────────────────

class TestVaguePrompts:
    def test_nextjs_with_no_scope(self):
        out = run_hook("build a nextjs app with supabase auth")
        assert is_triggered(out)

    def test_chrome_extension(self):
        out = run_hook("create a chrome extension that saves tabs")
        assert is_triggered(out)

    def test_help_me_phrasing(self):
        out = run_hook("i want to add a dashboard to my app")
        assert is_triggered(out)

    def test_framework_stack_combo(self):
        out = run_hook("make a react app with tailwind and shadcn")
        assert is_triggered(out)

    def test_backend_stack(self):
        out = run_hook("set up a fastapi backend with prisma")
        assert is_triggered(out)

    def test_ai_framework(self):
        out = run_hook("build an ai chatbot with langchain")
        assert is_triggered(out)

    def test_auth_without_scope(self):
        out = run_hook("add nextauth to my project")
        assert is_triggered(out)

    def test_from_scratch(self):
        out = run_hook("scaffold a t3 stack app from scratch")
        assert is_triggered(out)

    def test_mobile_framework(self):
        out = run_hook("build an expo app with supabase")
        assert is_triggered(out)

    def test_deployment(self):
        out = run_hook("help me deploy to cloudflare workers")
        assert is_triggered(out)


# ── Output structure tests ────────────────────────────────────────────────────

class TestOutputStructure:
    def test_triggered_output_has_correct_keys(self):
        out = run_hook("build a nextjs app with supabase auth")
        assert "hookSpecificOutput" in out
        assert "hookEventName" in out["hookSpecificOutput"]
        assert "additionalContext" in out["hookSpecificOutput"]

    def test_triggered_event_name_is_correct(self):
        out = run_hook("build a nextjs app with supabase auth")
        assert out["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"

    def test_additional_context_is_string(self):
        out = run_hook("build a nextjs supabase saas app")
        ctx = out["hookSpecificOutput"]["additionalContext"]
        assert isinstance(ctx, str)
        assert len(ctx) > 0


# ── Resilience tests ──────────────────────────────────────────────────────────

class TestResilience:
    def test_malformed_json_does_not_crash(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input="not valid json at all",
            capture_output=True,
            text=True,
        )
        assert result.returncode in (0, 1)

    def test_empty_json_object(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input="{}",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_missing_prompt_key(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps({"other_key": "value"}),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_prompt_with_special_characters(self):
        out = run_hook('build a nextjs app with auth — "quotes" and \\backslashes\\')
        # Should not crash — triggered or not doesn't matter, just no exception
        assert isinstance(out, dict)

    def test_very_long_prompt(self):
        long_prompt = "build a nextjs supabase app " * 50
        out = run_hook(long_prompt)
        assert isinstance(out, dict)
