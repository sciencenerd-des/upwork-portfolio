import { query, mutation } from "./_generated/server";
import { v } from "convex/values";
import { authKit } from "./auth";

const taskStatusValues = v.union(
  v.literal("todo"),
  v.literal("in_progress"),
  v.literal("done")
);

const taskPriorityValues = v.union(
  v.literal("low"),
  v.literal("medium"),
  v.literal("high"),
  v.literal("urgent")
);

// List tasks by project
export const listByProject = query({
  args: { projectId: v.id("projects") },
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

    // Verify project ownership
    const project = await ctx.db.get(args.projectId);
    if (!project || project.userId !== user._id) {
      return [];
    }

    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();

    // Sort by position
    return tasks.sort((a, b) => a.position - b.position);
  },
});

// List tasks by status for a project
export const listByStatus = query({
  args: {
    projectId: v.id("projects"),
    status: taskStatusValues,
  },
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

    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_project_status", (q) =>
        q.eq("projectId", args.projectId).eq("status", args.status)
      )
      .collect();

    return tasks.sort((a, b) => a.position - b.position);
  },
});

// Get single task by ID
export const getById = query({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, args) => {
    const workosUser = await authKit.getAuthUser(ctx);
    if (!workosUser) {
      return null;
    }

    const task = await ctx.db.get(args.taskId);
    if (!task) {
      return null;
    }

    // Verify ownership
    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", workosUser.id))
      .unique();

    if (!user || task.userId !== user._id) {
      return null;
    }

    return task;
  },
});

// Create new task
export const create = mutation({
  args: {
    title: v.string(),
    description: v.optional(v.string()),
    status: taskStatusValues,
    priority: taskPriorityValues,
    dueDate: v.optional(v.number()),
    projectId: v.id("projects"),
  },
  handler: async (ctx, args) => {
    const workosUser = await authKit.getAuthUser(ctx);
    if (!workosUser) {
      throw new Error("Not authenticated");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", workosUser.id))
      .unique();

    if (!user) {
      throw new Error("User not found");
    }

    // Verify project ownership
    const project = await ctx.db.get(args.projectId);
    if (!project || project.userId !== user._id) {
      throw new Error("Project not found or not authorized");
    }

    // Get max position for new task
    const existingTasks = await ctx.db
      .query("tasks")
      .withIndex("by_project_status", (q) =>
        q.eq("projectId", args.projectId).eq("status", args.status)
      )
      .collect();

    const maxPosition = existingTasks.reduce(
      (max, task) => Math.max(max, task.position),
      -1
    );

    const taskId = await ctx.db.insert("tasks", {
      title: args.title,
      description: args.description,
      status: args.status,
      priority: args.priority,
      dueDate: args.dueDate,
      position: maxPosition + 1,
      projectId: args.projectId,
      userId: user._id,
    });

    return taskId;
  },
});

// Update task
export const update = mutation({
  args: {
    taskId: v.id("tasks"),
    title: v.optional(v.string()),
    description: v.optional(v.string()),
    priority: v.optional(taskPriorityValues),
    dueDate: v.optional(v.union(v.number(), v.null())),
  },
  handler: async (ctx, args) => {
    const workosUser = await authKit.getAuthUser(ctx);
    if (!workosUser) {
      throw new Error("Not authenticated");
    }

    const task = await ctx.db.get(args.taskId);
    if (!task) {
      throw new Error("Task not found");
    }

    // Verify ownership
    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", workosUser.id))
      .unique();

    if (!user || task.userId !== user._id) {
      throw new Error("Not authorized");
    }

    const updates: Partial<typeof task> = {};
    if (args.title !== undefined) updates.title = args.title;
    if (args.description !== undefined) updates.description = args.description;
    if (args.priority !== undefined) updates.priority = args.priority;
    if (args.dueDate !== undefined) {
      updates.dueDate = args.dueDate === null ? undefined : args.dueDate;
    }

    await ctx.db.patch(args.taskId, updates);
    return args.taskId;
  },
});

// Update task status (for drag-and-drop)
export const updateStatus = mutation({
  args: {
    taskId: v.id("tasks"),
    status: taskStatusValues,
    position: v.number(),
  },
  handler: async (ctx, args) => {
    const workosUser = await authKit.getAuthUser(ctx);
    if (!workosUser) {
      throw new Error("Not authenticated");
    }

    const task = await ctx.db.get(args.taskId);
    if (!task) {
      throw new Error("Task not found");
    }

    // Verify ownership
    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", workosUser.id))
      .unique();

    if (!user || task.userId !== user._id) {
      throw new Error("Not authorized");
    }

    await ctx.db.patch(args.taskId, {
      status: args.status,
      position: args.position,
    });

    return args.taskId;
  },
});

// Reorder tasks within a column
export const reorder = mutation({
  args: {
    taskId: v.id("tasks"),
    newPosition: v.number(),
  },
  handler: async (ctx, args) => {
    const workosUser = await authKit.getAuthUser(ctx);
    if (!workosUser) {
      throw new Error("Not authenticated");
    }

    const task = await ctx.db.get(args.taskId);
    if (!task) {
      throw new Error("Task not found");
    }

    // Verify ownership
    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", workosUser.id))
      .unique();

    if (!user || task.userId !== user._id) {
      throw new Error("Not authorized");
    }

    await ctx.db.patch(args.taskId, {
      position: args.newPosition,
    });

    return args.taskId;
  },
});

// Delete task
export const remove = mutation({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, args) => {
    const workosUser = await authKit.getAuthUser(ctx);
    if (!workosUser) {
      throw new Error("Not authenticated");
    }

    const task = await ctx.db.get(args.taskId);
    if (!task) {
      throw new Error("Task not found");
    }

    // Verify ownership
    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", workosUser.id))
      .unique();

    if (!user || task.userId !== user._id) {
      throw new Error("Not authorized");
    }

    await ctx.db.delete(args.taskId);
    return args.taskId;
  },
});
