# prompt-mini

A Claude Code plugin that intercepts vague prompts via a `UserPromptSubmit` hook, classifies the user's skill level, asks at most 5 targeted questions, then forges a structured prompt tailored to the detected framework and task type — before Claude Code executes anything.

---

## What this repo is

This is the source repository for the prompt-mini Claude Code plugin. It is not a web app, not a CLI tool, and not a library. It is a plugin that installs into Claude Code and modifies how prompts are processed at the hook level.

---

## Project structure

```
.claude-plugin/
  plugin.json              plugin identity — name, version, author, license

.dev-marketplace/
  .claude-plugin/
    marketplace.json       local dev install config — points source to repo root

hooks/
  hooks.json               registers UserPromptSubmit → scripts/evaluate-prompt.py

scripts/
  evaluate-prompt.py       the hook gate — clarity scoring, bypass logic, skill trigger

skills/
  prompt-mini/
    SKILL.md               core skill brain — PAC zones, phase logic, reference table
    references/
      stacks.md            40+ framework entries with pitfalls, scope anchors, stop conditions
      question-patterns.md max-5 question engine and credit-killing anti-patterns
      templates.md         6 forged prompt templates (ReAct, File-Scope, Scaffold, Debug, Migrate, Review)
      patterns.md          35 Claude Code prompt anti-patterns with fixes

tests/
  test-prompts.md          test cases for the hook — run before any changes to evaluate-prompt.py

assets/                    demo GIFs and screenshots for README

CHANGELOG.md               version history
README.md                  public documentation
```

---

## How the plugin works

```
User types a prompt
       ↓
evaluate-prompt.py runs (UserPromptSubmit hook)
       ↓
Bypass? (* / # prefix) → pass through unchanged
Too short? (<12 chars)  → pass through unchanged
Clear prompt?           → pass through, inject prompt as additionalContext
Vague prompt?           → inject evaluation wrapper → prompt-mini skill fires
       ↓
Skill: scan project files → classify skill level → load matching stack sections
       ↓
Ask ≤5 questions → assemble forged prompt → deliver as single copyable block
```

---

## Development rules

- NEVER change the output format of `evaluate-prompt.py` without running all test cases in `tests/test-prompts.md` first
- NEVER increase hook token overhead above ~250 tokens — the bypass path must stay lightweight
- NEVER add a mandatory question to the skill — the hard cap is 5, target is 3
- NEVER break bypass prefix handling — `*`, `/`, `#` must always pass through
- Reference files in `skills/prompt-mini/references/` are lazy-loaded — they cost zero tokens until Claude reads them explicitly
- `stacks.md` entries MUST follow the established schema — see the file header

---

## Testing the hook locally (no Claude Code needed)

```bash
# Should pass through — clear prompt
echo '{"prompt": "fix the type error in src/components/Button.tsx line 42"}' | python3 scripts/evaluate-prompt.py

# Should trigger skill — vague + framework mention
echo '{"prompt": "build a nextjs app with supabase auth"}' | python3 scripts/evaluate-prompt.py

# Should pass through — bypass prefix
echo '{"prompt": "* run this as-is: fix everything"}' | python3 scripts/evaluate-prompt.py
```

Expected output on pass-through:
```json
{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "..."}}
```
No output on bypass or short prompts (script exits 0 silently).

---

## Testing the skill (no Claude Code needed)

Open claude.ai. Start a new conversation. Paste the full contents of `skills/prompt-mini/SKILL.md` as your first message. Then send a vague prompt like "add auth to my app". Verify that:
1. Claude asks ≤5 targeted questions
2. Questions do not ask what can be inferred from a typical project (framework, TypeScript, folder structure)
3. After answers, Claude delivers one structured prompt block — no preamble, no explanation

---

## Local dev install (testing the full plugin without marketplace)

```bash
# From inside Claude Code terminal
claude plugin marketplace add /absolute/path/to/prompt-mini/.dev-marketplace/.claude-plugin/marketplace.json
claude plugin install prompt-mini@local-dev
```

---

## Adding a new framework to stacks.md

Each entry follows this schema exactly:

```
### [Framework Name]
use-cases: webapp, saas, mobile   (comma-separated from the standard list)
detect: package.json key or config file that signals this framework
prompt-context: what to always include in forged prompts for this stack
pitfalls: what Claude Code gets wrong — prevent these in the forged prompt
scope-anchors: real file paths to put in the Scope block
stop-conditions: destructive actions specific to this stack
```

Standard use-case tags: `webapp`, `saas`, `mobile`, `desktop`, `extension`, `backend`, `ai-app`, `database`, `auth`, `deploy`

---

## Versioning

Increment `version` in `.claude-plugin/plugin.json` and add an entry to `CHANGELOG.md` on every meaningful change.

- Patch (0.x.Y): bug fixes in evaluate-prompt.py, wording fixes in skill or references
- Minor (0.X.0): new framework in stacks.md, new template, new question pattern
- Major (X.0.0): breaking change to hook output format, skill architecture change
