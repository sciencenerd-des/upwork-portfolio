import Link from "next/link";
import { DemoModeBadge } from "@/components/ui/demo-badge";

export default function RegisterPage() {
  return (
    <main className="single-center">
      <section className="card auth-card animate-fade-in">
        <div className="header-row">
          <h1>Create account</h1>
          <DemoModeBadge compact />
        </div>
        <p className="muted">For the demo, registration is simulated and routes directly to the dashboard.</p>
        <label className="label" htmlFor="name">
          Full name
        </label>
        <input id="name" className="input" placeholder="Alex Morgan" type="text" />
        <label className="label" htmlFor="work-email">
          Work email
        </label>
        <input id="work-email" className="input" placeholder="alex@northstar.design" type="email" />
        <button className="button primary" type="button">
          Launch demo workspace
        </button>
        <p className="muted">
          Already have an account? <Link href="/login">Sign in</Link>
        </p>
      </section>
    </main>
  );
}
