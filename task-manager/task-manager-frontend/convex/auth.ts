import { AuthKit, type AuthFunctions } from "@convex-dev/workos-authkit";
import { components, internal } from "./_generated/api";
import type { DataModel } from "./_generated/dataModel";
import { internalMutation, internalQuery } from "./_generated/server";
import { v } from "convex/values";

// Internal functions for auth
export const getAuthUser = internalQuery({
  args: { authId: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", args.authId))
      .unique();
  },
});

export const createUser = internalMutation({
  args: {
    authId: v.string(),
    email: v.string(),
    name: v.string(),
    avatarUrl: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("users", {
      authId: args.authId,
      email: args.email,
      name: args.name,
      avatarUrl: args.avatarUrl,
    });
  },
});

export const updateUser = internalMutation({
  args: {
    authId: v.string(),
    email: v.string(),
    name: v.string(),
    avatarUrl: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", args.authId))
      .unique();

    if (!user) {
      console.warn(`User not found: ${args.authId}`);
      return;
    }

    await ctx.db.patch(user._id, {
      email: args.email,
      name: args.name,
      avatarUrl: args.avatarUrl,
    });
  },
});

export const deleteUser = internalMutation({
  args: { authId: v.string() },
  handler: async (ctx, args) => {
    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", args.authId))
      .unique();

    if (!user) {
      console.warn(`User not found: ${args.authId}`);
      return;
    }

    // Delete user's projects and tasks
    const projects = await ctx.db
      .query("projects")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();

    for (const project of projects) {
      // Delete tasks in project
      const tasks = await ctx.db
        .query("tasks")
        .withIndex("by_project", (q) => q.eq("projectId", project._id))
        .collect();

      for (const task of tasks) {
        await ctx.db.delete(task._id);
      }

      await ctx.db.delete(project._id);
    }

    await ctx.db.delete(user._id);
  },
});

// Auth functions reference for AuthKit
const authFunctions: AuthFunctions = internal.auth;

// Initialize AuthKit
const authKit = new AuthKit<DataModel>(components.workOSAuthKit, {
  authFunctions,
});

// Export event handlers for WorkOS webhooks
export const { authKitEvent } = authKit.events({
  "user.created": async (ctx, event) => {
    const name = [event.data.firstName, event.data.lastName]
      .filter(Boolean)
      .join(" ") || event.data.email.split("@")[0];

    await ctx.db.insert("users", {
      authId: event.data.id,
      email: event.data.email,
      name,
      avatarUrl: event.data.profilePictureUrl || undefined,
    });
  },

  "user.updated": async (ctx, event) => {
    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", event.data.id))
      .unique();

    if (!user) {
      console.warn(`User not found: ${event.data.id}`);
      return;
    }

    const name = [event.data.firstName, event.data.lastName]
      .filter(Boolean)
      .join(" ") || event.data.email.split("@")[0];

    await ctx.db.patch(user._id, {
      email: event.data.email,
      name,
      avatarUrl: event.data.profilePictureUrl || undefined,
    });
  },

  "user.deleted": async (ctx, event) => {
    const user = await ctx.db
      .query("users")
      .withIndex("by_authId", (q) => q.eq("authId", event.data.id))
      .unique();

    if (!user) {
      console.warn(`User not found: ${event.data.id}`);
      return;
    }

    // Delete user's projects and tasks
    const projects = await ctx.db
      .query("projects")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();

    for (const project of projects) {
      const tasks = await ctx.db
        .query("tasks")
        .withIndex("by_project", (q) => q.eq("projectId", project._id))
        .collect();

      for (const task of tasks) {
        await ctx.db.delete(task._id);
      }

      await ctx.db.delete(project._id);
    }

    await ctx.db.delete(user._id);
  },

  "session.created": async (_ctx, event) => {
    console.log("Session created:", event.data.id);
  },
});

// Export authKit for use in other files
export { authKit };
