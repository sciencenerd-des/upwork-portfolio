import Link from "next/link";
import { Clock3, Users } from "lucide-react";
import { formatDate } from "@/lib/utils";
import { Project } from "@/types";

const healthTone: Record<Project["health"], string> = {
  "On Track": "success",
  "At Risk": "warning",
  Blocked: "danger"
};

export function ProjectGrid({ projects }: { projects: Project[] }) {
  return (
    <div className="grid-3">
      {projects.map((project) => (
        <Link key={project.id} href={`/project/${project.id}`} className="card project-card animate-fade-in-up">
          <div className="header-row">
            <h3>{project.name}</h3>
            <span className={`status-dot ${healthTone[project.health]}`}>{project.health}</span>
          </div>
          <p className="muted">{project.description}</p>
          <div className="meta-row">
            <span className="chip">
              <Clock3 size={14} />
              {formatDate(project.dueDate)}
            </span>
            <span className="chip">
              <Users size={14} />
              {project.team.length} members
            </span>
          </div>
          <div className="stack-sm">
            <div className="header-row">
              <span className="muted">Progress</span>
              <span>{project.progress}%</span>
            </div>
            <div className="progress-track">
              <span className="progress-fill" style={{ width: `${project.progress}%` }} />
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
