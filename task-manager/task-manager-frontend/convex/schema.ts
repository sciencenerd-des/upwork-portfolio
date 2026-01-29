import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Users synced from WorkOS
  users: defineTable({
    authId: v.string(),
    email: v.string(),
    name: v.string(),
    avatarUrl: v.optional(v.string()),
  })
    .index("by_authId", ["authId"])
    .index("by_email", ["email"]),

  // Projects
  projects: defineTable({
    name: v.string(),
    description: v.optional(v.string()),
    color: v.string(),
    status: v.union(v.literal("active"), v.literal("archived")),
    userId: v.id("users"),
  })
    .index("by_user", ["userId"])
    .index("by_user_status", ["userId", "status"]),

  // Tasks
  tasks: defineTable({
    title: v.string(),
    description: v.optional(v.string()),
    status: v.union(
      v.literal("todo"),
      v.literal("in_progress"),
      v.literal("done")
    ),
    priority: v.union(
      v.literal("low"),
      v.literal("medium"),
      v.literal("high"),
      v.literal("urgent")
    ),
    dueDate: v.optional(v.number()),
    position: v.number(),
    projectId: v.id("projects"),
    userId: v.id("users"),
  })
    .index("by_project", ["projectId"])
    .index("by_user", ["userId"])
    .index("by_project_status", ["projectId", "status"])
    .index("by_user_due", ["userId", "dueDate"]),
});
