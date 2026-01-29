"use client";

import * as React from "react";
import { Search, Filter, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface FilterOption {
  value: string;
  label: string;
  count?: number;
}

const statusOptions: FilterOption[] = [
  { value: "all", label: "All", count: 156 },
  { value: "open", label: "Open", count: 42 },
  { value: "in_progress", label: "In Progress", count: 38 },
  { value: "resolved", label: "Resolved", count: 56 },
  { value: "closed", label: "Closed", count: 20 },
];

const priorityOptions: FilterOption[] = [
  { value: "all", label: "All Priorities" },
  { value: "high", label: "High" },
  { value: "normal", label: "Normal" },
  { value: "low", label: "Low" },
];

const typeOptions: FilterOption[] = [
  { value: "all", label: "All Types" },
  { value: "bug", label: "Bug" },
  { value: "task", label: "Task" },
  { value: "feature", label: "Feature" },
  { value: "improvement", label: "Improvement" },
];

interface IssueFiltersProps {
  onSearchChange?: (value: string) => void;
  onStatusChange?: (value: string) => void;
  onPriorityChange?: (value: string) => void;
  onTypeChange?: (value: string) => void;
}

export function IssueFilters({
  onSearchChange,
  onStatusChange,
  onPriorityChange,
  onTypeChange,
}: IssueFiltersProps) {
  const [search, setSearch] = React.useState("");
  const [status, setStatus] = React.useState("all");
  const [priority, setPriority] = React.useState("all");
  const [type, setType] = React.useState("all");
  const [showFilters, setShowFilters] = React.useState(false);

  const activeFilters = [
    status !== "all" && { key: "status", label: statusOptions.find((s) => s.value === status)?.label },
    priority !== "all" && { key: "priority", label: priorityOptions.find((p) => p.value === priority)?.label },
    type !== "all" && { key: "type", label: typeOptions.find((t) => t.value === type)?.label },
  ].filter(Boolean) as { key: string; label: string }[];

  const clearFilter = (key: string) => {
    if (key === "status") {
      setStatus("all");
      onStatusChange?.("all");
    } else if (key === "priority") {
      setPriority("all");
      onPriorityChange?.("all");
    } else if (key === "type") {
      setType("all");
      onTypeChange?.("all");
    }
  };

  const clearAllFilters = () => {
    setStatus("all");
    setPriority("all");
    setType("all");
    setSearch("");
    onStatusChange?.("all");
    onPriorityChange?.("all");
    onTypeChange?.("all");
    onSearchChange?.("");
  };

  return (
    <div className="space-y-4">
      {/* Search and Filter Toggle */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search issues..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              onSearchChange?.(e.target.value);
            }}
            className="w-full h-9 rounded-md border bg-background pl-9 pr-4 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <Button
          variant={showFilters ? "secondary" : "outline"}
          size="sm"
          onClick={() => setShowFilters(!showFilters)}
        >
          <Filter className="h-4 w-4 mr-2" />
          Filters
          {activeFilters.length > 0 && (
            <Badge variant="secondary" className="ml-2">
              {activeFilters.length}
            </Badge>
          )}
        </Button>
      </div>

      {/* Status Tabs */}
      <div className="flex items-center gap-1 border-b">
        {statusOptions.map((option) => (
          <button
            key={option.value}
            onClick={() => {
              setStatus(option.value);
              onStatusChange?.(option.value);
            }}
            className={cn(
              "px-3 py-2 text-sm font-medium border-b-2 -mb-px transition-colors",
              status === option.value
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {option.label}
            {option.count !== undefined && (
              <span className="ml-1.5 text-xs text-muted-foreground">
                {option.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Expanded Filters */}
      {showFilters && (
        <div className="flex flex-wrap items-center gap-3 p-4 rounded-lg bg-muted/50">
          {/* Priority Filter */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Priority:</span>
            <select
              value={priority}
              onChange={(e) => {
                setPriority(e.target.value);
                onPriorityChange?.(e.target.value);
              }}
              className="h-8 rounded-md border bg-background px-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {priorityOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Type:</span>
            <select
              value={type}
              onChange={(e) => {
                setType(e.target.value);
                onTypeChange?.(e.target.value);
              }}
              className="h-8 rounded-md border bg-background px-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {typeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Active Filter Tags */}
      {activeFilters.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm text-muted-foreground">Active filters:</span>
          {activeFilters.map((filter) => (
            <Badge
              key={filter.key}
              variant="secondary"
              className="gap-1 cursor-pointer"
            >
              {filter.label}
              <X
                className="h-3 w-3"
                onClick={() => clearFilter(filter.key)}
              />
            </Badge>
          ))}
          <Button
            variant="ghost"
            size="sm"
            onClick={clearAllFilters}
            className="text-xs h-6"
          >
            Clear all
          </Button>
        </div>
      )}
    </div>
  );
}
