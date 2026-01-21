"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity } from "lucide-react";
import { PRIORITY_COLORS, STATUS_LABELS } from "@/lib/utils";
import { Doc } from "@/convex/_generated/dataModel";

type TaskWithProject = Doc<"tasks"> & {
  project: { name: string; color: string } | null;
};

interface RecentTasksProps {
  tasks: TaskWithProject[] | undefined;
}

export function RecentTasks({ tasks }: RecentTasksProps) {
  if (!tasks) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Activity className="h-5 w-5 text-primary" />
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-muted animate-pulse rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Activity className="h-5 w-5 text-primary" />
          Recent Activity
        </CardTitle>
      </CardHeader>
      <CardContent>
        {tasks.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">
            No recent activity. Create a task to get started!
          </p>
        ) : (
          <div className="space-y-2">
            {tasks.map((task) => (
              <Link
                key={task._id}
                href={`/project/${task.projectId}`}
                className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div
                  className="w-1 h-8 rounded-full"
                  style={{
                    backgroundColor: PRIORITY_COLORS[task.priority],
                  }}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate">{task.title}</p>
                </div>
                {task.project && (
                  <div className="flex items-center gap-1">
                    <div
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: task.project.color }}
                    />
                    <span className="text-xs text-muted-foreground hidden sm:inline">
                      {task.project.name}
                    </span>
                  </div>
                )}
                <span className="text-xs text-muted-foreground">
                  {STATUS_LABELS[task.status]}
                </span>
              </Link>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
