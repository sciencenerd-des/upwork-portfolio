import { demoProjects } from "@/lib/demo-data";
import { Project } from "@/types";

export async function getProjects(): Promise<Project[]> {
  return demoProjects.map((project) => ({ ...project }));
}

export async function getProjectById(projectId: string): Promise<Project | null> {
  const project = demoProjects.find((item) => item.id === projectId);
  return project ? { ...project } : null;
}
