# Question Patterns — AskUserQuestion Engine

Read this file during Phase 4. It covers the exact tool format, when to ask vs infer, corner cases, and credit-saving assembly rules.

---

## AskUserQuestion — Official Tool Schema

This is the exact format Claude Code expects. Do not deviate from it.

```json
{
  "questions": [
    {
      "question": "Clear specific question ending with ?",
      "header": "Short label",
      "multiSelect": false,
      "options": [
        {
          "label": "Concise choice (Recommended)",
          "description": "What this means, trade-offs, when to pick it"
        },
        {
          "label": "Alternative choice",
          "description": "What this means, when it applies"
        }
      ]
    }
  ]
}
```

### Hard limits — violating these breaks the tool

| Field | Constraint |
|-------|-----------|
| questions per call | 1–4 maximum |
| options per question | 2–4 exactly |
| header length | 12 characters maximum |
| multiSelect | must be explicitly set — never omit |
| Other option | NEVER add it — Claude Code provides it automatically |
| Recommended option | Put it FIRST and add "(Recommended)" to the label |
| question field | must end with `?` |
| label length | 1–5 words, concise and scannable |

### When to use multiSelect: true

Set `multiSelect: true` only when choices are genuinely non-exclusive — the user may legitimately want more than one:
- "Which platforms should this support?" → iOS AND Android are both valid
- "Which environments need this configured?" → dev AND staging AND prod
- "Which pages should have auth protection?" → multiple routes

Set `multiSelect: false` for everything else. Most questions are mutually exclusive.

---

## The Deduction Rule — Apply Before Every Question

Before writing any question, check each source in order. If the answer exists — infer, do not ask.

1. `package.json` → framework, dependencies, versions, scripts
2. `CLAUDE.md` → locked decisions, forbidden actions, conventions
3. Directory structure → `app/` = App Router, `pages/` = Pages Router, `src/` = SPA
4. File imports → active libraries, state pattern, styling approach
5. Conversation history → prior decisions, what failed, what was tried
6. Open files → the exact component or function likely in scope

**Cost of asking what you can infer:** one unnecessary question = one extra round-trip = wasted tokens on both sides.

---

## Credit-Killing Question Anti-Patterns

Never ask these. They signal you did not check the codebase.

| Never ask | Why | Instead |
|-----------|-----|---------|
| "What framework are you using?" | Read package.json | Infer and state assumption |
| "Do you want TypeScript?" | Check for .ts files | Infer from project |
| "What styling library?" | Check package.json | Infer from deps |
| "Should I use server or client component?" | Infer from use case | Decide, state assumption |
| "What should I name the file?" | Follow existing conventions | Name it, move on |
| "Do you want error handling?" | Always yes | Include it by default |
| "Should I add comments?" | Not unless asked | Skip |
| "Do you want tests?" | Only ask if tests/ folder exists | Otherwise skip |
| "Which language?" | Read existing files | Infer |
| "Do you want dark mode?" | Not asked, don't add it | Ghost feature |

---

## When to Ask vs Infer vs Decide

### Always ask — cannot be inferred
- Which specific page, route, or component when multiple candidates exist in the project
- Whether to create a new file or modify existing when both are equally plausible
- The exact task when the prompt is genuinely ambiguous after reading all files

### Ask for intermediate/senior — decide for beginners
| Decision | Ask when | Beginner default |
|----------|----------|-----------------|
| Auth strategy | Stack doesn't dictate one | Pick the standard for their stack |
| API pattern | Server action vs route handler is unclear | Server action for App Router |
| State approach | Complex feature, multiple valid options | useState/context first |
| Database pattern | Multiple ORMs detected | Match existing pattern |

### Never ask — always decide silently
| Decision | Rule |
|----------|------|
| Folder placement | Follow existing project structure |
| File naming | Match existing conventions in the project |
| Error handling style | Match existing pattern or framework default |
| TypeScript strictness | Match existing tsconfig |
| Import style | Match existing files (named vs default) |
| Component structure | Match existing components |

---

## Corner Cases — Multi-Framework and Complex Scenarios

These are the situations that cause confusion. Handle each explicitly.

### User mentions multiple frameworks
**Example:** "build a Next.js app with Supabase, Prisma, Clerk, and Tailwind"

