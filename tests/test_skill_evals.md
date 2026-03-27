# Skill Eval Test Cases

Tests for `skills/prompt-mini/SKILL.md` behavior.
Run these manually in claude.ai — paste SKILL.md as your first message, then send each prompt below.

**How to run:**
1. Open claude.ai, new conversation
2. Paste the full contents of `skills/prompt-mini/SKILL.md` as your first message
3. Send each test prompt below
4. Mark PASS or FAIL based on the criteria

---

## Category 1 — Question Engine (max-5 rule)

### Test S-01
**Prompt:** `add auth to my app`
**Criteria:**
- [ ] Asks ≤5 questions total
- [ ] Does NOT ask "what framework are you using?" (should infer or make it a question only if genuinely unknown)
- [ ] Offers options per question, not open-ended blanks
- [ ] Does NOT ask about TypeScript, error handling, or file naming
- [ ] After answers → delivers one forged prompt block, no preamble

---

### Test S-02
**Prompt:** `build a nextjs app with supabase auth and a dashboard`
**Criteria:**
- [ ] Asks ≤5 questions
- [ ] Does NOT ask what framework (Next.js is stated)
- [ ] Does NOT ask what database (Supabase is stated)
- [ ] May ask: which page the dashboard lives on, new project or existing, auth strategy
- [ ] Forged prompt references real Next.js App Router file paths (app/, middleware.ts)

---

### Test S-03 — Senior user
**Prompt:** `implement a server action in app/dashboard/actions.ts that queries the users table via Drizzle and returns the 10 most recent signups — use the existing db client in lib/db.ts`
**Criteria:**
- [ ] Asks 0–2 questions maximum (prompt is already specific)
- [ ] Does NOT ask about framework, database, or file naming
- [ ] Forged prompt scopes exactly to app/dashboard/actions.ts and lib/db.ts
- [ ] Stop conditions reference those exact files

---

### Test S-04 — Beginner user
**Prompt:** `i want to make an app where users can save their favourite recipes`
**Criteria:**
- [ ] Classifies as beginner (no tech terms, describes outcome)
- [ ] Offers opinionated stack choices as options — does not ask "which framework do you want?"
- [ ] Plain language questions — no jargon like "RSC" or "SSR"
- [ ] Makes sensible defaults for folder placement, error handling, auth strategy

---

## Category 2 — Template Selection

### Test S-05 — ReAct Agent template
**Prompt:** `add a complete checkout flow with Stripe to my Next.js app — payment intent, webhook handler, and success page`
**Criteria:**
- [ ] Uses Template A (ReAct Agent) — multi-step, multi-file
- [ ] Forged prompt has: Context, Objective, Starting state, Target state, Allowed actions, Forbidden actions, Stop conditions, Checkpoints
- [ ] Stop conditions include: "stop before adding npm packages", "stop before touching .env"
- [ ] Checkpoint output instruction included (✅ after each step)

---

### Test S-06 — File-Scope template
**Prompt:** `the login form in src/app/login/page.tsx throws a TypeError when email is null — fix it`
**Criteria:**
- [ ] Uses Template B (File-Scope) — single file, specific error
- [ ] Forged prompt scopes ONLY to src/app/login/page.tsx
- [ ] Includes current behavior vs desired behavior blocks
- [ ] MUST NOT touch anything else in the file

---

### Test S-07 — Debug template
**Prompt:** `TypeError: Cannot read properties of undefined (reading 'id') at getUserData src/lib/api.ts:43`
**Criteria:**
- [ ] Uses Template D (Debug)
- [ ] Forged prompt includes the exact error message
- [ ] Includes "what was tried" block (or asks if not known)
- [ ] Stop condition: "do not refactor beyond fixing the reported error"

---

## Category 3 — Anti-Pattern Fixes (silent)

### Test S-08 — Split task
**Prompt:** `add auth AND set up Stripe payments`
**Criteria:**
- [ ] Recognises two distinct tasks
- [ ] Delivers Prompt 1 (auth) and Prompt 2 (Stripe) as separate blocks
- [ ] "Run Prompt 1 first. Ask for Prompt 2 after it completes."
- [ ] Does NOT merge both into one prompt

---

### Test S-09 — No ghost features
**Prompt:** `add a loading spinner to the submit button in the checkout form`
**Criteria:**
- [ ] Forged prompt does NOT add: error boundaries, form validation improvements, animations, accessibility improvements unless asked
- [ ] Scope is exactly the submit button loading state
- [ ] MUST NOT touch anything beyond the button component

---

### Test S-10 — Constraints in first 30%
**Prompt:** `refactor the user profile page — do not touch the avatar upload component`
**Criteria:**
- [ ] "MUST NOT touch avatar upload component" appears in the first third of the forged prompt
- [ ] Not buried at the bottom

---

## Category 4 — Credit-Saving Rules

### Test S-11 — MUST/NEVER language
**Prompt:** `update the API route to validate the request body`
**Criteria:**
- [ ] Forged prompt uses MUST and NEVER — not "should" or "try to avoid"
- [ ] Stop conditions use "Stop and ask before..." not "be careful with..."

---

### Test S-12 — Real file paths
**Prompt:** `add server-side auth protection to the dashboard`
**Criteria:**
- [ ] Scope block references real paths: middleware.ts, app/dashboard/
- [ ] NOT vague like "in the authentication module" or "in the project"

---

## Scoring

| Test | PASS | FAIL | Notes |
|------|------|------|-------|
| S-01 | | | |
| S-02 | | | |
| S-03 | | | |
| S-04 | | | |
| S-05 | | | |
| S-06 | | | |
| S-07 | | | |
| S-08 | | | |
| S-09 | | | |
| S-10 | | | |
| S-11 | | | |
| S-12 | | | |

**Target: 10/12 pass before shipping v1.0.0**
