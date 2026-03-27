# Stacks Reference

Framework-specific context for forging prompts. Load only the sections matching the detected stack. Never load the entire file.

Each entry follows this schema:
- `use-cases:` — which project types this framework serves
- `detect:` — what file/key signals this framework is active
- `prompt-context:` — what to always include in the forged prompt when this stack is detected
- `pitfalls:` — what Claude Code gets wrong with this stack (prevent these explicitly)
- `scope-anchors:` — real file paths to use in the Scope block
- `stop-conditions:` — stack-specific stop conditions beyond the standard set

---

## Table of Contents

| Category | Frameworks |
|---|---|
| Web frameworks | Next.js App Router, Next.js Pages Router, Remix, SvelteKit, Astro, Nuxt 3, Qwik City, Vite + React, Vite + Vue 3, Vite + Svelte, T3 Stack |
| Mobile | React Native + Expo, Flutter, Kotlin + Compose, Swift + SwiftUI, Capacitor |
| Desktop | Tauri 2, Electron, Wails |
| Extensions | Chrome MV3, Firefox WebExtension, VS Code Extension, Raycast |
| Backend | Node + Express, Fastify, NestJS, Hono, FastAPI, Django, Flask, Go + chi, Rust + Axum, Laravel |
| AI / Agents | Vercel AI SDK, LangChain.js, LangGraph, Mastra, Anthropic SDK, OpenAI SDK |
| Database / ORM | Supabase, Prisma, Drizzle, MongoDB, Redis, Turso, Convex |
| Auth | NextAuth v5, Clerk, Supabase Auth, Better-Auth, Lucia |
| UI | Tailwind CSS 4, shadcn/ui, Radix, MUI, Mantine |
| Deploy | Vercel, Cloudflare Workers, Fly.io, Railway, Docker |

---

## WEB FRAMEWORKS

### Next.js App Router
use-cases: webapp, saas, ai-app, dashboard
detect: next.config.*, app/ directory present, "next" in package.json

prompt-context:
- State whether App Router (app/) or Pages Router (pages/) is in use
- Specify if using server actions or API routes for mutations
- Note if Turbopack is enabled (next dev --turbo)
- Include relevant layout.tsx, page.tsx, or route.ts context

pitfalls:
- Adds `"use client"` to everything — explicitly state which components stay server-side
- Creates API routes when server actions are more appropriate
- Mixes App Router and Pages Router patterns
- Ignores route groups — remind it that (folder) is a route group and affects layout nesting
- Forgets to add `"use server"` at top of action files
- Puts sensitive logic in client components

scope-anchors: app/, components/, lib/, middleware.ts, next.config.ts
stop-conditions:
- Stop before modifying next.config.ts
- Stop before changing any layout.tsx (affects all child routes)
- Stop before running `next build` or modifying .env

---

### Next.js Pages Router
use-cases: webapp, saas, legacy
detect: pages/ directory present, no app/ directory, "next" in package.json

prompt-context:
- Confirm Pages Router is in use (not App Router)
- State whether using getServerSideProps, getStaticProps, or API routes
- Include relevant pages/_app.tsx and pages/api/ context

pitfalls:
- Attempts to use server actions (App Router only)
- Mixes App Router file conventions into pages/
- Forgets that pages/api/ handlers need req/res pattern not Response objects

scope-anchors: pages/, components/, lib/, styles/
stop-conditions: Stop before modifying pages/_app.tsx or pages/_document.tsx

---

### Remix
use-cases: webapp, saas, fullstack
detect: "remix" in package.json, app/root.tsx present

prompt-context:
- State Remix version (v2 vs v1 patterns differ significantly)
- Note loader/action pattern in use
- Include relevant route file structure

pitfalls:
- Confuses Remix loaders with Next.js server actions
- Forgets that Remix uses nested routing by default
- Uses React state for data that should be in the loader

scope-anchors: app/routes/, app/components/, app/utils/
stop-conditions: Stop before modifying app/root.tsx or remix.config.js

---

### SvelteKit
use-cases: webapp, saas, fullstack
detect: "svelte" in package.json, svelte.config.js present

