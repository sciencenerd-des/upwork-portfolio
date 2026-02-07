# Task Manager Frontend

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?logo=vercel)](https://task-manager-frontend.vercel.app)

A polished project and task management UI with Kanban, list workflows, and real-time collaboration patterns.

## Value Proposition

**Notion-level polish for task management.**

Designed for teams that need visual clarity, fast capture, and clean execution views without enterprise-level setup overhead.

## Screenshot Gallery

| Dashboard | Kanban Board |
|---|---|
| ![Dashboard](https://placehold.co/1200x700/0f172a/ffffff?text=Dashboard+Overview+with+KPIs) | ![Kanban](https://placehold.co/1200x700/1d4ed8/ffffff?text=Drag-and-Drop+Kanban+Board) |

| Task Detail | Project View | Responsive Mobile |
|---|---|---|
| ![Task Detail](https://placehold.co/1200x700/047857/ffffff?text=Task+Detail+Drawer) | ![Project View](https://placehold.co/1200x700/7c2d12/ffffff?text=Project+Timeline+and+Filters) | ![Mobile](https://placehold.co/1200x700/7e22ce/ffffff?text=Mobile-Optimized+Task+Experience) |

## Demo Mode (No WorkOS Setup)

If you want to evaluate the product without configuring WorkOS:

1. Open the Vercel demo deployment: `https://task-manager-frontend.vercel.app`
2. Use demo workspace access (read-only seeded project/task data)
3. Explore dashboard, Kanban, filters, and task detail flows

This is the fastest path for recruiters/clients to review UX and interaction quality.

### Suggested Demo Tour

1. Open dashboard and review project/task summary cards
2. Switch to Kanban and drag a task across columns
3. Open a task detail panel and inspect due date/priority metadata

## Features

- Kanban + list task workflows
- Task priority/status/due date management
- Project-level organization and filtering
- Dashboard summaries and overdue views
- Real-time sync architecture via Convex
- WorkOS-based auth flow for production mode

## Clear Local Setup

### 1. Prerequisites

- Node.js 18+
- npm
- Convex account
- WorkOS account

### 2. Install

```bash
git clone https://github.com/sciencenerd-des/upwork-portfolio.git
cd upwork-portfolio/task-manager/task-manager-frontend
npm install
```

### 3. Configure Environment

Create `.env.local` with:

```bash
NEXT_PUBLIC_CONVEX_URL=your_convex_url
WORKOS_CLIENT_ID=your_workos_client_id
WORKOS_API_KEY=your_workos_api_key
WORKOS_COOKIE_PASSWORD=32_plus_char_secret
NEXT_PUBLIC_WORKOS_REDIRECT_URI=http://localhost:3000/callback
```

### 4. Start Development

```bash
npm run dev
```

If you run frontend/backend separately:

```bash
npm run dev:frontend
npm run dev:backend
```

Open `http://localhost:3000`.

## Deployment (Vercel)

1. Push repo to GitHub
2. Import `task-manager/task-manager-frontend` into Vercel
3. Set all required environment variables
4. Deploy and verify auth callback + task CRUD flows

## Architecture Overview

```text
┌─────────────────────────────┐
│ Next.js App Router Frontend │
│ - dashboard, projects, tasks│
└──────────────┬──────────────┘
               │
               v
┌─────────────────────────────┐
│ UI Layer                    │
│ - shadcn/ui                 │
│ - Tailwind styling          │
│ - dnd-kit interactions      │
└──────────────┬──────────────┘
               │
               v
┌─────────────────────────────┐
│ Data + Auth Clients         │
│ lib/api.ts, lib/auth.ts     │
│ Convex SDK + WorkOS AuthKit │
└──────────────┬──────────────┘
               │
               v
┌─────────────────────────────┐
│ Backend Services            │
│ Convex functions / API      │
│ (or FastAPI in full stack)  │
└─────────────────────────────┘
```

## Project Structure

```text
task-manager-frontend/
├── app/
│   ├── (auth)/
│   ├── (dashboard)/
│   ├── layout.tsx
│   └── globals.css
├── components/
│   ├── dashboard/
│   ├── layout/
│   ├── projects/
│   ├── tasks/
│   └── ui/
├── hooks/
├── lib/
├── types/
└── package.json
```

## License

MIT
