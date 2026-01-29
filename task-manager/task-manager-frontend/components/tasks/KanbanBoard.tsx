"use client";

import { useQuery, useMutation } from "convex/react";
import { api } from "@/convex/_generated/api";
import { Id, Doc } from "@/convex/_generated/dataModel";
import {
  DndContext,
  DragEndEvent,
  DragOverEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
} from "@dnd-kit/core";
import { useState } from "react";
import { KanbanColumn } from "./KanbanColumn";
import { TaskCard } from "./TaskCard";
import { CreateTaskDialog } from "./CreateTaskDialog";

type TaskStatus = "todo" | "in_progress" | "done";

interface KanbanBoardProps {
  projectId: Id<"projects">;
}

export function KanbanBoard({ projectId }: KanbanBoardProps) {
  const tasks = useQuery(api.tasks.listByProject, { projectId });
  const updateTaskStatus = useMutation(api.tasks.updateStatus);
  const [activeTask, setActiveTask] = useState<Doc<"tasks"> | null>(null);
  const [showCreateTask, setShowCreateTask] = useState(false);
  const [createInStatus, setCreateInStatus] = useState<TaskStatus>("todo");

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  const columns: { id: TaskStatus; title: string }[] = [
    { id: "todo", title: "To Do" },
    { id: "in_progress", title: "In Progress" },
    { id: "done", title: "Done" },
  ];

  const getTasksByStatus = (status: TaskStatus) => {
    if (!tasks) return [];
    return tasks.filter((task) => task.status === status);
  };

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const task = tasks?.find((t) => t._id === active.id);
    if (task) {
      setActiveTask(task);
    }
  };

  const handleDragOver = (_event: DragOverEvent) => {
    // Handle drag over if needed for visual feedback
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveTask(null);

    if (!over) return;

    const taskId = active.id as Id<"tasks">;
    const overId = over.id as string;

    // Determine the target status
    let newStatus: TaskStatus;
    if (columns.some((col) => col.id === overId)) {
      // Dropped on a column
      newStatus = overId as TaskStatus;
    } else {
      // Dropped on another task, get that task's status
      const overTask = tasks?.find((t) => t._id === overId);
      if (!overTask) return;
      newStatus = overTask.status;
    }

    const currentTask = tasks?.find((t) => t._id === taskId);
    if (!currentTask || currentTask.status === newStatus) return;

    // Calculate new position
    const tasksInColumn = getTasksByStatus(newStatus);
    const newPosition = tasksInColumn.length;

    try {
      await updateTaskStatus({
        taskId,
        status: newStatus,
        position: newPosition,
      });
    } catch (error) {
      console.error("Failed to update task status:", error);
    }
  };

  const handleAddTask = (status: TaskStatus) => {
    setCreateInStatus(status);
    setShowCreateTask(true);
  };

  if (!tasks) {
    return (
      <div className="flex gap-4 overflow-x-auto pb-4">
        {columns.map((column) => (
          <div
            key={column.id}
            className="flex-shrink-0 w-80 bg-muted/50 rounded-lg p-4"
          >
            <div className="h-8 w-24 bg-muted animate-pulse rounded mb-4" />
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="h-24 bg-muted animate-pulse rounded-lg"
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        <div className="flex gap-4 overflow-x-auto pb-4">
          {columns.map((column) => (
            <KanbanColumn
              key={column.id}
              id={column.id}
              title={column.title}
              tasks={getTasksByStatus(column.id)}
              onAddTask={() => handleAddTask(column.id)}
            />
          ))}
        </div>

        <DragOverlay>
          {activeTask && <TaskCard task={activeTask} isDragging />}
        </DragOverlay>
      </DndContext>

      <CreateTaskDialog
        projectId={projectId}
        defaultStatus={createInStatus}
        open={showCreateTask}
        onOpenChange={setShowCreateTask}
      />
    </>
  );
}
