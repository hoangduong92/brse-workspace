"use client";

import * as React from "react";
import { Plus, Download, Settings2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { IssueFilters } from "./issue-filters";
import { IssueTable } from "./issue-table";

export function IssuesPageContent() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Issues</h1>
          <p className="text-muted-foreground mt-1">
            Track and manage all issues across your project
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" size="sm">
            <Settings2 className="h-4 w-4 mr-2" />
            Customize
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            New Issue
          </Button>
        </div>
      </div>

      {/* Filters */}
      <IssueFilters />

      {/* Issues Table */}
      <IssueTable />
    </div>
  );
}
