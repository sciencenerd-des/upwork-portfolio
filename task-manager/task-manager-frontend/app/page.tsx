import Link from "next/link";
import {
  getSignInUrl,
  getSignUpUrl,
  withAuth,
} from "@workos-inc/authkit-nextjs";
import {
  CheckCircle2,
  KanbanSquare,
  ListTodo,
  Zap,
  Shield,
  Clock,
} from "lucide-react";

export default async function LandingPage() {
  const { user } = await withAuth();
  const signInUrl = await getSignInUrl();
  const signUpUrl = await getSignUpUrl();

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-slate-900">TaskFlow</span>
          </div>
          <div className="flex items-center gap-4">
            {user ? (
              <Link
                href="/dashboard"
                className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
              >
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link
                  href={signInUrl}
                  className="px-4 py-2 text-slate-600 hover:text-slate-900 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href={signUpUrl}
                  className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </nav>
      </header>

      {/* Hero */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold text-slate-900 mb-6">
          Organize Your Work,
          <br />
          <span className="text-primary">Boost Your Productivity</span>
        </h1>
        <p className="text-xl text-slate-600 max-w-2xl mx-auto mb-10">
          A simple yet powerful task management tool for freelancers, small
          teams, and solo entrepreneurs. Kanban boards, list views, and
          everything you need to stay on top of your projects.
        </p>
        <div className="flex items-center justify-center gap-4">
          {user ? (
            <Link
              href="/dashboard"
              className="px-8 py-4 bg-primary text-white text-lg font-semibold rounded-lg hover:bg-primary/90 transition-colors"
            >
              Open Dashboard
            </Link>
          ) : (
            <>
              <Link
                href={signUpUrl}
                className="px-8 py-4 bg-primary text-white text-lg font-semibold rounded-lg hover:bg-primary/90 transition-colors"
              >
                Start Free
              </Link>
              <Link
                href={signInUrl}
                className="px-8 py-4 border border-slate-300 text-slate-700 text-lg font-semibold rounded-lg hover:bg-slate-50 transition-colors"
              >
                Sign In
              </Link>
            </>
          )}
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-slate-900 text-center mb-12">
          Everything You Need to Stay Organized
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <KanbanSquare className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              Kanban Boards
            </h3>
            <p className="text-slate-600">
              Visualize your workflow with drag-and-drop Kanban boards. Move
              tasks between columns as work progresses.
            </p>
          </div>

          <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <ListTodo className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              List View
            </h3>
            <p className="text-slate-600">
              Prefer lists? Switch to list view for a table-based layout with
              sorting and filtering options.
            </p>
          </div>

          <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              Real-time Updates
            </h3>
            <p className="text-slate-600">
              Changes sync instantly across all your devices. No refresh needed
              - see updates as they happen.
            </p>
          </div>

          <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
              <Clock className="w-6 h-6 text-orange-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              Due Dates & Priorities
            </h3>
            <p className="text-slate-600">
              Set due dates and priorities to never miss a deadline. Get
              reminders for overdue tasks.
            </p>
          </div>

          <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
            <div className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-pink-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              Secure Authentication
            </h3>
            <p className="text-slate-600">
              Enterprise-grade security with WorkOS. Your data is safe and
              always available.
            </p>
          </div>

          <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
            <div className="w-12 h-12 bg-cyan-100 rounded-lg flex items-center justify-center mb-4">
              <CheckCircle2 className="w-6 h-6 text-cyan-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              Project Organization
            </h3>
            <p className="text-slate-600">
              Group tasks into projects with custom colors. Keep everything
              organized and easy to find.
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-20">
        <div className="bg-primary rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Get Organized?
          </h2>
          <p className="text-primary-foreground/80 text-lg mb-8 max-w-xl mx-auto">
            Join thousands of users who are already managing their projects more
            efficiently with TaskFlow.
          </p>
          {user ? (
            <Link
              href="/dashboard"
              className="inline-block px-8 py-4 bg-white text-primary text-lg font-semibold rounded-lg hover:bg-slate-100 transition-colors"
            >
              Go to Dashboard
            </Link>
          ) : (
            <Link
              href={signUpUrl}
              className="inline-block px-8 py-4 bg-white text-primary text-lg font-semibold rounded-lg hover:bg-slate-100 transition-colors"
            >
              Get Started for Free
            </Link>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 border-t border-slate-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-primary rounded flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4 text-white" />
            </div>
            <span className="text-sm text-slate-600">
              TaskFlow - Built for Productivity
            </span>
          </div>
          <p className="text-sm text-slate-500">
            &copy; {new Date().getFullYear()} Biswajit. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
