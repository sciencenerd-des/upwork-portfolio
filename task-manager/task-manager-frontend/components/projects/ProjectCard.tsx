"use client";

import Link from "next/link";
import { Doc } from "@/convex/_generated/dataModel";
import { FolderKanban, MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { useMutation } from "convex/react";
import { api } from "@/convex/_generated/api";
import { useState } from "react";
import { EditProjectDialog } from "./EditProjectDialog";

interface ProjectCardProps {
  project: Doc<"projects"> & {
    taskCount: number;
    completedCount: number;
  };
}

export function ProjectCard({ project }: ProjectCardProps) {
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const removeProject = useMutation(api.projects.remove);

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this project? All tasks will be deleted.")) {
      return;
    }
    setIsDeleting(true);
    try {
      await removeProject({ projectId: project._id });
    } catch (error) {
      console.error("Failed to delete project:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  const progress =
    project.taskCount > 0
      ? Math.round((project.completedCount / project.taskCount) * 100)
      : 0;

  return (
    <>
      <div className="relative group">
        <Link
          href={`/project/${project._id}`}
          className="block p-4 bg-card rounded-lg border hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-3">
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: `${project.color}20` }}
              >
                <FolderKanban
                  className="w-5 h-5"
                  style={{ color: project.color }}
                />
              </div>
              <div>
                <h3 className="font-medium text-slate-900 line-clamp-1">
                  {project.name}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {project.taskCount} tasks
                </p>
              </div>
            </div>
          </div>

          {project.description && (
            <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
              {project.description}
            </p>
          )}

          {/* Progress bar */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Progress</span>
              <span>{progress}%</span>
            </div>
            <div className="h-1.5 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-300"
                style={{
                  width: `${progress}%`,
                  backgroundColor: project.color,
                }}
              />
            </div>
          </div>
        </Link>

        {/* Actions dropdown */}
        <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setShowEditDialog(true)}>
                <Pencil className="mr-2 h-4 w-4" />
                Edit
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={handleDelete}
                disabled={isDeleting}
                className="text-destructive focus:text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                {isDeleting ? "Deleting..." : "Delete"}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <EditProjectDialog
        project={project}
        open={showEditDialog}
        onOpenChange={setShowEditDialog}
      />
    </>
  );
}
