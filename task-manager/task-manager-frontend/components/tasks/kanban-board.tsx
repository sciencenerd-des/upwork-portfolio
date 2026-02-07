import { CalendarClock, CircleDot } from "lucide-react";
import { Project, Task, TaskStatus } from "@/types";

const statusOrder: TaskStatus[] = ["backlog", "in_progress", "review", "done"];

const statusConfig: Record<TaskStatus, { label: string; tone: string }> = {
  backlog: { label: "Backlog", tone: "tone-backlog" },
  in_progress: { label: "In Progress", tone: "tone-progress" },
  review: { label: "Review", tone: "tone-review" },
  done: { label: "Done", tone: "tone-done" }
};

const priorityTone: Record<Task["priority"], string> = {
  low: "priority-low",
  medium: "priority-medium",
  high: "priority-high"
};

interface KanbanBoardProps {
  projects: Project[];
  tasks: Task[];
  compact?: boolean;
}

export function KanbanBoard({ projects, tasks, compact = false }: KanbanBoardProps) {
  const projectById = Object.fromEntries(projects.map((project) => [project.id, project]));

  return (
    <div className="kanban-board" data-compact={compact}>
      {statusOrder.map((status) => {
        const columnTasks = tasks.filter((task) => task.status === status);

        return (
          <section key={status} className={`kanban-column ${statusConfig[status].tone}`}>
            <header className="section-header">
              <h3>{statusConfig[status].label}</h3>
              <span className="pill">{columnTasks.length}</span>
            </header>

            <div className="stack-sm">
              {columnTasks.length === 0 ? (
                <p className="muted">No tasks in this stage.</p>
              ) : (
                columnTasks.map((task) => {
                  const projectName = projectById[task.projectId]?.name ?? "Unknown project";

                  return (
                    <article key={task.id} className="kanban-card">
                      <div className="header-row">
                        <p>{task.title}</p>
                        <span className={`priority-chip ${priorityTone[task.priority]}`}>{task.priority}</span>
                      </div>
                      <p className="muted">{projectName}</p>
                      <div className="meta-row">
                        <span className="chip">
                          <CircleDot size={12} />
                          {task.assignee}
                        </span>
                        <span className="chip">
                          <CalendarClock size={12} />
                          {task.dueDate}
                        </span>
                      </div>
                    </article>
                  );
                })
              )}
            </div>
          </section>
        );
      })}
    </div>
  );
}