prompt-context:
- State SvelteKit version
- Note whether using form actions or API routes
- Include relevant +page.svelte, +layout.svelte context

pitfalls:
- Writes React patterns in Svelte files (useState, useEffect)
- Forgets SvelteKit's file-based routing conventions (+page, +layout, +server)
- Mixes SSR and client-only code incorrectly

scope-anchors: src/routes/, src/lib/, src/components/
stop-conditions: Stop before modifying svelte.config.js or app.html

---

### Astro
use-cases: webapp, landing-page, blog, docs
detect: "astro" in package.json, astro.config.* present

prompt-context:
- State output mode: static, SSR, or hybrid
- Note whether using React/Svelte/Vue islands
- Include relevant .astro component context

pitfalls:
- Adds React hooks to .astro files (not supported — put in island components)
- Forgets that .astro files are server-only by default
- Treats Astro like a React SPA

scope-anchors: src/pages/, src/components/, src/layouts/
stop-conditions: Stop before modifying astro.config.mjs

---

### Vite + React
use-cases: webapp, spa, dashboard
detect: vite.config.*, "react" and "vite" in package.json, no "next"

prompt-context:
- Confirm Vite + React SPA (no SSR unless Vite SSR plugin detected)
- State state management in use (useState, Zustand, Jotai, Redux)
- Note routing library (React Router v6/v7, TanStack Router)

pitfalls:
- Attempts server actions or server components (not available in Vite SPA)
- Forgets that all data fetching must be client-side unless SSR configured
- Uses Next.js file-based routing patterns

scope-anchors: src/, src/components/, src/pages/, src/hooks/, src/lib/
stop-conditions: Stop before modifying vite.config.ts

---

### T3 Stack
use-cases: saas, fullstack, webapp
detect: "trpc" in package.json, "prisma" in package.json, Next.js present

prompt-context:
- Include tRPC router location (server/api/routers/)
- Note Prisma schema location
- State auth provider (NextAuth or Clerk)
- Include relevant router and procedure context

pitfalls:
- Creates REST API routes instead of tRPC procedures
- Forgets to add new routers to the root router
- Misses the distinction between protected and public procedures
- Skips Prisma schema migration after model changes

scope-anchors: server/api/, src/server/, prisma/schema.prisma, src/components/
stop-conditions:
- Stop before running prisma migrate
- Stop before modifying prisma/schema.prisma
- Stop before modifying the root tRPC router

---

## MOBILE

### React Native + Expo
use-cases: mobile, cross-platform, ios, android
detect: "expo" in package.json, app.json or app.config.ts present

prompt-context:
- State Expo SDK version
- Note whether using Expo Router or React Navigation
- Specify target platforms (iOS, Android, or both)
- Include relevant app.json config context

pitfalls:
- Uses web DOM APIs (window, document) — not available in RN
- Imports web-only CSS — RN uses StyleSheet
- Forgets that navigation is file-based in Expo Router
- Misses platform-specific file conventions (.ios.ts, .android.ts)

scope-anchors: app/, components/, hooks/, lib/
stop-conditions:
- Stop before modifying app.json or eas.json
- Stop before adding a native module (requires rebuild)
- Stop before running expo prebuild

---

### Flutter
use-cases: mobile, cross-platform, desktop
detect: pubspec.yaml present, "flutter" in pubspec.yaml

prompt-context:
- State Flutter SDK version from pubspec.yaml
- Include relevant widget tree context
- Note state management package in use (Riverpod, Bloc, Provider, GetX)

pitfalls:
- Generates React/JS patterns instead of Dart
- Forgets stateful vs stateless widget distinction
- Adds dependencies without running flutter pub get

scope-anchors: lib/, lib/screens/, lib/widgets/, lib/services/
stop-conditions:
- Stop before modifying pubspec.yaml
- Stop before running flutter pub get or flutter build

---

## DESKTOP

### Tauri 2
use-cases: desktop, cross-platform
detect: src-tauri/ present, tauri.conf.json present

prompt-context:
- State frontend framework used (React, Svelte, Vue)
- Note Rust backend commands defined in src-tauri/src/
- Specify whether using Tauri v1 or v2 (APIs differ significantly)

