import { CheckCircle2, Gauge, ListTodo, Target } from "lucide-react";
import { DashboardSummary } from "@/types";

export function SummaryCards({ summary }: { summary: DashboardSummary }) {
  const cards = [
    {
      icon: Target,
      label: "Active projects",
      value: summary.openProjects,
      helper: "Across strategic initiatives"
    },
    {
      icon: ListTodo,
      label: "Total tasks",
      value: summary.totalTasks,
      helper: "Tracked in current cycle"
    },
    {
      icon: CheckCircle2,
      label: "Completed",
      value: summary.completedTasks,
      helper: "Closed tasks in this dataset"
    },
    {
      icon: Gauge,
      label: "Velocity",
      value: `${summary.velocity}%`,
      helper: "Execution efficiency signal"
    }
  ];

  return (
    <section className="grid-4">
      {cards.map(({ icon: Icon, label, value, helper }) => (
        <article key={label} className="card stat-card animate-fade-in-up">
          <div className="header-row">
            <p className="muted">{label}</p>
            <span className="icon-chip">
              <Icon size={16} />
            </span>
          </div>
          <h3>{value}</h3>
          <p className="muted">{helper}</p>
        </article>
      ))}
    </section>
  );
}
