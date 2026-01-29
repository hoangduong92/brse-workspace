"use client";

import * as React from "react";
import {
  Search,
  Plus,
  MoreHorizontal,
  Mail,
  Shield,
  ShieldCheck,
  Crown,
  UserX,
  Calendar,
  Filter,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

// Types
interface Member {
  id: string;
  name: string;
  email: string;
  initials: string;
  avatar?: string;
  role: "owner" | "admin" | "member" | "guest";
  status: "active" | "pending" | "inactive";
  joinedAt: string;
  lastActive: string;
  issuesAssigned: number;
  issuesCompleted: number;
}

// Role config
const roleConfig = {
  owner: { label: "Owner", icon: Crown, color: "text-amber-500" },
  admin: { label: "Admin", icon: ShieldCheck, color: "text-blue-500" },
  member: { label: "Member", icon: Shield, color: "text-slate-500" },
  guest: { label: "Guest", icon: UserX, color: "text-slate-400" },
};

const statusConfig = {
  active: { label: "Active", variant: "success" as const },
  pending: { label: "Pending", variant: "warning" as const },
  inactive: { label: "Inactive", variant: "secondary" as const },
};

// Mock data
const mockMembers: Member[] = [
  {
    id: "1",
    name: "John Doe",
    email: "john@example.com",
    initials: "JD",
    role: "owner",
    status: "active",
    joinedAt: "Jan 1, 2024",
    lastActive: "Just now",
    issuesAssigned: 24,
    issuesCompleted: 18,
  },
  {
    id: "2",
    name: "Jane Smith",
    email: "jane@example.com",
    initials: "JS",
    role: "admin",
    status: "active",
    joinedAt: "Jan 5, 2024",
    lastActive: "2 hours ago",
    issuesAssigned: 18,
    issuesCompleted: 15,
  },
  {
    id: "3",
    name: "Mike Wilson",
    email: "mike@example.com",
    initials: "MW",
    role: "member",
    status: "active",
    joinedAt: "Jan 10, 2024",
    lastActive: "1 day ago",
    issuesAssigned: 12,
    issuesCompleted: 8,
  },
  {
    id: "4",
    name: "Sarah Johnson",
    email: "sarah@example.com",
    initials: "SJ",
    role: "member",
    status: "active",
    joinedAt: "Jan 15, 2024",
    lastActive: "3 hours ago",
    issuesAssigned: 15,
    issuesCompleted: 12,
  },
  {
    id: "5",
    name: "Alex Chen",
    email: "alex@example.com",
    initials: "AC",
    role: "member",
    status: "pending",
    joinedAt: "Jan 20, 2024",
    lastActive: "Never",
    issuesAssigned: 0,
    issuesCompleted: 0,
  },
  {
    id: "6",
    name: "Emily Brown",
    email: "emily@example.com",
    initials: "EB",
    role: "guest",
    status: "active",
    joinedAt: "Jan 18, 2024",
    lastActive: "5 days ago",
    issuesAssigned: 3,
    issuesCompleted: 2,
  },
];

// Stats Card
function StatCard({ title, value, subtitle }: { title: string; value: number; subtitle: string }) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-sm text-muted-foreground">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
    </div>
  );
}

// Member Card
function MemberCard({ member }: { member: Member }) {
  const RoleIcon = roleConfig[member.role].icon;

  return (
    <div className="flex items-center gap-4 p-4 rounded-lg border bg-card hover:shadow-sm transition-shadow cursor-pointer">
      {/* Avatar */}
      <Avatar className="h-12 w-12">
        {member.avatar && <AvatarImage src={member.avatar} alt={member.name} />}
        <AvatarFallback className="text-sm">{member.initials}</AvatarFallback>
      </Avatar>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold truncate">{member.name}</h3>
          <RoleIcon className={cn("h-4 w-4", roleConfig[member.role].color)} />
          <Badge variant={statusConfig[member.status].variant} className="text-xs">
            {statusConfig[member.status].label}
          </Badge>
        </div>
        <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Mail className="h-3 w-3" />
            {member.email}
          </span>
          <span className="hidden sm:flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            Joined {member.joinedAt}
          </span>
        </div>
      </div>

      {/* Stats */}
      <div className="hidden md:flex items-center gap-6 text-sm">
        <div className="text-center">
          <p className="font-semibold">{member.issuesAssigned}</p>
          <p className="text-xs text-muted-foreground">Assigned</p>
        </div>
        <div className="text-center">
          <p className="font-semibold">{member.issuesCompleted}</p>
          <p className="text-xs text-muted-foreground">Completed</p>
        </div>
      </div>

      {/* Last Active */}
      <div className="hidden lg:block text-sm text-muted-foreground text-right w-24">
        <p className="text-xs">Last active</p>
        <p>{member.lastActive}</p>
      </div>

      {/* Actions */}
      <Button variant="ghost" size="icon">
        <MoreHorizontal className="h-4 w-4" />
      </Button>
    </div>
  );
}

// Main Members Content
export function MembersContent() {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [roleFilter, setRoleFilter] = React.useState<string>("all");

  const filteredMembers = mockMembers.filter((member) => {
    const matchesSearch =
      member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = roleFilter === "all" || member.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const activeCount = mockMembers.filter((m) => m.status === "active").length;
  const pendingCount = mockMembers.filter((m) => m.status === "pending").length;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Members</h1>
          <p className="text-muted-foreground mt-1">
            Manage your team members and their permissions
          </p>
        </div>
        <Button size="sm">
          <Plus className="h-4 w-4 mr-2" />
          Invite Member
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Members" value={mockMembers.length} subtitle="In this project" />
        <StatCard title="Active" value={activeCount} subtitle="Currently active" />
        <StatCard title="Pending" value={pendingCount} subtitle="Awaiting acceptance" />
        <StatCard
          title="Avg. Completion"
          value={Math.round(
            (mockMembers.reduce((acc, m) => acc + m.issuesCompleted, 0) /
              Math.max(mockMembers.reduce((acc, m) => acc + m.issuesAssigned, 0), 1)) *
              100
          )}
          subtitle="Issue completion rate %"
        />
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search members..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-9 rounded-md border bg-background pl-9 pr-4 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="h-9 rounded-md border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="all">All Roles</option>
            <option value="owner">Owner</option>
            <option value="admin">Admin</option>
            <option value="member">Member</option>
            <option value="guest">Guest</option>
          </select>
        </div>
      </div>

      {/* Members List */}
      <div className="space-y-3">
        {filteredMembers.map((member) => (
          <MemberCard key={member.id} member={member} />
        ))}

        {filteredMembers.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            <p>No members found matching your criteria</p>
          </div>
        )}
      </div>
    </div>
  );
}
