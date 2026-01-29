"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Clock, CheckCircle2 } from "lucide-react";
import { PRIORITY_COLORS, PRIORITY_LABELS } from "@/lib/utils";
import { Doc } from "@/convex/_generated/dataModel";

type TaskWithProject = Doc<"tasks"> & {
  project: { name: string; color: string } | null;
};

interface DueTodayProps {
  tasks: TaskWithProject[] | undefined;
}

export function DueToday({ tasks }: DueTodayProps) {
  if (!tasks) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Clock className="h-5 w-5 text-amber-500" />
            Due Today
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
          <Clock className="h-5 w-5 text-amber-500" />
          Due Today
          {tasks.length > 0 && (
            <span className="ml-auto text-sm font-normal text-muted-foreground">
              {tasks.length} task{tasks.length !== 1 ? "s" : ""}
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {tasks.length === 0 ? (
          <div className="text-center py-4">
            <CheckCircle2 className="h-8 w-8 text-green-500 mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">
              No tasks due today. Enjoy your day!
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.map((task) => (
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
                <span
                  className="text-xs px-2 py-1 rounded-full"
                  style={{
                    backgroundColor: `${PRIORITY_COLORS[task.priority]}20`,
                    color: PRIORITY_COLORS[task.priority],
                  }}
                >
                  {PRIORITY_LABELS[task.priority]}
                </span>
              </Link>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
