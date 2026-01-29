"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FolderKanban,
  ListTodo,
  Users,
  GitBranch,
  FileText,
  BarChart3,
  Settings,
  ChevronDown,
  Plus,
  Home,
  Search,
  Bell,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface NavItem {
  title: string;
  href: string;
  icon: React.ElementType;
}

const mainNavItems: NavItem[] = [
  { title: "Home", href: "/", icon: Home },
  { title: "Issues", href: "/issues", icon: ListTodo },
  { title: "Board", href: "/board", icon: FolderKanban },
  { title: "Wiki", href: "/wiki", icon: FileText },
  { title: "Git", href: "/git", icon: GitBranch },
  { title: "Files", href: "/files", icon: FolderKanban },
];

const secondaryNavItems: NavItem[] = [
  { title: "Members", href: "/members", icon: Users },
  { title: "Reports", href: "/reports", icon: BarChart3 },
  { title: "Settings", href: "/settings", icon: Settings },
];

const projects = [
  { id: "1", name: "Backlog UI Pro", key: "BUP", color: "bg-blue-500" },
  { id: "2", name: "Mobile App", key: "MOB", color: "bg-emerald-500" },
  { id: "3", name: "API Gateway", key: "API", color: "bg-amber-500" },
];

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

export function Sidebar({ collapsed = false }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "flex flex-col bg-sidebar text-sidebar-foreground h-screen transition-all duration-200",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo */}
      <div className="flex h-14 items-center px-4 border-b border-sidebar-border">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold">
            B
          </div>
          {!collapsed && (
            <span className="font-semibold text-lg">Backlog</span>
          )}
        </Link>
      </div>

      {/* Search & Quick Actions */}
      {!collapsed && (
        <div className="p-3 space-y-2">
          <Button
            variant="ghost"
            className="w-full justify-start text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent"
          >
            <Search className="h-4 w-4 mr-2" />
            Search...
            <kbd className="ml-auto text-xs bg-sidebar-accent px-1.5 py-0.5 rounded">
              /
            </kbd>
          </Button>
        </div>
      )}

      <ScrollArea className="flex-1 px-3">
        {/* Project Selector */}
        <div className="py-2">
          {!collapsed && (
            <div className="flex items-center justify-between px-2 mb-2">
              <span className="text-xs font-medium text-sidebar-foreground/50 uppercase tracking-wider">
                Projects
              </span>
              <Button
                variant="ghost"
                size="icon"
                className="h-5 w-5 text-sidebar-foreground/50 hover:text-sidebar-foreground"
              >
                <Plus className="h-3 w-3" />
              </Button>
            </div>
          )}

          <div className="space-y-1">
            {projects.map((project) => (
              <Tooltip key={project.id} delayDuration={0}>
                <TooltipTrigger asChild>
                  <Link
                    href={`/projects/${project.key.toLowerCase()}`}
                    className={cn(
                      "flex items-center gap-2 px-2 py-1.5 rounded-md text-sm transition-colors cursor-pointer",
                      "hover:bg-sidebar-accent text-sidebar-foreground/70 hover:text-sidebar-foreground"
                    )}
                  >
                    <div
                      className={cn(
                        "h-5 w-5 rounded flex items-center justify-center text-[10px] font-bold text-white",
                        project.color
                      )}
                    >
                      {project.key[0]}
                    </div>
                    {!collapsed && (
                      <>
                        <span className="truncate flex-1">{project.name}</span>
                        <ChevronDown className="h-3 w-3 opacity-50" />
                      </>
                    )}
                  </Link>
                </TooltipTrigger>
                {collapsed && (
                  <TooltipContent side="right">{project.name}</TooltipContent>
                )}
              </Tooltip>
            ))}
          </div>
        </div>

        <Separator className="my-2 bg-sidebar-border" />

        {/* Main Navigation */}
        <nav className="space-y-1 py-2">
          {mainNavItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Tooltip key={item.href} delayDuration={0}>
                <TooltipTrigger asChild>
                  <Link
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 px-2 py-2 rounded-md text-sm transition-colors cursor-pointer",
                      isActive
                        ? "bg-sidebar-accent text-sidebar-foreground font-medium"
                        : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground"
                    )}
                  >
                    <item.icon className="h-4 w-4 shrink-0" />
                    {!collapsed && <span>{item.title}</span>}
                    {isActive && !collapsed && (
                      <div className="ml-auto h-1.5 w-1.5 rounded-full bg-primary" />
                    )}
                  </Link>
                </TooltipTrigger>
                {collapsed && (
                  <TooltipContent side="right">{item.title}</TooltipContent>
                )}
              </Tooltip>
            );
          })}
        </nav>

        <Separator className="my-2 bg-sidebar-border" />

        {/* Secondary Navigation */}
        <nav className="space-y-1 py-2">
          {secondaryNavItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Tooltip key={item.href} delayDuration={0}>
                <TooltipTrigger asChild>
                  <Link
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 px-2 py-2 rounded-md text-sm transition-colors cursor-pointer",
                      isActive
                        ? "bg-sidebar-accent text-sidebar-foreground font-medium"
                        : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground"
                    )}
                  >
                    <item.icon className="h-4 w-4 shrink-0" />
                    {!collapsed && <span>{item.title}</span>}
                  </Link>
                </TooltipTrigger>
                {collapsed && (
                  <TooltipContent side="right">{item.title}</TooltipContent>
                )}
              </Tooltip>
            );
          })}
        </nav>
      </ScrollArea>

      {/* User Section */}
      <div className="border-t border-sidebar-border p-3">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-sidebar-accent flex items-center justify-center text-sm font-medium">
            JD
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">John Doe</p>
              <p className="text-xs text-sidebar-foreground/50 truncate">
                john@example.com
              </p>
            </div>
          )}
          {!collapsed && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-sidebar-foreground/50 hover:text-sidebar-foreground"
            >
              <Bell className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </aside>
  );
}
