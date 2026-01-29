"use client";

import * as React from "react";
import {
  ListTodo,
  CheckCircle2,
  Clock,
  AlertCircle,
  TrendingUp,
  Users,
  FolderKanban,
  ArrowRight,
  MoreHorizontal,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

// Stats Card Component
interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: "positive" | "negative" | "neutral";
  icon: React.ElementType;
  iconColor: string;
}

function StatCard({
  title,
  value,
  change,
  changeType = "neutral",
  icon: Icon,
  iconColor,
}: StatCardProps) {
  return (
    <div className="rounded-lg border bg-card p-4 hover:shadow-sm transition-shadow cursor-pointer">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {change && (
            <p
              className={cn(
                "text-xs mt-1",
                changeType === "positive" && "text-emerald-600",
                changeType === "negative" && "text-red-600",
                changeType === "neutral" && "text-muted-foreground"
              )}
            >
              {change}
            </p>
          )}
        </div>
        <div className={cn("p-2 rounded-lg", iconColor)}>
          <Icon className="h-5 w-5 text-white" />
        </div>
      </div>
    </div>
  );
}

// Recent Issues Component
interface Issue {
  id: string;
  key: string;
  title: string;
  status: "open" | "in_progress" | "resolved" | "closed";
  priority: "high" | "normal" | "low";
  assignee?: { name: string; initials: string };
  updatedAt: string;
}

const mockIssues: Issue[] = [
  {
    id: "1",
    key: "BUP-123",
    title: "Implement user authentication flow",
    status: "in_progress",
    priority: "high",
    assignee: { name: "John Doe", initials: "JD" },
    updatedAt: "2 hours ago",
  },
  {
    id: "2",
    key: "BUP-122",
    title: "Fix sidebar navigation on mobile",
    status: "open",
    priority: "normal",
    assignee: { name: "Jane Smith", initials: "JS" },
    updatedAt: "5 hours ago",
  },
  {
    id: "3",
    key: "BUP-121",
    title: "Add dark mode support",
    status: "resolved",
    priority: "low",
    updatedAt: "1 day ago",
  },
  {
    id: "4",
    key: "BUP-120",
    title: "Performance optimization for large datasets",
    status: "in_progress",
    priority: "high",
    assignee: { name: "Mike Wilson", initials: "MW" },
    updatedAt: "2 days ago",
  },
  {
    id: "5",
    key: "BUP-119",
    title: "Update API documentation",
    status: "open",
    priority: "normal",
    updatedAt: "3 days ago",
  },
];

const statusConfig = {
  open: { label: "Open", variant: "info" as const },
  in_progress: { label: "In Progress", variant: "warning" as const },
  resolved: { label: "Resolved", variant: "success" as const },
  closed: { label: "Closed", variant: "secondary" as const },
};

const priorityConfig = {
  high: { color: "bg-red-500" },
  normal: { color: "bg-orange-500" },
  low: { color: "bg-green-500" },
};

