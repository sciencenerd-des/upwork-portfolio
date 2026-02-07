import { Project, Task, UserProfile } from "@/types";

export const demoUser: UserProfile = {
  id: "u_demo_admin",
  name: "Alex Morgan",
  email: "alex@northstar.design",
  role: "Product Lead",
  avatarColor: "var(--indigo)"
};

export const demoProjects: Project[] = [
  {
    id: "p_orion",
    name: "Orion Workspace Revamp",
    description: "Refresh the workspace experience with a focus on speed and discoverability.",
    owner: "Alex Morgan",
    health: "On Track",
    progress: 72,
    dueDate: "2026-03-21",
    team: ["Alex", "Priya", "Jordan", "Mina"],
    updatedAt: "2026-02-06"
  },
  {
    id: "p_portal",
    name: "Customer Portal Migration",
    description: "Migrate legacy portal workflows into a unified modern shell.",
    owner: "Priya Shah",
    health: "At Risk",
    progress: 48,
    dueDate: "2026-03-04",
    team: ["Priya", "Noah", "Ari", "Eli"],
    updatedAt: "2026-02-05"
  },
  {
    id: "p_knowledge",
    name: "Knowledge Base Launch",
    description: "Launch internal documentation hub with role-aware navigation.",
    owner: "Jordan Lee",
    health: "Blocked",
    progress: 31,
    dueDate: "2026-03-29",
    team: ["Jordan", "Mina", "Sam"],
    updatedAt: "2026-02-03"
  }
];

export const demoTasks: Task[] = [
  {
    id: "t_001",
    title: "Audit IA gaps in workspace navigation",
    description: "Map current routes against top customer journeys.",
    projectId: "p_orion",
    assignee: "Priya",
    status: "backlog",
    priority: "medium",
    dueDate: "2026-02-11",
    tags: ["UX", "Research"],
    estimate: 5
  },
  {
    id: "t_002",
    title: "Build responsive sidebar interactions",
    description: "Add compact state and keyboard accessibility polish.",
    projectId: "p_orion",
    assignee: "Mina",
    status: "in_progress",
    priority: "high",
    dueDate: "2026-02-12",
    tags: ["Frontend", "A11y"],
    estimate: 8
  },
  {
    id: "t_003",
    title: "Ship action tray animations",
    description: "Implement spring-like transitions for panel reveal.",
    projectId: "p_orion",
    assignee: "Alex",
    status: "review",
    priority: "medium",
    dueDate: "2026-02-13",
    tags: ["Motion"],
    estimate: 3
  },
  {
    id: "t_004",
    title: "Finalize visual regression snapshots",
    description: "Capture desktop/mobile snapshots for release branch.",
    projectId: "p_orion",
    assignee: "Jordan",
    status: "done",
    priority: "low",
    dueDate: "2026-02-04",
    tags: ["QA"],
    estimate: 2
  },
  {
    id: "t_005",
    title: "Map legacy permissions to new portal roles",
    description: "Ensure role mapping is complete before migration wave one.",
    projectId: "p_portal",
    assignee: "Noah",
    status: "backlog",
    priority: "high",
    dueDate: "2026-02-10",
    tags: ["Backend", "Security"],
    estimate: 8
  },
  {
    id: "t_006",
    title: "Create migration checklist",
    description: "Build a reusable checklist for each customer cohort.",
    projectId: "p_portal",
    assignee: "Priya",
    status: "in_progress",
    priority: "medium",
    dueDate: "2026-02-14",
    tags: ["Ops"],
    estimate: 5
  },
  {
    id: "t_007",
    title: "Review SSO callback handling",
    description: "Verify callback flows for workspaces with custom domains.",
    projectId: "p_portal",
    assignee: "Eli",
    status: "review",
    priority: "high",
    dueDate: "2026-02-09",
    tags: ["Auth", "WorkOS"],
    estimate: 5
  },
  {
    id: "t_008",
    title: "Close pilot migration report",
    description: "Summarize pilot findings and next actions.",
    projectId: "p_portal",
    assignee: "Ari",
    status: "done",
    priority: "medium",
    dueDate: "2026-02-02",
    tags: ["Reporting"],
    estimate: 2
  },
  {
    id: "t_009",
    title: "Define knowledge taxonomy",
    description: "Agree on information architecture before content loading.",
    projectId: "p_knowledge",
    assignee: "Jordan",
    status: "backlog",
    priority: "high",
    dueDate: "2026-02-15",
    tags: ["Content"],
    estimate: 5
  },
  {
    id: "t_010",
    title: "Draft contributor onboarding flow",
    description: "Design first-run flow for new article contributors.",
    projectId: "p_knowledge",
    assignee: "Sam",
    status: "in_progress",
    priority: "medium",
    dueDate: "2026-02-18",
    tags: ["Onboarding"],
    estimate: 8
  },
  {
    id: "t_011",
    title: "Review search relevance scoring",
    description: "Tune weighted fields for result ranking quality.",
    projectId: "p_knowledge",
    assignee: "Mina",
    status: "review",
    priority: "medium",
    dueDate: "2026-02-16",
    tags: ["Search"],
    estimate: 3
  },
  {
    id: "t_012",
    title: "Publish launch checklist",
    description: "Confirm QA, analytics, and adoption tracking are in place.",
    projectId: "p_knowledge",
    assignee: "Alex",
    status: "done",
    priority: "low",
    dueDate: "2026-02-01",
    tags: ["Launch"],
    estimate: 2
  }
];
