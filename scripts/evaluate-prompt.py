#!/usr/bin/env python3
"""
prompt-mini — evaluate-prompt.py
Evaluates prompt clarity and invokes the prompt-mini skill for vague cases.
"""
import json
import re
import sys

# ── Input ──────────────────────────────────────────────────────────────────
try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

prompt = input_data.get("prompt", "")
escaped_prompt = prompt.replace("\\", "\\\\").replace('"', '\\"')

def output_json(text):
    """Output text in UserPromptSubmit JSON format"""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": text
        }
    }))

# ── Bypass conditions ──────────────────────────────────────────────────────
# * prefix: user explicitly skips prompt-mini
# / prefix: slash commands (built-in or custom)
# # prefix: memory/context commands
if prompt.startswith("*"):
    output_json(prompt[1:].strip())
    sys.exit(0)
if prompt.startswith(("/", "#")):
    output_json(prompt)
    sys.exit(0)

# ── Clarity scoring ────────────────────────────────────────────────────────
# Clear signals: prompt already has enough scope to execute directly
CLEAR = [
    r"\.(tsx?|jsx?|py|go|rs|rb|php|sql|sh)\b",
    r"(src/|app/|pages/|components/|lib/|api/|hooks/)",
    r"\b(function|component|class|method|const|export)\b",
    r"(```|<context>|<task>)",
]

# Vague signals: framework/stack mention without clear scope or task
VAGUE = [
    r"\b(nextjs|next\.js|react|vite|svelte|nuxt|remix|astro|qwik)\b",
    r"\b(expo|flutter|swift|kotlin|capacitor|ionic)\b",
    r"\b(supabase|prisma|drizzle|firebase|mongodb|turso|neon|convex)\b",
    r"\b(tailwind|shadcn|radix|chakra|mui|mantine|daisy)\b",
    r"\b(fastapi|django|flask|express|fastify|nestjs|hono|laravel)\b",
    r"\b(chrome extension|browser extension|mv3|manifest v3)\b",
    r"\b(langchain|langgraph|openai|anthropic sdk|gemini|vercel ai)\b",
    r"\b(vercel|railway|cloudflare workers|netlify|fly\.io|render)\b",
    r"\b(nextauth|clerk|supabase auth|auth0|lucia|kinde)\b",
    r"\b(build|make|create|add).{0,30}\b(app|site|dashboard|feature|tool|project)\b",
    r"\b(i want|i need|can you|help me|how do i)\b",
    r"\b(full.?stack|from scratch|boilerplate|scaffold|end.?to.?end)\b",
]

# Short or empty prompts — pass through silently
if not prompt or len(prompt.strip()) < 12:
    sys.exit(0)

text = prompt.lower()
words = len(text.split())
clear_hits = sum(1 for s in CLEAR if re.search(s, text))
vague_hits = sum(1 for s in VAGUE if re.search(s, text))

# Short prompts with no clear scope lean vague
if words < 8 and clear_hits == 0:
    vague_hits += 2

# Long prompts with multiple clear signals pass through
if words > 40 and clear_hits >= 2:
    output_json(prompt)
    sys.exit(0)

needs_skill = vague_hits > clear_hits or (vague_hits > 0 and clear_hits == 0)

# ── Output ─────────────────────────────────────────────────────────────────
if needs_skill:
    output_json(f"""PROMPT EVALUATION — prompt-mini
Original request: "{escaped_prompt}"

EVALUATE: Is this prompt clear enough to execute, or does it need structuring?

PROCEED IMMEDIATELY if:
- You have sufficient context from the codebase OR can infer the full intent
- Conversation history already covers the scope and stack

ONLY invoke the prompt-mini skill if genuinely vague (missing scope, target files, or stack clarity):
  1. Briefly note why: "prompt-mini flagged this as vague because [specific reason]."
  2. Invoke the prompt-mini skill — it will ask ≤5 clarifying questions and assemble a structured prompt
  3. Trust user intent. Check conversation history before invoking the skill.

If clear: proceed with the original request. If vague: invoke the skill.""")
else:
    output_json(prompt)

sys.exit(0)