pitfalls:
- Writes Rust code in the frontend or vice versa
- Forgets to register new Tauri commands in main.rs
- Uses Node.js APIs in the Rust backend
- Skips the invoke() bridge for frontend-to-backend calls

scope-anchors: src/ (frontend), src-tauri/src/ (Rust backend)
stop-conditions:
- Stop before modifying src-tauri/tauri.conf.json
- Stop before adding a Rust dependency to Cargo.toml
- Stop before running cargo build or tauri build

---

### Electron
use-cases: desktop, cross-platform
detect: "electron" in package.json, main.js or main.ts at root

prompt-context:
- Distinguish main process (main.ts) vs renderer process (renderer/)
- Note IPC communication pattern in use
- State whether using contextBridge for security

pitfalls:
- Puts Node.js code in the renderer (security violation in modern Electron)
- Forgets IPC bridge for renderer-to-main communication
- Uses remote module (deprecated)

scope-anchors: main.ts (or main.js), preload.ts, src/renderer/
stop-conditions: Stop before modifying package.json build config

---

## BROWSER EXTENSIONS

### Chrome MV3
use-cases: browser-extension, chrome-extension
detect: manifest.json with "manifest_version": 3

prompt-context:
- Confirm Manifest V3 (not MV2)
- State which contexts are involved: service worker (background), content script, popup, options
- Note what permissions are currently in manifest.json
- Include relevant content script or service worker context

pitfalls:
- Uses background page (MV2) instead of service worker (MV3)
- Forgets that service workers cannot access DOM
- Uses XMLHttpRequest instead of fetch in service worker
- Adds permissions to manifest without noting they need user approval
- Puts long-running logic in service worker (it sleeps)
- Confuses which context has access to what (content script sees DOM, SW does not)

scope-anchors: manifest.json, background/ or service-worker.js, content/ or content-scripts/, popup/, options/
stop-conditions:
- Stop before modifying manifest.json permissions
- Stop before adding host_permissions entries

---

### VS Code Extension
use-cases: vscode-extension
detect: .vscodeignore present, "vsce" in package.json, contributes in package.json

prompt-context:
- Include extension entry point (extension.ts)
- Note activation events in package.json
- State which VS Code APIs are in use

pitfalls:
- Registers commands without adding them to package.json contributes.commands
- Forgets to dispose of subscriptions in deactivate()
- Uses Node.js APIs not available in extension host

scope-anchors: src/extension.ts, package.json (contributes section)
stop-conditions: Stop before modifying activation events in package.json

---

## BACKEND

### FastAPI
use-cases: backend, ai-app, dashboard
detect: "fastapi" in requirements.txt or pyproject.toml, main.py with FastAPI()

prompt-context:
- State Python version
- Include Pydantic model definitions relevant to the task
- Note authentication middleware in use (OAuth2, JWT, API key)
- Include relevant router file context

pitfalls:
- Forgets Pydantic v2 syntax differences from v1
- Puts business logic directly in route functions instead of services
- Skips response_model — causes unintentional data leakage
- Forgets async/await for async endpoints

scope-anchors: main.py, routers/, models/, schemas/, services/
stop-conditions:
- Stop before modifying database models or running migrations
- Stop before adding a new dependency to requirements.txt

---

### NestJS
use-cases: backend, enterprise
detect: "nestjs" or "@nestjs/core" in package.json, src/main.ts with NestFactory

prompt-context:
- Include module structure context
- Note which modules are relevant to the task
- State ORM in use (TypeORM, Prisma, MikroORM)

pitfalls:
- Creates services without injecting them via module providers
- Forgets to add new providers/controllers to the module
- Skips decorators that NestJS requires (@Injectable, @Controller, @Get)

scope-anchors: src/modules/, src/common/, src/main.ts
stop-conditions: Stop before modifying AppModule or database entities

---

### Hono
use-cases: backend, edge
detect: "hono" in package.json

prompt-context:
- Note deployment target (Cloudflare Workers, Bun, Node)
- Include relevant route file context
- State middleware in use

