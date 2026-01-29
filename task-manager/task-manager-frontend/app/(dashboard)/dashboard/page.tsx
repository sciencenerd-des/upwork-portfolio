"use client";

import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { TaskSummary } from "@/components/dashboard/TaskSummary";
import { OverdueTasks } from "@/components/dashboard/OverdueTasks";
import { DueToday } from "@/components/dashboard/DueToday";
import { RecentTasks } from "@/components/dashboard/RecentTasks";
import { ProjectList } from "@/components/projects/ProjectList";

export default function DashboardPage() {
  const currentUser = useQuery(api.users.getCurrentUser);
  const summary = useQuery(api.dashboard.getTaskSummary);
  const overdueTasks = useQuery(api.dashboard.getOverdueTasks);
  const dueTodayTasks = useQuery(api.dashboard.getDueToday);
  const recentTasks = useQuery(api.dashboard.getRecentTasks, { limit: 5 });

  if (!currentUser) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">
          Welcome back, {currentUser.name?.split(" ")[0] || "there"}!
        </h1>
        <p className="text-slate-600 mt-1">
          Here&apos;s what&apos;s happening with your tasks today.
        </p>
      </div>

      {/* Task Summary Cards */}
      <TaskSummary summary={summary} />

      {/* Two Column Layout */}
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Due Today */}
        <DueToday tasks={dueTodayTasks} />

        {/* Overdue Tasks */}
        <OverdueTasks tasks={overdueTasks} />
      </div>

      {/* Recent Tasks */}
      <RecentTasks tasks={recentTasks} />

      {/* Projects */}
      <div>
        <h2 className="text-xl font-semibold text-slate-900 mb-4">
          Your Projects
        </h2>
        <ProjectList />
      </div>
    </div>
  );
}
