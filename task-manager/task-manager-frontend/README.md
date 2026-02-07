# Task Manager Frontend

Enterprise-grade task management UI with a friendly, modern surface.

**Value prop:** Notion-level polish for task management.

## Live Demo

- Preview URL: https://skill-deploy-x7ee1dkq31-codex-agent-deploys.vercel.app

## What is Included

- Next.js App Router frontend with polished dashboard flows.
- Required Convex function modules:
  - `convex/projects.ts`
  - `convex/tasks.ts`
  - `convex/auth.ts`
  - `convex/dashboard.ts`
- Views for:
  - Dashboard (`/dashboard`)
  - Kanban board (`/kanban`)
  - Task list (`/tasks`)
  - Project view (`/project/p_orion`)
- Enterprise + friendly UI mix:
  - Navy + indigo core palette with warm accents.
  - Rounded cards, subtle gradients, smooth transitions.
  - Loading states via route loading skeletons.

## Demo Mode (No Full WorkOS Setup Required)

Demo mode is enabled by default so the portfolio can run without full auth wiring.

1. Copy `.env.example` to `.env.local`.
2. Keep `NEXT_PUBLIC_DEMO_MODE=true`.
3. Use placeholder WorkOS values for UI-only demo:
   - `NEXT_PUBLIC_WORKOS_CLIENT_ID=demo_workos_client_id`
   - `WORKOS_CLIENT_ID=demo_workos_client_id`
   - `WORKOS_API_KEY=demo_workos_api_key`
   - `WORKOS_REDIRECT_URI=http://localhost:3000/auth/callback`

When demo mode is enabled, sample projects/tasks are loaded and a `DemoMode` badge is shown in the app shell and auth pages.

## Screenshots

Captured files:

- `output/playwright/dashboard.png`
- `output/playwright/kanban.png`
- `output/playwright/task-list.png`
- `output/playwright/project-view.png`

## Local Development

```bash
npm install
npm run dev
```

Production build:

```bash
npm run build
npm run start
```