pitfalls:
- Uses Node.js-specific APIs when targeting Cloudflare Workers
- Forgets that Hono's Context (c) is not Express's (req, res)

scope-anchors: src/, index.ts
stop-conditions: Stop before modifying wrangler.toml

---

## AI / AGENTS

### Vercel AI SDK
use-cases: ai-app, saas
detect: "ai" in package.json (Vercel AI SDK), useChat or useCompletion in code

prompt-context:
- State SDK version (v3/v4 have different APIs)
- Note model provider in use (OpenAI, Anthropic, Google)
- Include relevant route handler or server action context
- Note streaming pattern (streamText, generateText, useChat)

pitfalls:
- Mixes v3 and v4 APIs (breaking changes between versions)
- Forgets to handle streaming response correctly in the UI
- Puts API keys in client components

scope-anchors: app/api/chat/, lib/ai.ts, components/chat/
stop-conditions: Stop before modifying .env or exposing API keys client-side

---

### LangChain.js / LangGraph
use-cases: ai-app
detect: "@langchain" in package.json

prompt-context:
- State LangChain version
- Note graph or chain structure relevant to the task
- Include relevant node/edge definitions for LangGraph

pitfalls:
- Uses deprecated LangChain v0.1 patterns in v0.2+
- Forgets to compile the graph before invoking
- Skips state schema definition in LangGraph

scope-anchors: src/agents/, src/chains/, src/graphs/
stop-conditions: Stop before modifying the graph's state schema

---

### Anthropic SDK
use-cases: ai-app
detect: "@anthropic-ai/sdk" in package.json

prompt-context:
- Note which Claude model is being called
- Include relevant message construction context
- State whether using streaming or non-streaming

pitfalls:
- Puts API key client-side
- Forgets to handle streaming with stream.on() or for-await
- Uses deprecated messages API patterns

scope-anchors: lib/anthropic.ts, app/api/, server/
stop-conditions: Stop before exposing ANTHROPIC_API_KEY client-side

---

## DATABASE / ORM

### Supabase
use-cases: webapp, saas, mobile, backend, auth
detect: "@supabase/supabase-js" or "@supabase/ssr" in package.json

prompt-context:
- State whether using supabase-js (client) or @supabase/ssr (server)
- Include relevant table names and RLS policy context
- Note auth setup (email, OAuth, magic link)
- Include supabase/migrations/ if schema changes are involved

pitfalls:
- Uses client-side Supabase for auth checks that should be server-side
- Disables RLS to make something work (security issue)
- Uses supabase-js instead of @supabase/ssr for Next.js App Router
- Forgets to handle auth session refresh in middleware

scope-anchors: lib/supabase.ts, supabase/migrations/, middleware.ts
stop-conditions:
- Stop before running supabase db push or any migration
- Stop before modifying RLS policies
- Stop before disabling RLS on any table

---

### Prisma
use-cases: webapp, saas, backend, fullstack
detect: prisma/schema.prisma present, "@prisma/client" in package.json

prompt-context:
- Include relevant model definitions from schema.prisma
- State database type (PostgreSQL, MySQL, SQLite)
- Note whether migration is needed after schema change

pitfalls:
- Modifies schema.prisma without noting that migration is required
- Calls prisma.X.Y() methods that don't exist on the detected models
- Forgets to run prisma generate after schema changes
- Uses Prisma in edge runtime (not supported)

scope-anchors: prisma/schema.prisma, lib/prisma.ts, prisma/migrations/
stop-conditions:
- Stop before running prisma migrate dev or prisma db push
- Stop before modifying prisma/schema.prisma

---

### Drizzle ORM
use-cases: webapp, saas, backend, edge
detect: "drizzle-orm" in package.json, drizzle.config.ts present

prompt-context:
- Include relevant schema file (db/schema.ts)
- State database driver (postgres.js, better-sqlite3, libsql)
- Note whether using Drizzle Kit for migrations

pitfalls:
- Mixes Drizzle v0.28 and v0.29+ APIs (significant changes)
- Forgets to import table definitions from schema when building queries
- Uses Prisma-style .findMany() instead of Drizzle's select().from()

