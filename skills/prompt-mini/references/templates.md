# Prompt Templates

Structured templates for forging Claude Code prompts. Read only the template matching the task type. Never load all at once.

## When to use each

| Template | Use when |
|----------|----------|
| [A — ReAct Agent](#template-a--react-agent) | Multi-step feature build, any task spanning multiple files |
| [B — File-Scope](#template-b--file-scope) | Single file edit, bug fix, refactor of one component or function |
| [C — Scaffold](#template-c--scaffold) | New project, new module, greenfield feature from zero |
| [D — Debug](#template-d--debug) | Known error, failing test, broken behavior with a traceback |
| [E — Migrate](#template-e--migrate) | Schema change, dependency upgrade, API migration |
| [F — Review](#template-f--review) | Code review, audit, security check, performance analysis |

---

## Template A — ReAct Agent

Use for any multi-step task where Claude Code will take autonomous actions across multiple files. Stop conditions are mandatory — without them, agents loop and burn credits.

```
## Context
Stack: [framework + versions + key libraries]
Current state: [what exists now — relevant files and their current behavior]
Prior decisions: [architecture choices already made, do not revisit]
What was tried: [previous attempts and why they failed, if any]

## Objective
[Single unambiguous goal in one sentence. Precise verb + exact target.]

## Starting state
[Exact file structure and environment state before this task begins]

## Target state
[What should exist when done — specific files, exports, behavior]

## Allowed actions
- Read and modify files inside: [specific directories only]
- Install only packages already in package.json / requirements.txt
- [Any other explicitly permitted action]

## Forbidden actions
- MUST NOT modify: [list specific files — config, schema, unrelated modules]
- MUST NOT run: [build commands, migrations, deployments]
- MUST NOT add features beyond what is stated in this prompt
- MUST NOT push to git or modify .env

## Stop conditions
Stop and ask before:
- Deleting any file
- Adding any npm / pip package not already installed
- Modifying package.json, .env, any config file, or database schema
- Running any migration
- Encountering an error that cannot be resolved in 2 attempts

## Checkpoints
After each major step, output: ✅ [what was completed]
At the end, output every file changed and what changed in each.
```

---

## Template B — File-Scope

Use for targeted single-file edits: bug fixes, refactors, adding a prop, updating a function. The most common Claude Code task type. Tight scope = no drift.

```
File: [exact/path/to/file.ext]
Target: [exact function name, component name, or section]

Current behavior:
[What this code does now — be specific about the broken or incomplete part]

Required change:
[What it must do after the edit — be specific]

Scope:
ONLY modify [function / component / section name].
MUST NOT touch anything else in this file or any other file.

Constraints:
- [Framework/language version]
- Do not add dependencies not already in package.json
- Preserve: [existing type signatures / API contracts / prop names]
- Follow existing code style and naming conventions in this file

Done when:
[Binary condition: "renders without error", "returns 200 from /api/login", "passes the existing test in __tests__/auth.test.ts"]
```

---

## Template C — Scaffold

Use when building something from zero: new project, new module, new route, new feature with no existing code to reference.

```
## Context
Stack: [every library, framework, and version that will be used]
Project structure: [existing directories and conventions to follow]

## What to build
[Name and purpose of the thing being scaffolded]

## Files to create
[List every file that should exist when done, with its purpose]

## Conventions to follow
- Naming: [file naming pattern, export style]
- Styling: [Tailwind / CSS modules / styled-components]
- State: [useState / Zustand / server state only]
- Data fetching: [server action / API route / React Query]

## Do NOT create
- [Any file not listed above]
- [Any library not in the stack]
- [Any boilerplate beyond what is listed]

## Done when
[Every listed file exists, no TypeScript errors, dev server starts]
```

---

## Template D — Debug

Use when there is a known error, failing test, or broken behavior with enough information to diagnose. The more specific the error, the better the output.

```
## Error
[Exact error message and stack trace — copy paste, do not paraphrase]

## Where it occurs
File: [exact path]
Function / line: [exact location if known]
Trigger: [what action causes this error]

## Environment
Stack: [framework + versions]
Node / Python / runtime version: [version]

## What was tried
[Previous fix attempts and why they failed. Do not suggest these again.]

## Constraints
- Fix only the reported error
- MUST NOT refactor code beyond what is needed for the fix
- MUST NOT change function signatures, prop types, or API contracts
- MUST NOT add new dependencies

## Done when
[Error no longer occurs. Existing tests still pass.]
```

---

## Template E — Migrate

Use for dependency upgrades, API migrations, schema changes, or any task that involves changing how existing code is structured or connected. Highest risk template — stop conditions are critical.

```
## Context
Stack: [current versions → target versions]
Scope: [which files or directories are involved]

## Migration task
From: [current state — API, schema, version, pattern]
To: [target state — new API, schema, version, pattern]

## Migration steps
[Ordered list of changes — most specific to least specific]

## Constraints
- Change only what is required for this migration
- Preserve all existing behavior and API contracts
- MUST NOT refactor unrelated code opportunistically
- MUST NOT change test files unless the migration breaks a test

## Stop conditions
Stop and ask before:
- Running any database migration
- Changing any file not directly involved in this migration
- Encountering a breaking change that requires an architectural decision

## Done when
[App starts. Existing tests pass. Migration-specific test passes if applicable.]
```

---

## Template F — Review

Use when asking Claude Code to audit, analyze, or review code without making changes. Output-only — no edits unless explicitly requested after review.

```
## Review target
File(s): [exact paths]
Scope: [what aspect to review — security, performance, type safety, conventions]

## Review criteria
[Specific things to check — e.g., "check for SQL injection risk in all Prisma raw queries", "check for missing null checks on user object"]

## Output format
For each issue found:
- Location: [file:line]
- Severity: [critical / warning / suggestion]
- Issue: [what is wrong]
- Fix: [specific recommended change]

## Constraints
- Do NOT make any edits during review
- Do NOT report style issues unless they affect correctness or security
- If no issues found, say so explicitly — do not invent findings

## Done when
Every file in scope has been reviewed and a structured report is output.
```