Do NOT ask about each — this is one stack. Detect all four, load all matching sections from `stacks.md`, combine their constraints and stop conditions into one forged prompt. Only ask what is still genuinely ambiguous after reading all of them together.

### User wants multiple output types
**Example:** "build a web app AND a Chrome extension that share the same backend"

This is two separate tasks. Use `multiSelect: false` for which to build first:
```json
{
  "question": "Which should be built first?",
  "header": "Build order",
  "multiSelect": false,
  "options": [
    {
      "label": "Web app (Recommended)",
      "description": "Build the shared backend + web app first. Extension can then consume the same API."
    },
    {
      "label": "Chrome extension",
      "description": "Build extension first. Will need a stub API until the backend is built."
    }
  ]
}
```

### User is unsure which framework to use
**Example:** "I want to build a SaaS app, not sure if Next.js or Remix"

This is a valid question. Use a single question with trade-off descriptions:
```json
{
  "question": "Which framework should we use for your SaaS?",
  "header": "Framework",
  "multiSelect": false,
  "options": [
    {
      "label": "Next.js App Router (Recommended)",
      "description": "Larger ecosystem, better Vercel integration, more community resources. Best default for SaaS."
    },
    {
      "label": "Remix",
      "description": "Stronger data loading patterns, better form handling, excellent for data-heavy apps."
    }
  ]
}
```

### User names a framework that does not match their project type
**Example:** "add a React Native screen" — but the project has no Expo or RN in package.json

Do not assume. Ask:
```json
{
  "question": "No React Native setup was found in this project. How should we proceed?",
  "header": "RN setup",
  "multiSelect": false,
  "options": [
    {
      "label": "Add Expo to this project",
      "description": "Initialize Expo SDK in this repo. Will require running npx create-expo-app or expo init."
    },
    {
      "label": "This is a separate project",
      "description": "The RN app lives in a different folder. Provide the correct path and I'll work there."
    }
  ]
}
```

### User asks for something that conflicts with existing architecture
**Example:** "add Redux" — but the project already uses Zustand

Flag the conflict, do not silently override:
```json
{
  "question": "This project already uses Zustand for state management. How should we proceed?",
  "header": "State mgmt",
  "multiSelect": false,
  "options": [
    {
      "label": "Keep Zustand (Recommended)",
      "description": "Continue with Zustand. I'll implement the new feature using the existing pattern."
    },
    {
      "label": "Replace with Redux",
      "description": "Migrate existing Zustand stores to Redux. This is a larger refactor — I'll split it into Prompt 1 (migration) and Prompt 2 (new feature)."
    }
  ]
}
```

### User wants to add a feature that requires an uninstalled package
**Example:** "add Stripe payments" — no Stripe package in package.json

State the dependency in the forged prompt's stop conditions — do not ask. Adding npm packages is a stop condition: "Stop and ask before installing stripe or @stripe/stripe-js."

### User gives a brand new greenfield project with no existing code
Nothing to infer from. Ask the minimum needed to establish the stack:
```json
[
  {
    "question": "What type of project is this?",
    "header": "Project type",
    "multiSelect": false,
    "options": [
      { "label": "Web app / SaaS (Recommended)", "description": "Browser-based app with a backend" },
      { "label": "Mobile app", "description": "iOS and/or Android via React Native or Flutter" },
      { "label": "Chrome extension", "description": "Browser plugin with content scripts or popup" },
      { "label": "Backend / API only", "description": "Server-side service, no frontend" }
    ]
  },
  {
    "question": "Which stack would you like to use?",
    "header": "Stack",
    "multiSelect": false,
    "options": [
      { "label": "Next.js + Supabase (Recommended)", "description": "Full-stack React with managed Postgres. Best default for most web apps." },
      { "label": "Vite + React + Node", "description": "SPA with a separate backend. More flexibility, more setup." },
      { "label": "T3 Stack", "description": "Next.js + Prisma + tRPC + TypeScript. Opinionated but powerful." },
      { "label": "Something else", "description": "Tell me your preferred stack in the Other field." }
    ]
  }
]
```

### User specifies conflicting frameworks
**Example:** "use Next.js Pages Router and App Router"

