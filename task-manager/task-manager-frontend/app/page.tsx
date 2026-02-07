import Link from "next/link";
import { ArrowRight, BriefcaseBusiness, KanbanSquare, Sparkles, Users } from "lucide-react";
import { DEMO_MODE } from "@/lib/config";

const highlights = [
  {
    icon: BriefcaseBusiness,
    title: "Enterprise clarity",
    description: "Portfolio-level project oversight with concise health and progress signals."
  },
  {
    icon: KanbanSquare,
    title: "Polished Kanban",
    description: "Status-focused board with visual priority cues and smooth transitions."
  },
  {
    icon: Users,
    title: "Team-friendly",
    description: "Clean ownership views that stay approachable for technical and non-technical teams."
  }
];

export default function LandingPage() {
  return (
    <main className="landing-root">
      <section className="landing card">
        <div className="landing-copy animate-fade-in">
          <span className="pill warm">Portfolio Demo Ready</span>
          <h1 className="title-xl">Task management with enterprise discipline and friendly usability.</h1>
          <p className="muted">
            A modern task manager designed with Notion-level polish for teams that need structure without friction.
          </p>
          <div className="landing-cta-row">
            <Link className="button primary" href="/dashboard">
              Open Dashboard
              <ArrowRight size={16} />
            </Link>
            <Link className="button secondary" href="/login">
              WorkOS Sign in
            </Link>
          </div>
          {DEMO_MODE ? <span className="pill">Demo mode active with sample project data</span> : null}
        </div>
        <div className="landing-grid">
          {highlights.map(({ icon: Icon, title, description }) => (
            <article key={title} className="card quiet-card animate-fade-in-up">
              <div className="icon-chip">
                <Icon size={18} />
              </div>
              <h2>{title}</h2>
              <p className="muted">{description}</p>
            </article>
          ))}
          <article className="card accent-card animate-fade-in-up">
            <div className="header-row">
              <h2>Visual direction</h2>
              <Sparkles size={18} />
            </div>
            <p className="muted">Navy foundation, indigo accents, warm details, rounded cards, and intentional motion.</p>
          </article>
        </div>
      </section>
    </main>
  );
}
