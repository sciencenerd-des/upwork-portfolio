"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, Calendar } from "lucide-react";
import { formatRelativeDate, PRIORITY_COLORS } from "@/lib/utils";
import { Doc } from "@/convex/_generated/dataModel";

type TaskWithProject = Doc<"tasks"> & {
  project: { name: string; color: string } | null;
};

interface OverdueTasksProps {
  tasks: TaskWithProject[] | undefined;
}

export function OverdueTasks({ tasks }: OverdueTasksProps) {
  if (!tasks) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <AlertTriangle className="h-5 w-5 text-destructive" />
            Overdue Tasks
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-16 bg-muted animate-pulse rounded" />
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
          <AlertTriangle className="h-5 w-5 text-destructive" />
          Overdue Tasks
          {tasks.length > 0 && (
            <span className="ml-auto text-sm font-normal text-destructive">
              {tasks.length} overdue
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {tasks.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">
            No overdue tasks. Great job!
          </p>
        ) : (
          <div className="space-y-3">
            {tasks.slice(0, 5).map((task) => (
              <Link
                key={task._id}
                href={`/project/${task.projectId}`}
                className="flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors"
              >
                <div
                  className="w-1 h-10 rounded-full"
                  style={{
                    backgroundColor: PRIORITY_COLORS[task.priority],
                  }}
                />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{task.title}</p>
                  {task.project && (
                    <div className="flex items-center gap-2 mt-1">
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: task.project.color }}
                      />
                      <span className="text-xs text-muted-foreground">
                        {task.project.name}
                      </span>
                    </div>
                  )}
                </div>
                {task.dueDate && (
                  <div className="flex items-center gap-1 text-xs text-destructive">
                    <Calendar className="h-3 w-3" />
                    {formatRelativeDate(task.dueDate)}
                  </div>
                )}
              </Link>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
