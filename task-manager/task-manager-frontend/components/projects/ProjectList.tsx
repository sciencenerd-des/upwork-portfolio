"use client";

import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { ProjectCard } from "./ProjectCard";
import { CreateProjectDialog } from "./CreateProjectDialog";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { useState } from "react";

export function ProjectList() {
  const projects = useQuery(api.projects.list, { status: "active" });
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  if (projects === undefined) {
    return (
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="h-32 bg-muted animate-pulse rounded-lg"
          />
        ))}
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="text-center py-12 bg-muted/30 rounded-lg border border-dashed">
        <h3 className="text-lg font-medium text-slate-900 mb-2">
          No projects yet
        </h3>
        <p className="text-slate-600 mb-4">
          Create your first project to start organizing tasks.
        </p>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Project
        </Button>
        <CreateProjectDialog
          open={showCreateDialog}
          onOpenChange={setShowCreateDialog}
        />
      </div>
    );
  }

  return (
    <>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.map((project) => (
          <ProjectCard key={project._id} project={project} />
        ))}
        <button
          onClick={() => setShowCreateDialog(true)}
          className="h-32 flex items-center justify-center border-2 border-dashed border-muted-foreground/25 rounded-lg hover:border-primary hover:bg-muted/50 transition-colors group"
        >
          <div className="text-center">
            <Plus className="w-8 h-8 mx-auto text-muted-foreground group-hover:text-primary transition-colors" />
            <span className="text-sm text-muted-foreground group-hover:text-primary transition-colors">
              New Project
            </span>
          </div>
        </button>
      </div>
      <CreateProjectDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
      />
    </>
  );
}
