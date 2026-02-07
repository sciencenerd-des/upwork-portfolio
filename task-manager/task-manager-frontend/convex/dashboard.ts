import { getProjects } from "@/convex/projects";
import { getTasks } from "@/convex/tasks";
import { DashboardSummary } from "@/types";

export async function getDashboardOverview(): Promise<DashboardSummary> {
  const projects = await getProjects();
  const tasks = await getTasks();

  const completedTasks = tasks.filter((task) => task.status === "done").length;

  return {
    openProjects: projects.length,
    totalTasks: tasks.length,
    completedTasks,
    velocity: Math.round((completedTasks / Math.max(tasks.length, 1)) * 100)
  };
}
