"use client";

import * as React from "react";
import {
  Download,
  Calendar,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Activity,
  Users,
  CheckCircle2,
  Clock,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

// Simple Bar Chart Component (CSS-based)
function BarChart({ data }: { data: { label: string; value: number; color: string }[] }) {
  const maxValue = Math.max(...data.map((d) => d.value));

  return (
    <div className="space-y-3">
      {data.map((item, index) => (
        <div key={index} className="space-y-1">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">{item.label}</span>
            <span className="font-medium">{item.value}</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className={cn("h-full rounded-full transition-all", item.color)}
              style={{ width: `${(item.value / maxValue) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

// Simple Pie Chart Component (CSS-based)
function DonutChart({
  data,
  total,
}: {
  data: { label: string; value: number; color: string }[];
  total: number;
}) {
  let cumulativePercent = 0;

  const segments = data.map((item) => {
    const percent = (item.value / total) * 100;
    const startPercent = cumulativePercent;
    cumulativePercent += percent;
    return { ...item, percent, startPercent };
  });

  // Create conic gradient
  const gradientStops = segments.map((seg) => {
    const colorMap: Record<string, string> = {
      "bg-blue-500": "#3B82F6",
      "bg-amber-500": "#F59E0B",
      "bg-emerald-500": "#10B981",
      "bg-slate-400": "#94A3B8",
    };
    const color = colorMap[seg.color] || "#94A3B8";
    return `${color} ${seg.startPercent}% ${seg.startPercent + seg.percent}%`;
  }).join(", ");

  return (
    <div className="flex items-center gap-6">
      {/* Donut */}
      <div
        className="relative w-32 h-32 rounded-full"
        style={{
          background: `conic-gradient(${gradientStops})`,
        }}
      >
        <div className="absolute inset-4 bg-card rounded-full flex items-center justify-center">
          <div className="text-center">
            <p className="text-2xl font-bold">{total}</p>
            <p className="text-xs text-muted-foreground">Total</p>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="space-y-2">
        {segments.map((item, index) => (
          <div key={index} className="flex items-center gap-2">
            <div className={cn("w-3 h-3 rounded-full", item.color)} />
            <span className="text-sm">{item.label}</span>
            <span className="text-sm text-muted-foreground">({item.value})</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Stat Card with Trend
function TrendCard({
  title,
  value,
  change,
  changeType,
  icon: Icon,
  iconColor,
}: {
  title: string;
  value: string | number;
  change: string;
  changeType: "positive" | "negative" | "neutral";
  icon: React.ElementType;
  iconColor: string;
}) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          <div className="flex items-center gap-1 mt-1">
            {changeType === "positive" ? (
              <TrendingUp className="h-3 w-3 text-emerald-500" />
            ) : changeType === "negative" ? (
              <TrendingDown className="h-3 w-3 text-red-500" />
            ) : null}
            <span
              className={cn(
                "text-xs",
                changeType === "positive" && "text-emerald-500",
                changeType === "negative" && "text-red-500",
                changeType === "neutral" && "text-muted-foreground"
              )}
            >
              {change}
            </span>
          </div>
        </div>
        <div className={cn("p-2 rounded-lg", iconColor)}>
          <Icon className="h-5 w-5 text-white" />
        </div>
      </div>
    </div>
  );
}

// Activity Timeline
function ActivityTimeline() {
  const activities = [
    { date: "Today", completed: 8, created: 5, resolved: 3 },
    { date: "Yesterday", completed: 12, created: 8, resolved: 6 },
    { date: "Mon, Jan 22", completed: 10, created: 7, resolved: 4 },
    { date: "Sun, Jan 21", completed: 5, created: 3, resolved: 2 },
    { date: "Sat, Jan 20", completed: 3, created: 2, resolved: 1 },
    { date: "Fri, Jan 19", completed: 15, created: 10, resolved: 8 },
    { date: "Thu, Jan 18", completed: 11, created: 9, resolved: 5 },
  ];

  const maxValue = Math.max(...activities.flatMap((a) => [a.completed, a.created, a.resolved]));

  return (
    <div className="space-y-4">
      {/* Legend */}
      <div className="flex items-center gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-500" />
          <span>Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500" />
          <span>Created</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-purple-500" />
          <span>Resolved</span>
        </div>
      </div>

      {/* Chart */}
      <div className="space-y-3">
        {activities.map((day, index) => (
          <div key={index} className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground w-28 shrink-0">{day.date}</span>
            <div className="flex-1 flex items-center gap-1 h-6">
              <div
                className="h-full bg-emerald-500 rounded-l"
                style={{ width: `${(day.completed / maxValue) * 33}%` }}
              />
              <div
                className="h-full bg-blue-500"
                style={{ width: `${(day.created / maxValue) * 33}%` }}
              />
              <div
                className="h-full bg-purple-500 rounded-r"
                style={{ width: `${(day.resolved / maxValue) * 33}%` }}
              />
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground w-24 shrink-0">
              <span className="text-emerald-500">{day.completed}</span>
              <span className="text-blue-500">{day.created}</span>
              <span className="text-purple-500">{day.resolved}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Main Reports Content
export function ReportsContent() {
  const [dateRange, setDateRange] = React.useState("7d");

  const issuesByStatus = [
    { label: "Open", value: 42, color: "bg-blue-500" },
    { label: "In Progress", value: 38, color: "bg-amber-500" },
    { label: "Resolved", value: 56, color: "bg-emerald-500" },
    { label: "Closed", value: 20, color: "bg-slate-400" },
  ];

  const issuesByPriority = [
    { label: "High", value: 24, color: "bg-red-500" },
    { label: "Normal", value: 68, color: "bg-orange-500" },
    { label: "Low", value: 64, color: "bg-green-500" },
  ];

  const issuesByAssignee = [
    { label: "John Doe", value: 28, color: "bg-blue-500" },
    { label: "Jane Smith", value: 24, color: "bg-emerald-500" },
    { label: "Mike Wilson", value: 18, color: "bg-amber-500" },
    { label: "Sarah Johnson", value: 15, color: "bg-purple-500" },
    { label: "Unassigned", value: 12, color: "bg-slate-400" },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Reports</h1>
          <p className="text-muted-foreground mt-1">
            Analytics and insights for your project
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 border rounded-md p-1">
            {["7d", "30d", "90d", "1y"].map((range) => (
              <Button
                key={range}
                variant={dateRange === range ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setDateRange(range)}
                className="h-7 px-3"
              >
                {range}
              </Button>
            ))}
          </div>
          <Button variant="outline" size="sm">
            <Calendar className="h-4 w-4 mr-2" />
            Custom
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <TrendCard
          title="Total Issues"
          value={156}
          change="+12% from last period"
          changeType="positive"
          icon={BarChart3}
          iconColor="bg-blue-500"
        />
        <TrendCard
          title="Completed"
          value={89}
          change="+8% from last period"
          changeType="positive"
          icon={CheckCircle2}
          iconColor="bg-emerald-500"
        />
        <TrendCard
          title="Avg. Resolution Time"
          value="3.2 days"
          change="-15% from last period"
          changeType="positive"
          icon={Clock}
          iconColor="bg-amber-500"
        />
        <TrendCard
          title="Overdue"
          value={7}
          change="+2 from last period"
          changeType="negative"
          icon={AlertCircle}
          iconColor="bg-red-500"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Issues by Status */}
        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Issues by Status</h3>
            <PieChart className="h-4 w-4 text-muted-foreground" />
          </div>
          <DonutChart
            data={issuesByStatus}
            total={issuesByStatus.reduce((acc, d) => acc + d.value, 0)}
          />
        </div>

        {/* Issues by Priority */}
        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Issues by Priority</h3>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </div>
          <BarChart data={issuesByPriority} />
        </div>

        {/* Issues by Assignee */}
        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Issues by Assignee</h3>
            <Users className="h-4 w-4 text-muted-foreground" />
          </div>
          <BarChart data={issuesByAssignee} />
        </div>

        {/* Activity Timeline */}
        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Daily Activity</h3>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </div>
          <ActivityTimeline />
        </div>
      </div>

      {/* Velocity Metrics */}
      <div className="rounded-lg border bg-card p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Team Velocity</h3>
          <Badge variant="secondary">Last 7 days</Badge>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="text-center p-4 rounded-lg bg-muted/50">
            <p className="text-3xl font-bold text-emerald-500">24</p>
            <p className="text-sm text-muted-foreground mt-1">Issues completed</p>
          </div>
          <div className="text-center p-4 rounded-lg bg-muted/50">
            <p className="text-3xl font-bold text-blue-500">18</p>
            <p className="text-sm text-muted-foreground mt-1">Story points</p>
          </div>
          <div className="text-center p-4 rounded-lg bg-muted/50">
            <p className="text-3xl font-bold text-amber-500">2.4</p>
            <p className="text-sm text-muted-foreground mt-1">Avg. cycle time (days)</p>
          </div>
        </div>
      </div>
    </div>
  );
}
