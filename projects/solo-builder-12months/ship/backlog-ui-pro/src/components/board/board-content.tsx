"use client";

import * as React from "react";
import {
  Plus,
  MoreHorizontal,
  MessageSquare,
  Paperclip,
  Calendar,
  GripVertical,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

// Types
interface BoardCard {
  id: string;
  key: string;
  title: string;
  priority: "high" | "normal" | "low";
  assignee?: { name: string; initials: string };
  comments: number;
  attachments: number;
  dueDate?: string;
}

interface BoardColumn {
  id: string;
  title: string;
  status: string;
  color: string;
  cards: BoardCard[];
}

// Priority config
const priorityColors = {
  high: "bg-red-500",
  normal: "bg-orange-500",
  low: "bg-green-500",
};

// Mock data
const mockColumns: BoardColumn[] = [
  {
    id: "open",
    title: "Open",
    status: "open",
    color: "border-t-blue-500",
    cards: [
      {
        id: "1",
        key: "BUP-125",
        title: "Add user profile page with avatar upload",
        priority: "high",
        assignee: { name: "John Doe", initials: "JD" },
        comments: 3,
        attachments: 1,
        dueDate: "Jan 30",
      },
      {
        id: "2",
        key: "BUP-124",
        title: "Fix mobile navigation menu",
        priority: "normal",
        comments: 0,
        attachments: 0,
      },
      {
        id: "3",
        key: "BUP-123",
        title: "Update API documentation",
        priority: "low",
        assignee: { name: "Jane Smith", initials: "JS" },
        comments: 2,
        attachments: 0,
      },
    ],
  },
  {
    id: "in_progress",
    title: "In Progress",
    status: "in_progress",
    color: "border-t-amber-500",
    cards: [
      {
        id: "4",
        key: "BUP-122",
        title: "Implement OAuth2 authentication flow",
        priority: "high",
        assignee: { name: "Mike Wilson", initials: "MW" },
        comments: 8,
        attachments: 2,
        dueDate: "Jan 28",
      },
      {
        id: "5",
        key: "BUP-121",
        title: "Add dark mode support",
        priority: "normal",
        assignee: { name: "Sarah Johnson", initials: "SJ" },
        comments: 5,
        attachments: 0,
      },
    ],
  },
  {
    id: "review",
    title: "In Review",
    status: "review",
    color: "border-t-purple-500",
    cards: [
      {
        id: "6",
        key: "BUP-120",
        title: "Performance optimization for tables",
        priority: "high",
        assignee: { name: "John Doe", initials: "JD" },
        comments: 12,
        attachments: 3,
      },
    ],
  },
  {
    id: "resolved",
    title: "Resolved",
    status: "resolved",
    color: "border-t-emerald-500",
    cards: [
      {
        id: "7",
        key: "BUP-119",
        title: "Fix date picker timezone issue",
        priority: "normal",
        assignee: { name: "Jane Smith", initials: "JS" },
        comments: 4,
        attachments: 1,
      },
      {
        id: "8",
        key: "BUP-118",
        title: "Add export to CSV feature",
        priority: "low",
        assignee: { name: "Mike Wilson", initials: "MW" },
        comments: 2,
        attachments: 0,
      },
      {
        id: "9",
        key: "BUP-117",
        title: "Improve error messages",
        priority: "low",
        comments: 1,
        attachments: 0,
      },
    ],
  },
];

// Card Component
function KanbanCard({ card }: { card: BoardCard }) {
  return (
    <div className="bg-card border rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow cursor-pointer group">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <div className={cn("w-1.5 h-1.5 rounded-full", priorityColors[card.priority])} />
          <span className="text-xs text-muted-foreground font-mono">{card.key}</span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <MoreHorizontal className="h-3 w-3" />
        </Button>
      </div>

      {/* Title */}
      <p className="text-sm font-medium mb-3 line-clamp-2">{card.title}</p>

      {/* Footer */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          {card.dueDate && (
            <span className="flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              {card.dueDate}
            </span>
          )}
          {card.comments > 0 && (
            <span className="flex items-center gap-1">
              <MessageSquare className="h-3 w-3" />
              {card.comments}
            </span>
          )}
          {card.attachments > 0 && (
            <span className="flex items-center gap-1">
              <Paperclip className="h-3 w-3" />
              {card.attachments}
            </span>
          )}
        </div>
        {card.assignee ? (
          <Avatar className="h-6 w-6">
            <AvatarFallback className="text-[10px]">{card.assignee.initials}</AvatarFallback>
          </Avatar>
        ) : (
          <div className="h-6 w-6 rounded-full border-2 border-dashed border-muted-foreground/30" />
        )}
      </div>
    </div>
  );
}

// Column Component
function KanbanColumn({ column }: { column: BoardColumn }) {
  return (
    <div className="flex flex-col w-72 shrink-0">
      {/* Column Header */}
      <div className={cn("rounded-t-lg border border-b-0 bg-card p-3 border-t-4", column.color)}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-sm">{column.title}</h3>
            <Badge variant="secondary" className="text-xs">
              {column.cards.length}
            </Badge>
          </div>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" className="h-7 w-7">
              <Plus className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" className="h-7 w-7">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Cards Container */}
      <div className="flex-1 rounded-b-lg border bg-muted/30 p-2 space-y-2 min-h-[200px]">
        {column.cards.map((card) => (
          <KanbanCard key={card.id} card={card} />
        ))}

        {/* Add Card Button */}
        <Button
          variant="ghost"
          className="w-full justify-start text-muted-foreground hover:text-foreground"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add issue
        </Button>
      </div>
    </div>
  );
}

// Main Board Content
export function BoardContent() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Board</h1>
          <p className="text-muted-foreground mt-1">
            Visualize your workflow with Kanban board
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <GripVertical className="h-4 w-4 mr-2" />
            Customize
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Add Column
          </Button>
        </div>
      </div>

      {/* Board */}
      <ScrollArea className="w-full">
        <div className="flex gap-4 pb-4">
          {mockColumns.map((column) => (
            <KanbanColumn key={column.id} column={column} />
          ))}
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
    </div>
  );
}
