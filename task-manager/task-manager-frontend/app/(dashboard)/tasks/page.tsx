import { TaskList } from "@/components/tasks/task-list";
import { getTasksData } from "@/lib/api";

export default async function TasksPage() {
  const { projects, tasks } = await getTasksData();

  return (
    <section className="stack-lg animate-fade-in">
      <header className="card hero-card">
        <span className="pill">Tasks</span>
        <h1 className="title-lg">Detailed task registry</h1>
        <p className="muted">Priorities, due dates, and ownership in one clean list view.</p>
      </header>
      <article className="card">
        <TaskList projects={projects} tasks={tasks} />
      </article>
    </section>
  );
}
