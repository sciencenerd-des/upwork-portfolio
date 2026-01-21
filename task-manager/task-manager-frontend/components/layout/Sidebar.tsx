"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import {
  LayoutDashboard,
  FolderKanban,
  Settings,
  Plus,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { CreateProjectDialog } from "@/components/projects/CreateProjectDialog";
import { useState } from "react";

export function Sidebar() {
  const pathname = usePathname();
  const projects = useQuery(api.projects.list, { status: "active" });
  const [showCreateProject, setShowCreateProject] = useState(false);

  const navItems = [
    {
      label: "Dashboard",
      href: "/dashboard",
      icon: LayoutDashboard,
    },
    {
      label: "Settings",
      href: "/settings",
      icon: Settings,
    },
  ];

  return (
    <>
      <aside className="hidden lg:flex flex-col w-64 border-r bg-muted/30 min-h-[calc(100vh-3.5rem)]">
        <nav className="flex-1 p-4 space-y-2">
          {/* Main navigation */}
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                pathname === item.href
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}

          {/* Projects section */}
          <div className="pt-4">
            <div className="flex items-center justify-between px-3 mb-2">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Projects
              </span>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={() => setShowCreateProject(true)}
              >
                <Plus className="h-4 w-4" />
                <span className="sr-only">New project</span>
              </Button>
            </div>

            <div className="space-y-1">
              {projects === undefined ? (
                <div className="px-3 py-2">
                  <div className="h-4 w-24 bg-muted animate-pulse rounded" />
                </div>
              ) : projects.length === 0 ? (
                <div className="px-3 py-2 text-sm text-muted-foreground">
                  No projects yet
                </div>
              ) : (
                projects.map((project) => (
                  <Link
                    key={project._id}
                    href={`/project/${project._id}`}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors group",
                      pathname === `/project/${project._id}`
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:text-foreground hover:bg-muted"
                    )}
                  >
                    <div
                      className="w-3 h-3 rounded-full flex-shrink-0"
                      style={{ backgroundColor: project.color }}
                    />
                    <span className="flex-1 truncate">{project.name}</span>
                    <span
                      className={cn(
                        "text-xs",
                        pathname === `/project/${project._id}`
                          ? "text-primary-foreground/70"
                          : "text-muted-foreground"
                      )}
                    >
                      {project.taskCount}
                    </span>
                    <ChevronRight
                      className={cn(
                        "h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity",
                        pathname === `/project/${project._id}`
                          ? "text-primary-foreground"
                          : "text-muted-foreground"
                      )}
                    />
                  </Link>
                ))
              )}
            </div>
          </div>
        </nav>
      </aside>

      <CreateProjectDialog
        open={showCreateProject}
        onOpenChange={setShowCreateProject}
      />
    </>
  );
}
