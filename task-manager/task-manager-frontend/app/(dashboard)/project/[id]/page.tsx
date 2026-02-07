import { notFound } from "next/navigation";
import { ProjectGrid } from "@/components/projects/project-grid";
import { TaskList } from "@/components/tasks/task-list";
import { getProjectData } from "@/lib/api";

export default async function ProjectPage({ params }: { params: { id: string } }) {
  const { project, tasks } = await getProjectData(params.id);

  if (!project) {
    notFound();
  }

  return (
    <section className="stack-lg animate-fade-in">
      <header className="card hero-card">
        <span className="pill">Project view</span>
        <h1 className="title-lg">{project.name}</h1>
        <p className="muted">{project.description}</p>
        <div className="meta-row">
          <span className="chip">Owner: {project.owner}</span>
          <span className="chip">Health: {project.health}</span>
          <span className="chip">Due: {project.dueDate}</span>
        </div>
      </header>

      <section className="stack-md">
        <div className="section-header">
          <h2>Project status</h2>
        </div>
        <ProjectGrid projects={[project]} />
      </section>

      <section className="stack-md">
        <div className="section-header">
          <h2>Tasks under this project</h2>
        </div>
        <article className="card">
          <TaskList projects={[project]} tasks={tasks} />
        </article>
      </section>
    </section>
  );
}
