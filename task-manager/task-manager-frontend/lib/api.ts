import { getAuthContext } from "@/convex/auth";
import { getDashboardOverview } from "@/convex/dashboard";
import { getProjectById, getProjects } from "@/convex/projects";
import { getTasks, getTasksByProject } from "@/convex/tasks";
import { DEMO_MODE } from "@/lib/config";

const DEMO_DELAY_MS = DEMO_MODE ? 220 : 0;

async function withDelay<T>(callback: () => Promise<T>) {
  if (DEMO_DELAY_MS > 0) {
    await new Promise((resolve) => setTimeout(resolve, DEMO_DELAY_MS));
  }

  return callback();
}

export async function getDashboardData() {
  return withDelay(async () => {
    const [summary, projects, tasks, authState] = await Promise.all([
      getDashboardOverview(),
      getProjects(),
      getTasks(),
      getAuthContext()
    ]);

    return { summary, projects, tasks, authState };
  });
}

export async function getKanbanData() {
  return withDelay(async () => {
    const [projects, tasks] = await Promise.all([getProjects(), getTasks()]);
    return { projects, tasks };
  });
}

export async function getTasksData() {
  return withDelay(async () => {
    const [projects, tasks] = await Promise.all([getProjects(), getTasks()]);
    return { projects, tasks };
  });
}

export async function getProjectData(projectId: string) {
  return withDelay(async () => {
    const [project, tasks] = await Promise.all([getProjectById(projectId), getTasksByProject(projectId)]);
    return { project, tasks };
  });
}
