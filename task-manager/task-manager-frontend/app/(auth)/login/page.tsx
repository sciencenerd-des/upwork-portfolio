import Link from "next/link";
import { DemoModeBadge } from "@/components/ui/demo-badge";

export default function LoginPage() {
  return (
    <main className="single-center">
      <section className="card auth-card animate-fade-in">
        <div className="header-row">
          <h1>Sign in</h1>
          <DemoModeBadge compact />
        </div>
        <p className="muted">WorkOS is optional for this portfolio build. Continue directly in demo mode.</p>
        <label className="label" htmlFor="email">
          Email
        </label>
        <input id="email" className="input" placeholder="demo@company.com" type="email" />
        <label className="label" htmlFor="password">
          Password
        </label>
        <input id="password" className="input" placeholder="••••••••" type="password" />
        <button className="button primary" type="button">
          Continue to dashboard
        </button>
        <p className="muted">
          Need an account? <Link href="/register">Create one</Link>
        </p>
      </section>
    </main>
  );
}
