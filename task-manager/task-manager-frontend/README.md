# Task Manager

A full-stack task management application with Kanban board, list view, and user authentication.

## Tech Stack

- **Frontend:** Next.js 14 (App Router) + Tailwind CSS + shadcn/ui
- **Backend:** Convex (real-time database + serverless functions)
- **Authentication:** WorkOS AuthKit SDK
- **Drag & Drop:** @dnd-kit

## Features

- User authentication (email/password + OAuth via WorkOS)
- Real-time data synchronization across tabs/devices
- Project management (create, edit, archive, delete)
- Task management with Kanban board and list view
- Drag-and-drop task reordering
- Task filtering by status and priority
- Dashboard with task summaries and overdue tasks

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Convex account (https://convex.dev)
- WorkOS account (https://workos.com)

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

Copy the example env file and fill in your credentials:

```bash
cp .env.local.example .env.local
```

Required variables:
- `NEXT_PUBLIC_CONVEX_URL` - From Convex dashboard
- `WORKOS_CLIENT_ID` - From WorkOS dashboard
- `WORKOS_API_KEY` - From WorkOS dashboard
- `WORKOS_COOKIE_PASSWORD` - 32+ character random string
- `NEXT_PUBLIC_WORKOS_REDIRECT_URI` - Your auth callback URL

### 3. Initialize Convex

```bash
npx convex dev
```

This will:
- Create your Convex project (if new)
- Deploy functions to Convex
- Generate TypeScript types

### 4. Configure WorkOS Webhooks

In your WorkOS Dashboard → Webhooks, add:
- **Endpoint:** `https://<your-convex-deployment>.convex.site/authkitEvent`
- **Events:** `user.created`, `user.updated`, `user.deleted`

### 5. Run Development Server

In two terminals:

```bash
# Terminal 1: Next.js frontend
npm run dev:frontend

# Terminal 2: Convex backend (if not already running)
npm run dev:backend
```

Or run both concurrently:

```bash
npm run dev
```

Visit http://localhost:3000

## Project Structure

```
├── app/                    # Next.js App Router
│   ├── (auth)/            # Auth pages (login, register)
│   ├── (dashboard)/       # Protected dashboard pages
│   └── callback/          # WorkOS auth callback
├── components/
│   ├── ui/                # shadcn/ui components
│   ├── layout/            # Header, Sidebar
│   ├── projects/          # Project components
│   ├── tasks/             # Task & Kanban components
│   └── dashboard/         # Dashboard widgets
├── convex/                # Convex backend
│   ├── schema.ts          # Database schema
│   ├── auth.ts            # User sync events
│   ├── users.ts           # User queries/mutations
│   ├── projects.ts        # Project CRUD
│   ├── tasks.ts           # Task CRUD
│   └── dashboard.ts       # Dashboard aggregations
├── lib/                   # Utilities
├── providers/             # React context providers
└── middleware.ts          # Auth middleware
```

## Deployment

### Frontend (Vercel)

1. Push to GitHub
2. Import to Vercel
3. Add environment variables
4. Deploy

### Backend (Convex)

```bash
npx convex deploy
```

## License

MIT
