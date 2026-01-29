"use client";

import * as React from "react";
import {
  Bug,
  Lightbulb,
  CheckSquare,
  Zap,
  MoreHorizontal,
  MessageSquare,
  Paperclip,
  ChevronUp,
  ChevronDown,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

// Issue type icons
const typeIcons = {
  bug: { icon: Bug, color: "text-red-500" },
  task: { icon: CheckSquare, color: "text-blue-500" },
  feature: { icon: Lightbulb, color: "text-amber-500" },
  improvement: { icon: Zap, color: "text-purple-500" },
};

// Status badge config
const statusConfig = {
  open: { label: "Open", variant: "info" as const },
  in_progress: { label: "In Progress", variant: "warning" as const },
  resolved: { label: "Resolved", variant: "success" as const },
  closed: { label: "Closed", variant: "secondary" as const },
};

// Priority indicator
const priorityConfig = {
  high: { color: "bg-red-500", label: "High" },
  normal: { color: "bg-orange-500", label: "Normal" },
  low: { color: "bg-green-500", label: "Low" },
};

export interface Issue {
  id: string;
  key: string;
  title: string;
  type: keyof typeof typeIcons;
  status: keyof typeof statusConfig;
  priority: keyof typeof priorityConfig;
  assignee?: { name: string; initials: string };
  reporter: { name: string; initials: string };
  comments: number;
  attachments: number;
  createdAt: string;
  updatedAt: string;
  dueDate?: string;
}

// Mock data
export const mockIssues: Issue[] = [
  {
    id: "1",
    key: "BUP-123",
    title: "Implement user authentication flow with OAuth2",
    type: "feature",
    status: "in_progress",
    priority: "high",
    assignee: { name: "John Doe", initials: "JD" },
    reporter: { name: "Sarah Johnson", initials: "SJ" },
    comments: 8,
    attachments: 2,
    createdAt: "2024-01-15",
    updatedAt: "2 hours ago",
    dueDate: "2024-01-30",
  },
  {
    id: "2",
    key: "BUP-122",
    title: "Fix sidebar navigation on mobile devices",
    type: "bug",
    status: "open",
    priority: "high",
    assignee: { name: "Jane Smith", initials: "JS" },
    reporter: { name: "Mike Wilson", initials: "MW" },
    comments: 3,
    attachments: 1,
    createdAt: "2024-01-14",
    updatedAt: "5 hours ago",
  },
  {
    id: "3",
    key: "BUP-121",
    title: "Add dark mode support across all components",
    type: "improvement",
    status: "resolved",
    priority: "normal",
    reporter: { name: "John Doe", initials: "JD" },
    comments: 12,
    attachments: 0,
    createdAt: "2024-01-10",
    updatedAt: "1 day ago",
  },
  {
    id: "4",
    key: "BUP-120",
    title: "Performance optimization for large datasets in tables",
    type: "task",
    status: "in_progress",
    priority: "high",
    assignee: { name: "Mike Wilson", initials: "MW" },
    reporter: { name: "Jane Smith", initials: "JS" },
    comments: 5,
    attachments: 3,
    createdAt: "2024-01-08",
    updatedAt: "2 days ago",
    dueDate: "2024-01-25",
  },
  {
    id: "5",
    key: "BUP-119",
    title: "Update API documentation for v2 endpoints",
    type: "task",
    status: "open",
    priority: "low",
    reporter: { name: "Sarah Johnson", initials: "SJ" },
    comments: 0,
    attachments: 0,
    createdAt: "2024-01-05",
    updatedAt: "3 days ago",
  },
  {
    id: "6",
    key: "BUP-118",
    title: "Database connection pool exhaustion under load",
    type: "bug",
    status: "open",
    priority: "high",
    assignee: { name: "John Doe", initials: "JD" },
    reporter: { name: "Mike Wilson", initials: "MW" },
    comments: 15,
    attachments: 4,
    createdAt: "2024-01-04",
    updatedAt: "4 hours ago",
    dueDate: "2024-01-20",
  },
  {
    id: "7",
    key: "BUP-117",
    title: "Implement real-time notifications system",
    type: "feature",
    status: "in_progress",
    priority: "normal",
    assignee: { name: "Jane Smith", initials: "JS" },
    reporter: { name: "John Doe", initials: "JD" },
    comments: 6,
    attachments: 1,
    createdAt: "2024-01-02",
    updatedAt: "1 day ago",
  },
  {
    id: "8",
    key: "BUP-116",
    title: "Add keyboard shortcuts for common actions",
    type: "improvement",
    status: "closed",
    priority: "low",
    reporter: { name: "Sarah Johnson", initials: "SJ" },
    comments: 2,
    attachments: 0,
    createdAt: "2023-12-28",
    updatedAt: "1 week ago",
  },
];

interface IssueTableProps {
  issues?: Issue[];
}

export function IssueTable({ issues = mockIssues }: IssueTableProps) {
  const [sortField, setSortField] = React.useState<string>("updatedAt");
  const [sortDirection, setSortDirection] = React.useState<"asc" | "desc">("desc");
  const [selectedIssues, setSelectedIssues] = React.useState<Set<string>>(new Set());

  const toggleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const toggleSelectAll = () => {
    if (selectedIssues.size === issues.length) {
      setSelectedIssues(new Set());
    } else {
      setSelectedIssues(new Set(issues.map((i) => i.id)));
    }
  };

  const toggleSelect = (id: string) => {
    const newSelected = new Set(selectedIssues);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIssues(newSelected);
  };

  const SortIcon = ({ field }: { field: string }) => {
    if (sortField !== field) return null;
    return sortDirection === "asc" ? (
      <ChevronUp className="h-4 w-4" />
    ) : (
      <ChevronDown className="h-4 w-4" />
    );
  };

  return (
    <div className="rounded-lg border bg-card overflow-hidden">
      {/* Table Header */}
      <div className="grid grid-cols-[auto_1fr_120px_120px_100px_120px_auto] items-center gap-4 px-4 py-3 bg-muted/50 border-b text-sm font-medium text-muted-foreground">
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={selectedIssues.size === issues.length && issues.length > 0}
            onChange={toggleSelectAll}
            className="h-4 w-4 rounded border-gray-300"
          />
        </div>
        <button
          onClick={() => toggleSort("title")}
          className="flex items-center gap-1 hover:text-foreground text-left"
        >
          Issue
          <SortIcon field="title" />
        </button>
        <button
          onClick={() => toggleSort("status")}
          className="flex items-center gap-1 hover:text-foreground"
        >
          Status
          <SortIcon field="status" />
        </button>
        <button
          onClick={() => toggleSort("priority")}
          className="flex items-center gap-1 hover:text-foreground"
        >
          Priority
          <SortIcon field="priority" />
        </button>
        <div>Assignee</div>
        <button
          onClick={() => toggleSort("updatedAt")}
          className="flex items-center gap-1 hover:text-foreground"
        >
          Updated
          <SortIcon field="updatedAt" />
        </button>
        <div></div>
      </div>

      {/* Table Body */}
      <div className="divide-y">
        {issues.map((issue) => {
          const TypeIcon = typeIcons[issue.type].icon;
          const typeColor = typeIcons[issue.type].color;

          return (
            <div
              key={issue.id}
              className={cn(
                "grid grid-cols-[auto_1fr_120px_120px_100px_120px_auto] items-center gap-4 px-4 py-3 hover:bg-muted/30 transition-colors cursor-pointer",
                selectedIssues.has(issue.id) && "bg-primary/5"
              )}
            >
              {/* Checkbox */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedIssues.has(issue.id)}
                  onChange={() => toggleSelect(issue.id)}
                  onClick={(e) => e.stopPropagation()}
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>

              {/* Issue Info */}
              <div className="flex items-center gap-3 min-w-0">
                <TypeIcon className={cn("h-4 w-4 shrink-0", typeColor)} />
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground font-mono">
                      {issue.key}
                    </span>
                    {issue.dueDate && (
                      <span className="text-xs text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">
                        Due {issue.dueDate}
                      </span>
                    )}
                  </div>
                  <p className="text-sm font-medium truncate">{issue.title}</p>
                  <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                    {issue.comments > 0 && (
                      <span className="flex items-center gap-1">
                        <MessageSquare className="h-3 w-3" />
                        {issue.comments}
                      </span>
                    )}
                    {issue.attachments > 0 && (
                      <span className="flex items-center gap-1">
                        <Paperclip className="h-3 w-3" />
                        {issue.attachments}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Status */}
              <div>
                <Badge variant={statusConfig[issue.status].variant}>
                  {statusConfig[issue.status].label}
                </Badge>
              </div>

              {/* Priority */}
              <div className="flex items-center gap-2">
                <div
                  className={cn(
                    "w-2 h-2 rounded-full",
                    priorityConfig[issue.priority].color
                  )}
                />
                <span className="text-sm">{priorityConfig[issue.priority].label}</span>
              </div>

              {/* Assignee */}
              <div>
                {issue.assignee ? (
                  <Avatar className="h-7 w-7">
                    <AvatarFallback className="text-[10px]">
                      {issue.assignee.initials}
                    </AvatarFallback>
                  </Avatar>
                ) : (
                  <div className="h-7 w-7 rounded-full border-2 border-dashed border-muted-foreground/30" />
                )}
              </div>

              {/* Updated */}
              <div className="text-sm text-muted-foreground">
                {issue.updatedAt}
              </div>

              {/* Actions */}
              <div>
                <Button variant="ghost" size="icon" className="h-7 w-7">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Table Footer */}
      <div className="flex items-center justify-between px-4 py-3 border-t bg-muted/30">
        <span className="text-sm text-muted-foreground">
          {selectedIssues.size > 0
            ? `${selectedIssues.size} of ${issues.length} selected`
            : `${issues.length} issues`}
        </span>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled>
            Previous
          </Button>
          <Button variant="outline" size="sm">
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}
