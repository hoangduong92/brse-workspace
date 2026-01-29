"use client";

import * as React from "react";
import {
  FileText,
  Folder,
  FolderOpen,
  Plus,
  Search,
  MoreHorizontal,
  Clock,
  User,
  ChevronRight,
  ChevronDown,
  Edit3,
  Trash2,
  Copy,
  Star,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

// Types
interface WikiPage {
  id: string;
  title: string;
  type: "page" | "folder";
  children?: WikiPage[];
  lastModified?: string;
  author?: { name: string; initials: string };
  starred?: boolean;
}

// Mock data
const mockWikiTree: WikiPage[] = [
  {
    id: "1",
    title: "Getting Started",
    type: "folder",
    children: [
      { id: "1-1", title: "Quick Start Guide", type: "page", lastModified: "2 days ago", author: { name: "John Doe", initials: "JD" } },
      { id: "1-2", title: "Installation", type: "page", lastModified: "1 week ago", author: { name: "Jane Smith", initials: "JS" } },
      { id: "1-3", title: "Configuration", type: "page", lastModified: "3 days ago", author: { name: "John Doe", initials: "JD" } },
    ],
  },
  {
    id: "2",
    title: "API Documentation",
    type: "folder",
    children: [
      { id: "2-1", title: "Authentication", type: "page", lastModified: "1 day ago", author: { name: "Mike Wilson", initials: "MW" }, starred: true },
      { id: "2-2", title: "Endpoints Reference", type: "page", lastModified: "5 hours ago", author: { name: "Sarah Johnson", initials: "SJ" } },
      {
        id: "2-3",
        title: "Examples",
        type: "folder",
        children: [
          { id: "2-3-1", title: "Node.js Examples", type: "page", lastModified: "1 week ago", author: { name: "John Doe", initials: "JD" } },
          { id: "2-3-2", title: "Python Examples", type: "page", lastModified: "2 weeks ago", author: { name: "Jane Smith", initials: "JS" } },
        ],
      },
    ],
  },
  {
    id: "3",
    title: "Development Guidelines",
    type: "page",
    lastModified: "3 days ago",
    author: { name: "Mike Wilson", initials: "MW" },
    starred: true,
  },
  {
    id: "4",
    title: "Architecture Overview",
    type: "page",
    lastModified: "1 week ago",
    author: { name: "Sarah Johnson", initials: "SJ" },
  },
  {
    id: "5",
    title: "Deployment",
    type: "folder",
    children: [
      { id: "5-1", title: "Production Setup", type: "page", lastModified: "4 days ago", author: { name: "John Doe", initials: "JD" } },
      { id: "5-2", title: "CI/CD Pipeline", type: "page", lastModified: "2 days ago", author: { name: "Mike Wilson", initials: "MW" } },
    ],
  },
];

// Selected page content
const mockContent = {
  title: "Quick Start Guide",
  lastModified: "2 days ago",
  author: { name: "John Doe", initials: "JD" },
  content: `
# Quick Start Guide

Welcome to Backlog UI Pro! This guide will help you get started quickly.

## Prerequisites

Before you begin, ensure you have the following installed:
- Node.js 18 or higher
- npm or yarn package manager

## Installation

\`\`\`bash
npm install
npm run dev
\`\`\`

## Project Structure

The project follows a standard Next.js App Router structure:

- \`src/app/\` - Page routes
- \`src/components/\` - Reusable components
- \`src/lib/\` - Utility functions

## Next Steps

1. Explore the dashboard
2. Create your first issue
3. Invite team members
  `,
};

// Tree Item Component
function TreeItem({
  page,
  level = 0,
  selectedId,
  onSelect,
}: {
  page: WikiPage;
  level?: number;
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  const [expanded, setExpanded] = React.useState(level === 0);
  const hasChildren = page.type === "folder" && page.children && page.children.length > 0;
  const isSelected = selectedId === page.id;

  return (
    <div>
      <div
        className={cn(
          "flex items-center gap-2 px-2 py-1.5 rounded-md text-sm cursor-pointer transition-colors",
          isSelected ? "bg-primary/10 text-primary" : "hover:bg-muted",
          level > 0 && "ml-4"
        )}
        onClick={() => {
          if (hasChildren) {
            setExpanded(!expanded);
          }
          onSelect(page.id);
        }}
      >
        {hasChildren ? (
          expanded ? (
            <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
          )
        ) : (
          <span className="w-4" />
        )}

        {page.type === "folder" ? (
          expanded ? (
            <FolderOpen className="h-4 w-4 shrink-0 text-amber-500" />
          ) : (
            <Folder className="h-4 w-4 shrink-0 text-amber-500" />
          )
        ) : (
          <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
        )}

        <span className="truncate flex-1">{page.title}</span>

        {page.starred && <Star className="h-3 w-3 fill-amber-400 text-amber-400" />}
      </div>

      {hasChildren && expanded && (
        <div className="mt-1">
          {page.children!.map((child) => (
            <TreeItem
              key={child.id}
              page={child}
              level={level + 1}
              selectedId={selectedId}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Main Wiki Content
export function WikiContent() {
  const [selectedId, setSelectedId] = React.useState<string | null>("1-1");
  const [searchQuery, setSearchQuery] = React.useState("");

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-6">
      {/* Sidebar - Wiki Tree */}
      <div className="w-72 shrink-0 flex flex-col rounded-lg border bg-card">
        {/* Search */}
        <div className="p-3 border-b">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search wiki..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-9 rounded-md border bg-background pl-9 pr-4 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>

        {/* Tree */}
        <div className="flex-1 overflow-auto p-3 space-y-1">
          {mockWikiTree.map((page) => (
            <TreeItem
              key={page.id}
              page={page}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />
          ))}
        </div>

        {/* Add Page Button */}
        <div className="p-3 border-t">
          <Button className="w-full" size="sm">
            <Plus className="h-4 w-4 mr-2" />
            New Page
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col rounded-lg border bg-card overflow-hidden">
        {/* Content Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold">{mockContent.title}</h1>
            <Button variant="ghost" size="icon" className="h-7 w-7">
              <Star className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Edit3 className="h-4 w-4 mr-2" />
              Edit
            </Button>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Meta Info */}
        <div className="flex items-center gap-4 px-4 py-2 border-b bg-muted/30 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            <span>Last modified {mockContent.lastModified}</span>
          </div>
          <div className="flex items-center gap-2">
            <User className="h-4 w-4" />
            <span>by {mockContent.author.name}</span>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-auto p-6">
          <div className="prose prose-sm max-w-none">
            <div className="space-y-4">
              <h1 className="text-2xl font-bold">Quick Start Guide</h1>
              <p className="text-muted-foreground">
                Welcome to Backlog UI Pro! This guide will help you get started quickly.
              </p>

              <h2 className="text-xl font-semibold mt-6">Prerequisites</h2>
              <p>Before you begin, ensure you have the following installed:</p>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>Node.js 18 or higher</li>
                <li>npm or yarn package manager</li>
              </ul>

              <h2 className="text-xl font-semibold mt-6">Installation</h2>
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
                <code className="text-sm">
                  npm install{"\n"}
                  npm run dev
                </code>
              </pre>

              <h2 className="text-xl font-semibold mt-6">Project Structure</h2>
              <p>The project follows a standard Next.js App Router structure:</p>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li><code className="bg-muted px-1 rounded">src/app/</code> - Page routes</li>
                <li><code className="bg-muted px-1 rounded">src/components/</code> - Reusable components</li>
                <li><code className="bg-muted px-1 rounded">src/lib/</code> - Utility functions</li>
              </ul>

              <h2 className="text-xl font-semibold mt-6">Next Steps</h2>
              <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                <li>Explore the dashboard</li>
                <li>Create your first issue</li>
                <li>Invite team members</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
