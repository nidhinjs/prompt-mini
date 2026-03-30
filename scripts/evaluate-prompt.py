#!/usr/bin/env python3
"""
prompt-mini — evaluate-prompt.py
Evaluates prompt clarity and invokes the prompt-mini skill for vague cases.
"""
import json
import re
import sys

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
if prompt.startswith("*"):
    output_json(prompt[1:].strip())
    sys.exit(0)
if prompt.startswith(("/", "#")):
    output_json(prompt)
    sys.exit(0)

# Short or empty prompts — pass through silently
if not prompt or len(prompt.strip()) < 12:
    sys.exit(0)

# ── Clarity scoring ────────────────────────────────────────────────────────
# CLEAR signals — prompt is already specific enough to execute directly
CLEAR = [
    # Exact file paths
    r"\.(tsx?|jsx?|py|go|rs|rb|php|sql|sh|css|html|json|yaml|yml|env)\b",
    r"(src/|app/|pages/|components/|lib/|api/|hooks/|utils/|services/|store/|types/)",
    # Specific code targets
    r"\b(function|component|class|method|const|export|interface|type|enum)\s+\w+",
    # Already structured
    r"(```|<context>|<task>|## |ONLY modify|MUST NOT)",
    # Specific line or error references
    r"\bline\s+\d+\b",
    r"\b(TypeError|SyntaxError|ReferenceError|404|500|undefined|null)\b",
]

# VAGUE signals — needs structuring before execution
VAGUE = [
    # Starting from scratch
    r"\b(build|create|make|develop|start|scaffold|generate|set up|setup)\b.{0,40}\b(app|application|project|site|website|platform|tool|system|service|api|backend|frontend)\b",
    r"\b(from scratch|from zero|brand new|greenfield|boilerplate|starter|template)\b",
    r"\b(full.?stack|end.?to.?end|entire|complete|whole)\b",

    # Feature requests without scope
    r"\b(add|implement|integrate|build|create)\b.{0,30}\b(auth|authentication|login|signup|payment|checkout|dashboard|profile|settings|search|filter|upload|notification|email|chat|feed|timeline)\b",

    # Framework mentions without file scope
    r"\b(nextjs|next\.js|react native|expo|flutter|svelte|nuxt|remix|astro|qwik|solid)\b",
    r"\b(fastapi|django|flask|express|fastify|nestjs|hono|laravel|rails|gin|axum)\b",
    r"\b(supabase|firebase|mongodb|prisma|drizzle|turso|convex|planetscale|neon)\b",
    r"\b(tailwind|shadcn|radix|chakra|mui|mantine|daisy|framer)\b",
    r"\b(stripe|twilio|sendgrid|resend|pusher|socket\.io|websocket)\b",
    r"\b(nextauth|clerk|auth0|lucia|better.?auth|kinde)\b",
    r"\b(vercel|railway|cloudflare|netlify|fly\.io|render|aws|gcp|docker)\b",
    r"\b(langchain|langgraph|openai|anthropic|gemini|vercel ai|huggingface)\b",
    r"\b(chrome extension|browser extension|mv3|manifest v3|vs code extension|raycast)\b",

    # Vague intent signals
    r"\b(i want|i need|can you|help me|how do i|i would like|please)\b",
    r"\b(something|something like|kind of|sort of|basically|essentially)\b",
    r"\b(improve|optimize|refactor|clean up|rewrite|redesign)\b.{0,20}\b(everything|all|whole|entire|app|project|codebase)\b",

    # Mobile / desktop
    r"\b(ios|android|mobile app|desktop app|cross.?platform)\b",
    r"\b(react native|expo|flutter|tauri|electron|swift|kotlin|jetpack)\b",
]

text = prompt.lower()
words = len(text.split())
clear_hits = sum(1 for s in CLEAR if re.search(s, text))
vague_hits = sum(1 for s in VAGUE if re.search(s, text))

# Any prompt under 6 words with no clear signals is vague
if words < 6 and clear_hits == 0:
    vague_hits += 3

# Medium prompts with no clear signals lean vague
if words < 15 and clear_hits == 0 and vague_hits == 0:
    vague_hits += 1

# Long detailed prompts with multiple clear signals pass through
if words > 35 and clear_hits >= 3:
    output_json(prompt)
    sys.exit(0)

# Clear wins only if it strongly outweighs vague
needs_skill = vague_hits >= clear_hits or (vague_hits > 0 and clear_hits <= 1)

# ── Output ─────────────────────────────────────────────────────────────────
if needs_skill:
    # Compact wrapper — minimum tokens, maximum signal
    output_json(f'prompt-mini: The user wants to BUILD something, not receive a prompt. Invoke the prompt-mini skill now for "{escaped_prompt}". Ask up to 6 questions to gather context, then EXECUTE the task immediately — do not show the forged prompt as text.')
else:
    output_json(prompt)

sys.exit(0)
