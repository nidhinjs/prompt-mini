# Credit-Killing Patterns

35 prompt anti-patterns that cause re-prompts, runaway agents, and wasted tokens. Read this file when diagnosing a weak prompt or when the original has clear structural failures. Apply fixes silently — only flag if the fix changes the user's intent.

---

## Task Patterns

| # | Pattern | Bad | Fixed |
|---|---------|-----|-------|
| 1 | **Vague task verb** | "help me with my code" | "Refactor `getUserData()` in `src/lib/api.ts` to handle null returns with early exit" |
| 2 | **Two tasks in one** | "add auth AND set up email" | Split: Prompt 1 for auth, Prompt 2 for email. Each runs after the previous completes. |
| 3 | **No success condition** | "make it better" | "Done when the component renders without console errors and accepts `user: User \| null`" |
| 4 | **Over-permissive agent** | "do whatever it takes" | Explicit allowed list + explicit forbidden list. No open-ended permissions. |
| 5 | **Emotional description** | "it's completely broken fix everything" | "Throws `TypeError: Cannot read property 'id' of undefined` at `src/auth.ts:43` when `user` is null" |
| 6 | **Build the whole thing** | "build my entire app" | Prompt 1: scaffold + routing. Prompt 2: core feature. Prompt 3: auth. Never one shot. |
| 7 | **Implicit reference** | "now add the other thing we discussed" | Always restate the full task. Claude Code has no cross-session memory. |

---

## Context Patterns

| # | Pattern | Bad | Fixed |
|---|---------|-----|-------|
| 8 | **No project state** | "add a login page" | "Next.js 15 App Router. No auth exists. Supabase client in `lib/supabase.ts`. No middleware yet." |
| 9 | **Forgotten stack** | New prompt contradicts prior tech choice | Include stack block: framework, ORM, auth, UI library, deployment target. Every prompt. |
| 10 | **No prior failure context** | (blank) | "Already tried `getSession()` on client side — it returns null. The issue is server-side auth." |
| 11 | **Hallucination invite** | "what's the best way to do X?" | "Recommend only patterns you are certain are supported in Next.js 15 App Router. Say [uncertain] if not." |
| 12 | **Assumed Claude Code memory** | "you already know my project" | Claude Code has no memory between sessions. Always provide full context in the prompt. |
| 13 | **No mention of what was tried** | (blank) | "Tried X — failed because Y. Do not suggest X." |

---

## Scope Patterns

| # | Pattern | Bad | Fixed |
|---|---------|-----|-------|
| 14 | **No file scope** | "fix the auth bug" | "Fix `handleLogin()` in `src/app/(auth)/login/page.tsx` only. Touch nothing else." |
| 15 | **No stack constraints** | "build a form component" | "React 18, TypeScript strict, Tailwind only, no new libraries, shadcn `<Input>` and `<Button>` only" |
| 16 | **Missing forbidden list** | Agent touches config files | "MUST NOT touch: `package.json`, `.env`, `next.config.ts`, `prisma/schema.prisma`" |
| 17 | **No stop condition** | "build the whole feature" | Stop conditions required: list every destructive action that needs human approval first |
| 18 | **Wrong scope for IDE AI** | "update the login function" | "Update `handleLogin()` in `src/pages/Login.tsx` — that function only, nothing else in the file" |
| 19 | **Entire codebase as context** | Full repo dump | Scope to the one relevant file and function. More context = more drift. |

---

## Agentic Patterns (Claude Code specific)

| # | Pattern | Bad | Fixed |
|---|---------|-----|-------|
| 20 | **No starting state** | "build a REST API" | "Empty Node.js project. Express 4.18 installed. `src/app.ts` exists with basic server setup." |
| 21 | **No target state** | "add authentication" | "`src/middleware/auth.ts` with JWT verify middleware. `POST /login` and `POST /register` routes in `src/routes/auth.ts`." |
| 22 | **Silent agent** | No progress output | "After each step output: ✅ [what was completed]" — catches failures early, costs ~5 tokens |
| 23 | **Unlocked filesystem** | No file restrictions | "ONLY edit files inside `src/`. MUST NOT touch `package.json`, `.env`, any config file." |
| 24 | **No human review trigger** | Agent decides everything | "Stop and ask before: deleting files, adding npm packages, modifying `.env`, changing database schema" |
| 25 | **No checkpoint summary** | Agent finishes silently | "At the end, output every file changed and what changed in each." |
| 26 | **Runaway loop risk** | No error handling instruction | "If an error cannot be resolved in 2 attempts, stop and report the exact error. Do not keep trying." |
| 27 | **Schema change without pause** | Migration runs silently | "Stop before running any migration or `prisma db push`. Show the schema diff and wait for approval." |

---

## Format Patterns

| # | Pattern | Bad | Fixed |
|---|---------|-----|-------|
| 28 | **No output format** | "explain this" | "List 3 bullet points, each under 20 words. One-sentence summary at top." |
| 29 | **Implicit length** | "write a summary" | "Exactly 2 sentences. No headers, no bullets." |
| 30 | **No role for complex tasks** | (blank) | "You are a senior Next.js engineer. Prioritize server components and minimize client-side JavaScript." |
| 31 | **Weak signal words** | "try to avoid", "should not" | Replace with MUST NOT and NEVER. Weak words get ignored under pressure. |

---

## Reasoning Patterns

| # | Pattern | Bad | Fixed |
|---|---------|-----|-------|
| 32 | **No CoT for logic tasks** | "which approach is better?" | "Think through both approaches step by step before recommending. Consider performance, maintainability, and existing patterns in this codebase." |
| 33 | **CoT on reasoning models** | Sending "think step by step" to extended thinking | Remove it — Claude's extended thinking mode reasons internally. CoT instructions degrade output. |
| 34 | **Contradicting prior decisions** | New prompt ignores earlier architecture | Always restate established decisions: "Auth is Supabase. ORM is Drizzle. Do not suggest alternatives." |
| 35 | **Ghost features** | Agent adds unrequested extras | "Do NOT add features beyond what is stated. No loading states, no error boundaries, no extra components unless explicitly requested." |