These cannot coexist cleanly. Flag it:
```json
{
  "question": "Next.js supports either App Router or Pages Router per project, not both equally. Which should this feature use?",
  "header": "Router",
  "multiSelect": false,
  "options": [
    {
      "label": "App Router (Recommended)",
      "description": "Modern approach with server components and server actions. Recommended for new features."
    },
    {
      "label": "Pages Router",
      "description": "Classic approach. Choose this if the rest of the project is already in pages/."
    }
  ]
}
```

### Multi-platform support — use multiSelect
**Example:** "make this work on iOS and Android"

```json
{
  "question": "Which platforms should this feature support?",
  "header": "Platforms",
  "multiSelect": true,
  "options": [
    { "label": "iOS", "description": "Apple devices via Expo iOS build" },
    { "label": "Android", "description": "Android devices via Expo Android build" },
    { "label": "Web", "description": "Browser via Expo Web (React Native Web)" }
  ]
}
```

### User says "keep it simple" or "make it basic"
Read as: fewer questions, more beginner defaults, simpler template. Do not ask about auth strategy, state management, or patterns. Pick the simplest reasonable default for every decision and state it in the forged prompt context block.

### User says "production-ready" or "enterprise"
Read as: more detailed stop conditions, explicit RLS/security constraints from stacks.md, split into multiple prompts if scope is large. Flag any shortcuts that would undermine production quality.

---

## Question Format Reference

### 1 question — single clear ambiguity
```json
{
  "questions": [
    {
      "question": "Which component should be modified?",
      "header": "Component",
      "multiSelect": false,
      "options": [
        {
          "label": "LoginForm (Recommended)",
          "description": "src/components/auth/LoginForm.tsx — handles email/password submission"
        },
        {
          "label": "AuthProvider",
          "description": "src/components/auth/AuthProvider.tsx — wraps the app with session state"
        }
      ]
    }
  ]
}
```

### 2–3 questions — moderate ambiguity
```json
{
  "questions": [
    {
      "question": "Which page should the dashboard live on?",
      "header": "Route",
      "multiSelect": false,
      "options": [
        { "label": "/dashboard (Recommended)", "description": "New protected route under app/dashboard/" },
        { "label": "/app/home", "description": "Rename and extend the existing home page" }
      ]
    },
    {
      "question": "Should the dashboard data load server-side or client-side?",
      "header": "Data fetch",
      "multiSelect": false,
      "options": [
        { "label": "Server component (Recommended)", "description": "Fetch on server, no loading state needed, better for SEO and performance" },
        { "label": "Client with useEffect", "description": "Fetch on client, easier to add real-time updates later" }
      ]
    }
  ]
}
```

### 4 questions — only for genuinely complex greenfield or architectural decisions
Use sparingly. If you are at 4 questions, check again whether any can be inferred.

---

## Credit-Saving Assembly Rules

Apply these when building the forged prompt in Phase 5.

**Rule 1 — Constraints in first 30%**
Critical MUST NOT rules appear in the first third of the prompt. They decay at the tail — Claude Code ignores late constraints under execution pressure.

**Rule 2 — Real file paths only**
Bad: "in the authentication module"
Good: "in `src/lib/auth.ts` and `src/middleware.ts` only"

**Rule 3 — Specific stop conditions**
Bad: "stop if something seems off"
Good: "Stop and ask before: deleting any file, adding any npm package, modifying `.env`, changing the database schema"

**Rule 4 — Split two-task prompts**
If the original request has two distinct deliverables, deliver Prompt 1 and Prompt 2 as separate blocks. Never merge them. Add: "➡️ Run Prompt 1 first. Ask for Prompt 2 after it completes."

**Rule 5 — MUST and NEVER over weak words**
"should not modify" → "MUST NOT modify"
"try to avoid" → "NEVER"
Weak words get ignored when the agent is deep in execution.

**Rule 6 — No ghost features**
If you added anything not in the original request, remove it. Scope creep costs credits and trust.

**Rule 7 — Checkpoint on every multi-step task**
Always include: "After each major step, output: ✅ [what was completed]"
Costs ~5 tokens. Catches failures before they compound.

**Rule 8 — Error ceiling**
Always include: "If an error cannot be resolved in 2 attempts, stop and report the exact error — do not keep trying."
Prevents runaway loops that burn credits.
