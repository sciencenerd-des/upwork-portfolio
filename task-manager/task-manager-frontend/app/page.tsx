import Link from "next/link";
import { ArrowRight, BriefcaseBusiness, KanbanSquare, Layers, Sparkles, Target, Users } from "lucide-react";
import { DemoModeBadge } from "@/components/ui/demo-badge";

const highlights = [
  {
    icon: BriefcaseBusiness,
    title: "Portfolio Clarity",
    description: "Unified project oversight with health signals, progress tracking, and resource visibility across all workstreams."
  },
  {
    icon: KanbanSquare,
    title: "Visual Workflow",
    description: "Intuitive Kanban with priority-driven design, status columns, and seamless task progression."
  },
  {
    icon: Users,
    title: "Team Alignment",
    description: "Clear ownership, async-friendly updates, and accessible views for technical and business stakeholders alike."
  },
  {
    icon: Target,
    title: "Outcome Focused",
    description: "Milestone tracking, deadline visibility, and progress analytics that keep delivery on target."
  }
];

export default function LandingPage() {
  return (
    <main className="landing-root">
      <section className="landing card">
        <div className="landing-copy animate-fade-in">
          <div className="landing-header-row">
            <span className="pill warm">Production-Ready Demo</span>
            <DemoModeBadge />
          </div>
          <h1 className="title-xl">Project management that balances structure with speed.</h1>
          <p className="muted">
            Northstar PM delivers enterprise-grade visibility with consumer-grade usability. 
            Built for teams that need accountability without bureaucracy.
          </p>
          <div className="landing-cta-row">
            <Link className="button primary" href="/dashboard">
              Explore Dashboard
              <ArrowRight size={16} />
            </Link>
            <Link className="button secondary" href="/login">
              Sign In with WorkOS
            </Link>
          </div>
          <div className="landing-meta">
            <span className="chip">
              <Layers size={12} />
              Next.js 14 + Convex
            </span>
            <span className="chip">
              <Sparkles size={12} />
              Demo Mode Available
            </span>
          </div>
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
        </div>
      </section>
    </main>
  );
}
