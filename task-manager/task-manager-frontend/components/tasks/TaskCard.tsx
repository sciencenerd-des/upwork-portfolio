"use client";

import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Doc } from "@/convex/_generated/dataModel";
import { Calendar, MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import {
  formatRelativeDate,
  isOverdue,
  PRIORITY_COLORS,
  PRIORITY_LABELS,
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
import { useMutation } from "convex/react";
import { api } from "@/convex/_generated/api";
import { useState } from "react";
import { EditTaskDialog } from "./EditTaskDialog";

interface TaskCardProps {
  task: Doc<"tasks">;
  isDragging?: boolean;
}

export function TaskCard({ task, isDragging }: TaskCardProps) {
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const removeTask = useMutation(api.tasks.remove);

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({
    id: task._id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this task?")) {
      return;
    }
    setIsDeleting(true);
    try {
      await removeTask({ taskId: task._id });
    } catch (error) {
      console.error("Failed to delete task:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  const overdue = isOverdue(task.dueDate);

  return (
    <>
      <div
        ref={setNodeRef}
        style={style}
        {...attributes}
        {...listeners}
        className={cn(
          "bg-card border rounded-lg p-3 cursor-grab active:cursor-grabbing hover:shadow-sm transition-shadow group",
          (isDragging || isSortableDragging) && "opacity-50 shadow-lg",
          overdue && task.status !== "done" && "border-destructive/50"
        )}
      >
        {/* Priority indicator */}
        <div className="flex items-start gap-2 mb-2">
          <div
            className="w-1 h-full min-h-[40px] rounded-full flex-shrink-0"
            style={{ backgroundColor: PRIORITY_COLORS[task.priority] }}
          />
          <div className="flex-1 min-w-0">
            <p className="font-medium text-sm line-clamp-2">{task.title}</p>
            {task.description && (
              <p className="text-xs text-muted-foreground line-clamp-1 mt-1">
                {task.description}
              </p>
            )}
          </div>
          {/* Actions */}
          <div className="opacity-0 group-hover:opacity-100 transition-opacity">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={(e) => e.stopPropagation()}
                >
                  <MoreHorizontal className="h-3 w-3" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowEditDialog(true);
                  }}
                >
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

        {/* Footer */}
        <div className="flex items-center justify-between mt-2">
          <span
            className="text-xs px-2 py-0.5 rounded-full"
            style={{
              backgroundColor: `${PRIORITY_COLORS[task.priority]}20`,
              color: PRIORITY_COLORS[task.priority],
            }}
          >
            {PRIORITY_LABELS[task.priority]}
          </span>

          {task.dueDate && (
            <div
              className={cn(
                "flex items-center gap-1 text-xs",
                overdue && task.status !== "done"
                  ? "text-destructive"
                  : "text-muted-foreground"
              )}
            >
              <Calendar className="h-3 w-3" />
              {formatRelativeDate(task.dueDate)}
            </div>
          )}
        </div>
      </div>

      <EditTaskDialog
        task={task}
        open={showEditDialog}
        onOpenChange={setShowEditDialog}
      />
    </>
  );
}
