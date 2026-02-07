import { Clock3, Flag, Layers3 } from "lucide-react";
import { Project, Task } from "@/types";

const prioritySort: Record<Task["priority"], number> = {
  high: 0,
  medium: 1,
  low: 2
};

interface TaskListProps {
  projects: Project[];
  tasks: Task[];
  compact?: boolean;
}

export function TaskList({ projects, tasks, compact = false }: TaskListProps) {
  const projectById = Object.fromEntries(projects.map((project) => [project.id, project.name]));
  const orderedTasks = [...tasks].sort((a, b) => prioritySort[a.priority] - prioritySort[b.priority]);
  const visibleTasks = compact ? orderedTasks.slice(0, 6) : orderedTasks;

  return (
    <div className="task-list">
      {visibleTasks.map((task) => (
        <article key={task.id} className="task-row">
          <div>
            <h3>{task.title}</h3>
            <p className="muted">{task.description}</p>
          </div>
          <div className="meta-row">
            <span className="chip">
              <Layers3 size={12} />
              {projectById[task.projectId] ?? "Unknown project"}
            </span>
            <span className="chip">
              <Flag size={12} />
              {task.priority}
            </span>
            <span className="chip">
              <Clock3 size={12} />
              {task.dueDate}
            </span>
          </div>
        </article>
      ))}
    </div>
  );
}
