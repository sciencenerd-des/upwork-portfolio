import { KanbanBoard } from "@/components/tasks/kanban-board";
import { getKanbanData } from "@/lib/api";

export default async function KanbanPage() {
  const { projects, tasks } = await getKanbanData();

  return (
    <section className="stack-lg animate-fade-in">
      <header className="card hero-card">
        <span className="pill">Kanban</span>
        <h1 className="title-lg">Delivery board</h1>
        <p className="muted">A polished multi-column board for backlog, execution, review, and completion.</p>
      </header>
      <article className="card">
        <KanbanBoard projects={projects} tasks={tasks} />
      </article>
    </section>
  );
}
