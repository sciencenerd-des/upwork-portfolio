import { query } from "./_generated/server";
import { v } from "convex/values";
import { authKit } from "./auth";

// Get task summary for dashboard
export const getTaskSummary = query({
  args: {},
  handler: async (ctx) => {
    const workosUser = await authKit.getAuthUser(ctx);
    if (!workosUser) {
      return {
        total: 0,
        todo: 0,
        inProgress: 0,
        done: 0,
      };
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", workosUser.id))
      .unique();

    if (!user) {
      return {
        total: 0,
        todo: 0,
        inProgress: 0,
        done: 0,
      };
    }

    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();

    return {
      total: tasks.length,
      todo: tasks.filter((t) => t.status === "todo").length,
      inProgress: tasks.filter((t) => t.status === "in_progress").length,
      done: tasks.filter((t) => t.status === "done").length,
    };
  },
});

// Get overdue tasks
export const getOverdueTasks = query({
  args: {},
  handler: async (ctx) => {
    const workosUser = await authKit.getAuthUser(ctx);
    if (!workosUser) {
      return [];
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", workosUser.id))
      .unique();

    if (!user) {
      return [];
    }

    const now = Date.now();
    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();

    const overdueTasks = tasks.filter(
      (task) =>
        task.dueDate &&
        task.dueDate < now &&
        task.status !== "done"
    );

    // Get project info for each task
    const tasksWithProject = await Promise.all(
      overdueTasks.map(async (task) => {
        const project = await ctx.db.get(task.projectId);
        return {
          ...task,
          project: project
            ? { name: project.name, color: project.color }
            : null,
        };
      })
    );

    return tasksWithProject.sort((a, b) => (a.dueDate ?? 0) - (b.dueDate ?? 0));
  },
});

// Get tasks due today
export const getDueToday = query({
  args: {},
  handler: async (ctx) => {
    const workosUser = await authKit.getAuthUser(ctx);
    if (!workosUser) {
      return [];
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", workosUser.id))
      .unique();

    if (!user) {
      return [];
    }

    const now = new Date();
    const startOfDay = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate()
    ).getTime();
    const endOfDay = startOfDay + 24 * 60 * 60 * 1000;

    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();

    const dueTodayTasks = tasks.filter(
      (task) =>
        task.dueDate &&
        task.dueDate >= startOfDay &&
        task.dueDate < endOfDay &&
        task.status !== "done"
    );

    // Get project info for each task
    const tasksWithProject = await Promise.all(
      dueTodayTasks.map(async (task) => {
        const project = await ctx.db.get(task.projectId);
        return {
          ...task,
          project: project
            ? { name: project.name, color: project.color }
            : null,
        };
      })
    );

    return tasksWithProject;
  },
});

// Get recent tasks (last updated)
export const getRecentTasks = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const workosUser = await authKit.getAuthUser(ctx);
    if (!workosUser) {
      return [];
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", workosUser.id))
      .unique();

    if (!user) {
      return [];
    }

    const limit = args.limit ?? 5;

    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .order("desc")
      .take(limit);

    // Get project info for each task
    const tasksWithProject = await Promise.all(
      tasks.map(async (task) => {
        const project = await ctx.db.get(task.projectId);
        return {
          ...task,
          project: project
            ? { name: project.name, color: project.color }
            : null,
        };
      })
    );

    return tasksWithProject;
  },
});
