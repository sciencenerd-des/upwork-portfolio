import { demoTasks } from "@/lib/demo-data";
import { Task } from "@/types";

export async function getTasks(): Promise<Task[]> {
  return demoTasks.map((task) => ({ ...task }));
}

export async function getTasksByProject(projectId: string): Promise<Task[]> {
  return demoTasks.filter((task) => task.projectId === projectId).map((task) => ({ ...task }));
}
