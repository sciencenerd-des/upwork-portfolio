import Link from "next/link";

export default function NotFoundPage() {
  return (
    <main className="single-center">
      <section className="card info-card">
        <h1>Project not found</h1>
        <p className="muted">This demo only includes a fixed set of sample projects.</p>
        <Link className="button primary" href="/dashboard">
          Return to dashboard
        </Link>
      </section>
    </main>
  );
}
