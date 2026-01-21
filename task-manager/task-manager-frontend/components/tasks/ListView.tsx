"use client";

import { useQuery, useMutation } from "convex/react";
import { api } from "@/convex/_generated/api";
import { Id, Doc } from "@/convex/_generated/dataModel";
import {
  Calendar,
  ChevronDown,
  MoreHorizontal,
  Pencil,
  Trash2,
  Plus,
} from "lucide-react";
import {
  formatRelativeDate,
  isOverdue,
  PRIORITY_COLORS,
  PRIORITY_LABELS,
  STATUS_LABELS,
} from "@/lib/utils";
import { cn } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { CreateTaskDialog } from "./CreateTaskDialog";
import { EditTaskDialog } from "./EditTaskDialog";

type SortField = "title" | "status" | "priority" | "dueDate";
type SortDirection = "asc" | "desc";

interface ListViewProps {
  projectId: Id<"projects">;
}

export function ListView({ projectId }: ListViewProps) {
  const tasks = useQuery(api.tasks.listByProject, { projectId });
  const removeTask = useMutation(api.tasks.remove);
  const updateTaskStatus = useMutation(api.tasks.updateStatus);

  const [sortField, setSortField] = useState<SortField>("status");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");
  const [showCreateTask, setShowCreateTask] = useState(false);
  const [editingTask, setEditingTask] = useState<Doc<"tasks"> | null>(null);

  if (!tasks) {
    return (
      <div className="border rounded-lg">
        <div className="h-12 bg-muted/50 border-b" />
        <div className="space-y-2 p-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-12 bg-muted animate-pulse rounded" />
          ))}
        </div>
      </div>
    );
  }

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const sortedTasks = [...tasks].sort((a, b) => {
    let comparison = 0;

    switch (sortField) {
      case "title":
        comparison = a.title.localeCompare(b.title);
        break;
      case "status":
        const statusOrder = { todo: 0, in_progress: 1, done: 2 };
        comparison = statusOrder[a.status] - statusOrder[b.status];
        break;
      case "priority":
        const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 };
        comparison = priorityOrder[a.priority] - priorityOrder[b.priority];
        break;
      case "dueDate":
        const aDate = a.dueDate ?? Infinity;
        const bDate = b.dueDate ?? Infinity;
        comparison = aDate - bDate;
        break;
    }

    return sortDirection === "asc" ? comparison : -comparison;
  });

  const handleDelete = async (taskId: Id<"tasks">) => {
    if (!confirm("Are you sure you want to delete this task?")) return;
    try {
      await removeTask({ taskId });
    } catch (error) {
      console.error("Failed to delete task:", error);
    }
  };

  const handleStatusChange = async (
    task: Doc<"tasks">,
    newStatus: "todo" | "in_progress" | "done"
  ) => {
    try {
      await updateTaskStatus({
        taskId: task._id,
        status: newStatus,
        position: task.position,
      });
    } catch (error) {
      console.error("Failed to update task status:", error);
    }
  };

  const SortHeader = ({
    field,
    children,
  }: {
    field: SortField;
    children: React.ReactNode;
  }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center gap-1 hover:text-foreground transition-colors"
    >
      {children}
      {sortField === field && (
        <ChevronDown
          className={cn(
            "w-4 h-4 transition-transform",
            sortDirection === "desc" && "rotate-180"
          )}
        />
      )}
    </button>
  );

  return (
    <>
      <div className="border rounded-lg overflow-hidden">
        {/* Header */}
        <div className="grid grid-cols-[1fr_120px_100px_120px_40px] gap-4 px-4 py-3 bg-muted/50 border-b text-sm font-medium text-muted-foreground">
          <SortHeader field="title">Title</SortHeader>
          <SortHeader field="status">Status</SortHeader>
          <SortHeader field="priority">Priority</SortHeader>
          <SortHeader field="dueDate">Due Date</SortHeader>
          <span />
        </div>

        {/* Rows */}
        {sortedTasks.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            <p className="mb-4">No tasks yet. Add your first task!</p>
            <Button onClick={() => setShowCreateTask(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Task
            </Button>
          </div>
        ) : (
          <div className="divide-y">
            {sortedTasks.map((task) => {
              const overdue = isOverdue(task.dueDate);

              return (
                <div
                  key={task._id}
                  className="grid grid-cols-[1fr_120px_100px_120px_40px] gap-4 px-4 py-3 items-center hover:bg-muted/30 transition-colors"
                >
                  {/* Title */}
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className="w-1 h-8 rounded-full flex-shrink-0"
                      style={{
                        backgroundColor: PRIORITY_COLORS[task.priority],
                      }}
                    />
                    <div className="min-w-0">
                      <p className="font-medium text-sm truncate">
                        {task.title}
                      </p>
                      {task.description && (
                        <p className="text-xs text-muted-foreground truncate">
                          {task.description}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Status */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 px-2 justify-start"
                      >
                        <div
                          className={cn(
                            "w-2 h-2 rounded-full mr-2",
                            task.status === "todo" && "bg-slate-500",
                            task.status === "in_progress" && "bg-amber-500",
                            task.status === "done" && "bg-green-500"
                          )}
                        />
                        <span className="text-xs">
                          {STATUS_LABELS[task.status]}
                        </span>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="start">
                      <DropdownMenuItem
                        onClick={() => handleStatusChange(task, "todo")}
                      >
                        <div className="w-2 h-2 rounded-full bg-slate-500 mr-2" />
                        To Do
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => handleStatusChange(task, "in_progress")}
                      >
                        <div className="w-2 h-2 rounded-full bg-amber-500 mr-2" />
                        In Progress
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => handleStatusChange(task, "done")}
                      >
                        <div className="w-2 h-2 rounded-full bg-green-500 mr-2" />
                        Done
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>

                  {/* Priority */}
                  <span
                    className="text-xs px-2 py-1 rounded-full w-fit"
                    style={{
                      backgroundColor: `${PRIORITY_COLORS[task.priority]}20`,
                      color: PRIORITY_COLORS[task.priority],
                    }}
                  >
                    {PRIORITY_LABELS[task.priority]}
                  </span>

                  {/* Due Date */}
                  {task.dueDate ? (
                    <div
                      className={cn(
                        "flex items-center gap-1 text-xs",
                        overdue && task.status !== "done"
                          ? "text-destructive"
                          : "text-muted-foreground"
                      )}
                    >
                      <Calendar className="w-3 h-3" />
                      {formatRelativeDate(task.dueDate)}
                    </div>
                  ) : (
                    <span className="text-xs text-muted-foreground">—</span>
                  )}

                  {/* Actions */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => setEditingTask(task)}>
                        <Pencil className="mr-2 h-4 w-4" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={() => handleDelete(task._id)}
                        className="text-destructive focus:text-destructive"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              );
            })}
          </div>
        )}

        {/* Add Task Button */}
        {sortedTasks.length > 0 && (
          <div className="px-4 py-3 border-t">
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start text-muted-foreground"
              onClick={() => setShowCreateTask(true)}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Task
            </Button>
          </div>
        )}
      </div>

      <CreateTaskDialog
        projectId={projectId}
        defaultStatus="todo"
        open={showCreateTask}
        onOpenChange={setShowCreateTask}
      />

      {editingTask && (
        <EditTaskDialog
          task={editingTask}
          open={!!editingTask}
          onOpenChange={(open) => !open && setEditingTask(null)}
        />
      )}
    </>
  );
}
