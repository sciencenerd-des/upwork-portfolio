import { DemoModeBadge } from "@/components/ui/demo-badge";
import { DEMO_MODE, WORKOS_PLACEHOLDER_CONFIG } from "@/lib/config";

export default function SettingsPage() {
  return (
    <section className="stack-lg animate-fade-in">
      <header className="card hero-card">
        <span className="pill">Settings</span>
        <h1 className="title-lg">Environment configuration</h1>
        <p className="muted">This build supports a zero-config demo mode while remaining WorkOS-ready.</p>
      </header>

      <article className="card stack-md">
        <div className="header-row">
          <h2>Authentication mode</h2>
          <DemoModeBadge />
        </div>
        <p className="muted">
          Current mode: <strong>{DEMO_MODE ? "Demo" : "WorkOS"}</strong>
        </p>
        <div className="meta-row">
          <span className="chip">Client ID: {WORKOS_PLACEHOLDER_CONFIG.clientId}</span>
          <span className="chip">Org: {WORKOS_PLACEHOLDER_CONFIG.organizationId}</span>
          <span className="chip">Redirect: {WORKOS_PLACEHOLDER_CONFIG.redirectUri}</span>
        </div>
      </article>

      <article className="card stack-sm">
        <h2>Demo behavior</h2>
        <p className="muted">
          When `NEXT_PUBLIC_DEMO_MODE=true`, sample projects and tasks are injected and sign-in is simulated for
          portfolio reviews.
        </p>
      </article>
    </section>
  );
}
