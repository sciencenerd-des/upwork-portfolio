"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { KanbanSquare, LayoutDashboard, ListChecks, Settings, Sparkles } from "lucide-react";
import { DemoModeBadge } from "@/components/ui/demo-badge";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/kanban", label: "Kanban", icon: KanbanSquare },
  { href: "/tasks", label: "Tasks", icon: ListChecks },
  { href: "/settings", label: "Settings", icon: Settings }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="app-shell animate-fade-in">
      <aside className="sidebar card">
        <div className="stack-sm">
          <span className="pill warm">Task Manager</span>
          <h1 className="sidebar-title">Northstar PM</h1>
          <p className="muted">Enterprise precision, friendly execution.</p>
        </div>

        <nav className="nav-stack" aria-label="Primary">
          {navItems.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href || (href === "/dashboard" && pathname.startsWith("/project/"));

            return (
              <Link key={href} href={href} className={cn("nav-link", isActive && "active")}>
                <Icon size={16} />
                <span>{label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="card sidebar-note">
          <p className="muted">Focus area</p>
          <p>Polished planning workflows for team velocity.</p>
        </div>
      </aside>

      <div className="main-panel">
        <header className="topbar card">
          <div className="header-row">
            <div>
              <h2>Program workspace</h2>
              <p className="muted">Cross-functional delivery command center</p>
            </div>
            <div className="meta-row">
              <DemoModeBadge />
              <span className="chip">
                <Sparkles size={14} />
                Live portfolio build
              </span>
            </div>
          </div>
        </header>
        <main className="content-area">{children}</main>
      </div>
    </div>
  );
}