function RecentIssues() {
  return (
    <div className="rounded-lg border bg-card">
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="font-semibold">Recent Issues</h3>
        <Button variant="ghost" size="sm" className="text-primary">
          View all
          <ArrowRight className="h-4 w-4 ml-1" />
        </Button>
      </div>
      <div className="divide-y">
        {mockIssues.map((issue) => (
          <div
            key={issue.id}
            className="flex items-center gap-4 p-4 hover:bg-muted/50 transition-colors cursor-pointer"
          >
            <div
              className={cn("w-1 h-8 rounded-full", priorityConfig[issue.priority].color)}
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground font-mono">
                  {issue.key}
                </span>
                <Badge variant={statusConfig[issue.status].variant}>
                  {statusConfig[issue.status].label}
                </Badge>
              </div>
              <p className="text-sm font-medium truncate mt-1">{issue.title}</p>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              {issue.assignee ? (
                <Avatar className="h-6 w-6">
                  <AvatarFallback className="text-[10px]">
                    {issue.assignee.initials}
                  </AvatarFallback>
                </Avatar>
              ) : (
                <div className="h-6 w-6 rounded-full border-2 border-dashed border-muted-foreground/30" />
              )}
              <span className="text-xs text-muted-foreground hidden sm:block">
                {issue.updatedAt}
              </span>
              <Button variant="ghost" size="icon" className="h-7 w-7">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Activity Feed Component
interface Activity {
  id: string;
  user: { name: string; initials: string };
  action: string;
  target: string;
  time: string;
}

const mockActivities: Activity[] = [
  {
    id: "1",
    user: { name: "John Doe", initials: "JD" },
    action: "created issue",
    target: "BUP-123",
    time: "2 hours ago",
  },
  {
    id: "2",
    user: { name: "Jane Smith", initials: "JS" },
    action: "commented on",
    target: "BUP-122",
    time: "3 hours ago",
  },
  {
    id: "3",
    user: { name: "Mike Wilson", initials: "MW" },
    action: "resolved",
    target: "BUP-121",
    time: "5 hours ago",
  },
  {
    id: "4",
    user: { name: "Sarah Johnson", initials: "SJ" },
    action: "assigned to",
    target: "BUP-120",
    time: "1 day ago",
  },
];

function ActivityFeed() {
  return (
    <div className="rounded-lg border bg-card">
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="font-semibold">Recent Activity</h3>
        <Button variant="ghost" size="sm" className="text-primary">
          View all
          <ArrowRight className="h-4 w-4 ml-1" />
        </Button>
      </div>
      <div className="p-4 space-y-4">
        {mockActivities.map((activity) => (
          <div key={activity.id} className="flex items-start gap-3">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="text-xs">
                {activity.user.initials}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm">
                <span className="font-medium">{activity.user.name}</span>{" "}
                <span className="text-muted-foreground">{activity.action}</span>{" "}
                <span className="font-medium text-primary">{activity.target}</span>
              </p>
              <p className="text-xs text-muted-foreground mt-0.5">
                {activity.time}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Projects Overview Component
interface Project {
  id: string;
  name: string;
  key: string;
  color: string;
  openIssues: number;
  progress: number;
}

const mockProjects: Project[] = [
  { id: "1", name: "Backlog UI Pro", key: "BUP", color: "bg-blue-500", openIssues: 24, progress: 65 },
  { id: "2", name: "Mobile App", key: "MOB", color: "bg-emerald-500", openIssues: 12, progress: 45 },
  { id: "3", name: "API Gateway", key: "API", color: "bg-amber-500", openIssues: 8, progress: 80 },
];

function ProjectsOverview() {
  return (
    <div className="rounded-lg border bg-card">
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="font-semibold">Projects</h3>
        <Button variant="ghost" size="sm" className="text-primary">
          View all
          <ArrowRight className="h-4 w-4 ml-1" />
        </Button>
      </div>
      <div className="p-4 space-y-4">
        {mockProjects.map((project) => (
          <div
            key={project.id}
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
          >
            <div
              className={cn(
                "h-10 w-10 rounded-lg flex items-center justify-center text-white font-bold",
                project.color
              )}
            >
              {project.key[0]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{project.name}</p>
              <p className="text-xs text-muted-foreground">
                {project.openIssues} open issues
              </p>
            </div>
            <div className="w-24">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-muted-foreground">Progress</span>
                <span className="font-medium">{project.progress}%</span>
              </div>
              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                <div
                  className={cn("h-full rounded-full", project.color)}
                  style={{ width: `${project.progress}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Main Dashboard Content
export function DashboardContent() {
  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h1 className="text-2xl font-bold">Welcome back, John</h1>
        <p className="text-muted-foreground mt-1">
          Here&apos;s what&apos;s happening with your projects today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Issues"
          value={156}
          change="+12% from last month"
          changeType="positive"
          icon={ListTodo}
          iconColor="bg-blue-500"
        />
        <StatCard
          title="Completed"
          value={89}
          change="+8% from last month"
          changeType="positive"
          icon={CheckCircle2}
          iconColor="bg-emerald-500"
        />
        <StatCard
          title="In Progress"
          value={42}
          change="-3% from last month"
          changeType="neutral"
          icon={Clock}
          iconColor="bg-amber-500"
        />
        <StatCard
          title="Overdue"
          value={7}
          change="-2 from last week"
          changeType="positive"
          icon={AlertCircle}
          iconColor="bg-red-500"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent Issues - Takes 2 columns */}
        <div className="lg:col-span-2">
          <RecentIssues />
        </div>

        {/* Sidebar - Activity & Projects */}
        <div className="space-y-6">
          <ActivityFeed />
          <ProjectsOverview />
        </div>
      </div>

      {/* Quick Stats Row */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="flex items-center gap-4 rounded-lg border bg-card p-4 cursor-pointer hover:shadow-sm transition-shadow">
          <div className="p-2 rounded-lg bg-primary/10">
            <TrendingUp className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Velocity</p>
            <p className="text-lg font-semibold">24 issues/week</p>
          </div>
        </div>
        <div className="flex items-center gap-4 rounded-lg border bg-card p-4 cursor-pointer hover:shadow-sm transition-shadow">
          <div className="p-2 rounded-lg bg-emerald-500/10">
            <Users className="h-5 w-5 text-emerald-500" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Team Members</p>
            <p className="text-lg font-semibold">12 active</p>
          </div>
        </div>
        <div className="flex items-center gap-4 rounded-lg border bg-card p-4 cursor-pointer hover:shadow-sm transition-shadow">
          <div className="p-2 rounded-lg bg-amber-500/10">
            <FolderKanban className="h-5 w-5 text-amber-500" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Active Projects</p>
            <p className="text-lg font-semibold">6 projects</p>
          </div>
        </div>
      </div>
    </div>
  );
}
