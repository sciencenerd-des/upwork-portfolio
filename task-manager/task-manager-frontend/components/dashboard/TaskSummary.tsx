"use client";

import { Card, CardContent } from "@/components/ui/card";
import { ListTodo, Clock, CheckCircle2, AlertCircle } from "lucide-react";

interface TaskSummaryProps {
  summary:
    | {
        total: number;
        todo: number;
        inProgress: number;
        done: number;
      }
    | undefined;
}

export function TaskSummary({ summary }: TaskSummaryProps) {
  if (!summary) {
    return (
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <div className="h-16 bg-muted animate-pulse rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const stats = [
    {
      label: "Total Tasks",
      value: summary.total,
      icon: ListTodo,
      color: "text-blue-600",
      bgColor: "bg-blue-100",
    },
    {
      label: "To Do",
      value: summary.todo,
      icon: AlertCircle,
      color: "text-slate-600",
      bgColor: "bg-slate-100",
    },
    {
      label: "In Progress",
      value: summary.inProgress,
      icon: Clock,
      color: "text-amber-600",
      bgColor: "bg-amber-100",
    },
    {
      label: "Completed",
      value: summary.done,
      icon: CheckCircle2,
      color: "text-green-600",
      bgColor: "bg-green-100",
    },
  ];

  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <Card key={stat.label}>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div>
                <p className="text-2xl font-bold">{stat.value}</p>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
