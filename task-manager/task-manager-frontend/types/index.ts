export type TaskStatus = "backlog" | "in_progress" | "review" | "done";
export type TaskPriority = "low" | "medium" | "high";

export type ProjectHealth = "On Track" | "At Risk" | "Blocked";

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
  avatarColor: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  owner: string;
  health: ProjectHealth;
  progress: number;
  dueDate: string;
  team: string[];
  updatedAt: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  projectId: string;
  assignee: string;
  status: TaskStatus;
  priority: TaskPriority;
  dueDate: string;
  tags: string[];
  estimate: number;
}

export interface DashboardSummary {
  openProjects: number;
  totalTasks: number;
  completedTasks: number;
  velocity: number;
}

export interface AuthState {
  mode: "demo" | "workos";
  isAuthenticated: boolean;
  workosClientId: string;
  user: UserProfile;
}