scope-anchors: db/schema.ts, db/index.ts, drizzle.config.ts
stop-conditions:
- Stop before running drizzle-kit generate or push
- Stop before modifying db/schema.ts

---

## AUTH

### NextAuth v5 (Auth.js)
use-cases: webapp, saas
detect: "next-auth" version >= 5 in package.json, auth.ts at root

prompt-context:
- Confirm v5 (not v4 — APIs are completely different)
- Include auth.ts config context
- Note providers in use

pitfalls:
- Uses v4 session/jwt callbacks syntax in v5
- Forgets that v5 uses auth() instead of getServerSession()
- Misses the middleware.ts auth guard pattern for v5

scope-anchors: auth.ts, middleware.ts, app/api/auth/
stop-conditions: Stop before modifying auth.ts providers

---

### Clerk
use-cases: webapp, saas, mobile
detect: "@clerk/nextjs" or "@clerk/clerk-react" in package.json

prompt-context:
- Note which Clerk middleware/provider is in use
- State whether using App Router or Pages Router (different Clerk setup)
- Include clerkMiddleware config context

pitfalls:
- Uses old Clerk v4 patterns (authMiddleware is deprecated — use clerkMiddleware)
- Forgets to wrap app in ClerkProvider
- Puts auth checks in wrong context (client vs server)

scope-anchors: middleware.ts, app/layout.tsx (for ClerkProvider)
stop-conditions: Stop before modifying Clerk publishable keys or webhook config

---

## UI LIBRARIES

### Tailwind CSS 4
use-cases: webapp, saas, mobile, desktop, extension, backend
detect: "tailwindcss" >= 4 in package.json, @import "tailwindcss" in CSS

prompt-context:
- Confirm Tailwind v4 (CSS-first config, no tailwind.config.js)
- Note that v4 uses @theme in CSS instead of JS config
- State component library layered on top if any (shadcn, DaisyUI)

pitfalls:
- Generates tailwind.config.js (v3 pattern — not used in v4)
- Uses old arbitrary value syntax that changed in v4
- Adds plugins via JS config instead of CSS @plugin

scope-anchors: app/globals.css or src/index.css (where @import "tailwindcss" lives)
stop-conditions: Stop before modifying the CSS entry point

---

### shadcn/ui
use-cases: webapp, dashboard, saas
detect: components/ui/ directory present, "components.json" at root

prompt-context:
- Include components.json config (paths, style, rsc setting)
- Note which components are already installed (in components/ui/)
- State whether RSC mode is on or off

pitfalls:
- Generates component code from scratch instead of using `npx shadcn add`
- Modifies files in components/ui/ directly (they get overwritten by CLI)
- Forgets that shadcn components need to be added via CLI, not copy-paste

scope-anchors: components/ui/ (read-only reference), components/ (custom components)
stop-conditions:
- Stop before running npx shadcn add (confirm which component first)
- NEVER directly edit files in components/ui/

---

## DEPLOYMENT

### Vercel
use-cases: webapp, saas, edge
detect: vercel.json present, or Next.js project (Vercel is default)

prompt-context:
- Note if Edge Runtime is used (different from Node.js runtime)
- Include relevant vercel.json config if present
- State environment variables needed

pitfalls:
- Adds Node.js-only APIs to Edge Runtime functions
- Forgets to add new env vars to Vercel project settings
- Misses that Vercel Cron requires Pro plan

scope-anchors: vercel.json, .vercel/
stop-conditions: Stop before modifying vercel.json or environment variable names

---

### Cloudflare Workers
use-cases: backend, edge, extension
detect: wrangler.toml present, "wrangler" in package.json

prompt-context:
- Include wrangler.toml bindings (KV, D1, R2, Durable Objects)
- Note compatibility_date in wrangler.toml
- State whether using Hono, itty-router, or raw Workers API

pitfalls:
- Uses Node.js APIs not available in Workers runtime
- Forgets to declare bindings in wrangler.toml before using them in code
- Uses dynamic imports (not supported in Workers)

scope-anchors: src/index.ts, wrangler.toml
stop-conditions:
- Stop before modifying wrangler.toml bindings
- Stop before running wrangler deploy
