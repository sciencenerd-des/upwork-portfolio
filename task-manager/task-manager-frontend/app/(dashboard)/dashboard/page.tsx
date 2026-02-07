import { SummaryCards } from "@/components/dashboard/summary-cards";
import { ProjectGrid } from "@/components/projects/project-grid";
import { KanbanBoard } from "@/components/tasks/kanban-board";
import { TaskList } from "@/components/tasks/task-list";
import { getDashboardData } from "@/lib/api";

export default async function DashboardPage() {
  const { summary, projects, tasks } = await getDashboardData();

  return (
    <section className="stack-lg animate-fade-in">
      <header className="card hero-card">
        <div>
          <span className="pill">Dashboard</span>
          <h1 className="title-lg">Executive workspace overview</h1>
          <p className="muted">Track delivery health, unblock risks, and keep teams aligned across active initiatives.</p>
        </div>
      </header>

      <SummaryCards summary={summary} />

      <section className="stack-md">
        <div className="section-header">
          <h2>Active projects</h2>
        </div>
        <ProjectGrid projects={projects} />
      </section>

      <section className="grid-2 stack-sm">
        <article className="card">
          <div className="section-header">
            <h2>Kanban snapshot</h2>
          </div>
          <KanbanBoard projects={projects} tasks={tasks.slice(0, 8)} compact />
        </article>
        <article className="card">
          <div className="section-header">
            <h2>Task list</h2>
          </div>
          <TaskList projects={projects} tasks={tasks.slice(0, 6)} compact />
        </article>
      </section>
    </section>
  );
}
