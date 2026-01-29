import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: Date | number): string {
  const d = typeof date === "number" ? new Date(date) : date;
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatRelativeDate(date: Date | number): string {
  const d = typeof date === "number" ? new Date(date) : date;
  const now = new Date();
  const diffTime = d.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Tomorrow";
  if (diffDays === -1) return "Yesterday";
  if (diffDays < -1) return `${Math.abs(diffDays)} days ago`;
  if (diffDays > 1 && diffDays <= 7) return `In ${diffDays} days`;

  return formatDate(d);
}

export function isOverdue(dueDate: number | undefined): boolean {
  if (!dueDate) return false;
  return dueDate < Date.now();
}

export function isDueToday(dueDate: number | undefined): boolean {
  if (!dueDate) return false;
  const now = new Date();
  const startOfDay = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate()
  ).getTime();
  const endOfDay = startOfDay + 24 * 60 * 60 * 1000;
  return dueDate >= startOfDay && dueDate < endOfDay;
}

export const PROJECT_COLORS = [
  { name: "Blue", value: "#2563EB" },
  { name: "Green", value: "#22C55E" },
  { name: "Purple", value: "#9333EA" },
  { name: "Pink", value: "#EC4899" },
  { name: "Orange", value: "#F97316" },
  { name: "Teal", value: "#14B8A6" },
  { name: "Red", value: "#EF4444" },
  { name: "Yellow", value: "#EAB308" },
];

export const PRIORITY_COLORS = {
  urgent: "#EF4444",
  high: "#F97316",
  medium: "#EAB308",
  low: "#94A3B8",
};

export const STATUS_LABELS = {
  todo: "To Do",
  in_progress: "In Progress",
  done: "Done",
};

export const PRIORITY_LABELS = {
  urgent: "Urgent",
  high: "High",
  medium: "Medium",
  low: "Low",
};
