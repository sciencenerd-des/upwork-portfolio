"use client";

import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { Id } from "@/convex/_generated/dataModel";
import { useParams } from "next/navigation";
import { KanbanBoard } from "@/components/tasks/KanbanBoard";
import { ListView } from "@/components/tasks/ListView";
import { Button } from "@/components/ui/button";
import { KanbanSquare, List, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { cn } from "@/lib/utils";

type ViewMode = "kanban" | "list";

export default function ProjectPage() {
  const params = useParams();
  const projectId = params.id as Id<"projects">;
  const project = useQuery(api.projects.getById, { projectId });
  const [viewMode, setViewMode] = useState<ViewMode>("kanban");

  if (project === undefined) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-64 bg-muted animate-pulse rounded" />
        <div className="h-[600px] bg-muted/50 animate-pulse rounded-lg" />
      </div>
    );
  }

  if (project === null) {
    return (
      <div className="text-center py-20">
        <h1 className="text-2xl font-bold text-slate-900 mb-2">
          Project not found
        </h1>
        <p className="text-slate-600 mb-4">
          This project may have been deleted or you don&apos;t have access.
        </p>
        <Button asChild>
          <Link href="/dashboard">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/dashboard"
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex items-center gap-3">
            <div
              className="w-4 h-4 rounded-full"
              style={{ backgroundColor: project.color }}
            />
            <h1 className="text-2xl font-bold text-slate-900">
              {project.name}
            </h1>
          </div>
          {project.description && (
            <span className="text-muted-foreground hidden sm:inline">
              — {project.description}
            </span>
          )}
        </div>

        {/* View Toggle */}
        <div className="flex items-center gap-1 bg-muted p-1 rounded-lg">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setViewMode("kanban")}
            className={cn(
              "h-8",
              viewMode === "kanban" && "bg-background shadow-sm"
            )}
          >
            <KanbanSquare className="w-4 h-4 mr-2" />
            Kanban
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setViewMode("list")}
            className={cn(
              "h-8",
              viewMode === "list" && "bg-background shadow-sm"
            )}
          >
            <List className="w-4 h-4 mr-2" />
            List
          </Button>
        </div>
      </div>

      {/* Task Stats */}
      <div className="flex items-center gap-4 text-sm text-muted-foreground">
        <span>{project.taskCount} total tasks</span>
        <span>•</span>
        <span>{project.completedCount} completed</span>
        {project.taskCount > 0 && (
          <>
            <span>•</span>
            <span>
              {Math.round((project.completedCount / project.taskCount) * 100)}%
              done
            </span>
          </>
        )}
      </div>

      {/* Content */}
      {viewMode === "kanban" ? (
        <KanbanBoard projectId={projectId} />
      ) : (
        <ListView projectId={projectId} />
      )}
    </div>
  );
}
