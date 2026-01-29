import { query, mutation } from "./_generated/server";
import { v } from "convex/values";
import { authKit } from "./auth";

// List all projects for current user
export const list = query({
  args: {
    status: v.optional(v.union(v.literal("active"), v.literal("archived"))),
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

    let projectsQuery = ctx.db
      .query("projects")
      .withIndex("by_user", (q) => q.eq("userId", user._id));

    const projects = await projectsQuery.collect();

    // Filter by status if provided
    const filteredProjects = args.status
      ? projects.filter((p) => p.status === args.status)
      : projects;

    // Get task counts for each project
    const projectsWithCounts = await Promise.all(
      filteredProjects.map(async (project) => {
        const tasks = await ctx.db
          .query("tasks")
          .withIndex("by_project", (q) => q.eq("projectId", project._id))
          .collect();

        const taskCount = tasks.length;
        const completedCount = tasks.filter((t) => t.status === "done").length;

        return {
          ...project,
          taskCount,
          completedCount,
        };
      })
    );

    return projectsWithCounts;
  },
});

// Get single project by ID
export const getById = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    const workosUser = await authKit.getAuthUser(ctx);
    if (!workosUser) {
      return null;
    }

    const project = await ctx.db.get(args.projectId);
    if (!project) {
      return null;
    }

    // Verify ownership
    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", workosUser.id))
      .unique();

    if (!user || project.userId !== user._id) {
      return null;
    }

    // Get task counts
    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_project", (q) => q.eq("projectId", project._id))
      .collect();

    return {
      ...project,
      taskCount: tasks.length,
      completedCount: tasks.filter((t) => t.status === "done").length,
    };
  },
});

// Create new project
export const create = mutation({
  args: {
    name: v.string(),
    description: v.optional(v.string()),
    color: v.string(),
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

    const projectId = await ctx.db.insert("projects", {
      name: args.name,
      description: args.description,
      color: args.color,
      status: "active",
      userId: user._id,
    });

    return projectId;
  },
});

// Update project
export const update = mutation({
  args: {
    projectId: v.id("projects"),
    name: v.optional(v.string()),
    description: v.optional(v.string()),
    color: v.optional(v.string()),
    status: v.optional(v.union(v.literal("active"), v.literal("archived"))),
  },
  handler: async (ctx, args) => {
    const workosUser = await authKit.getAuthUser(ctx);
    if (!workosUser) {
      throw new Error("Not authenticated");
    }

    const project = await ctx.db.get(args.projectId);
    if (!project) {
      throw new Error("Project not found");
    }

    // Verify ownership
    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", workosUser.id))
      .unique();

    if (!user || project.userId !== user._id) {
      throw new Error("Not authorized");
    }

    const updates: Partial<typeof project> = {};
    if (args.name !== undefined) updates.name = args.name;
    if (args.description !== undefined) updates.description = args.description;
    if (args.color !== undefined) updates.color = args.color;
    if (args.status !== undefined) updates.status = args.status;

    await ctx.db.patch(args.projectId, updates);
    return args.projectId;
  },
});

// Delete project (cascades to tasks)
export const remove = mutation({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    const workosUser = await authKit.getAuthUser(ctx);
    if (!workosUser) {
      throw new Error("Not authenticated");
    }

    const project = await ctx.db.get(args.projectId);
    if (!project) {
      throw new Error("Project not found");
    }

    // Verify ownership
    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", workosUser.id))
      .unique();

    if (!user || project.userId !== user._id) {
      throw new Error("Not authorized");
    }

    // Delete all tasks in project
    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();

    for (const task of tasks) {
      await ctx.db.delete(task._id);
    }

    // Delete project
    await ctx.db.delete(args.projectId);
    return args.projectId;
  },
});
