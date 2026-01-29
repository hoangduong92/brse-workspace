"use client";

import * as React from "react";
import {
  Settings,
  User,
  Bell,
  Shield,
  Palette,
  Globe,
  Key,
  Trash2,
  Save,
  Upload,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

// Types
interface SettingsTab {
  id: string;
  label: string;
  icon: React.ElementType;
}

const settingsTabs: SettingsTab[] = [
  { id: "general", label: "General", icon: Settings },
  { id: "profile", label: "Profile", icon: User },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "security", label: "Security", icon: Shield },
  { id: "appearance", label: "Appearance", icon: Palette },
  { id: "integrations", label: "Integrations", icon: Globe },
];

// Form Input Component
function FormInput({
  label,
  type = "text",
  placeholder,
  value,
  onChange,
  description,
}: {
  label: string;
  type?: string;
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  description?: string;
}) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">{label}</label>
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        className="w-full h-9 rounded-md border bg-background px-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
      />
      {description && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}
    </div>
  );
}

// Toggle Switch Component
function Toggle({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <div className="flex items-start justify-between py-3">
      <div className="space-y-0.5">
        <p className="text-sm font-medium">{label}</p>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
      <button
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={cn(
          "relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors",
          checked ? "bg-primary" : "bg-muted"
        )}
      >
        <span
          className={cn(
            "pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-lg ring-0 transition-transform",
            checked ? "translate-x-4" : "translate-x-0"
          )}
        />
      </button>
    </div>
  );
}

// General Settings Section
function GeneralSettings() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">General Settings</h2>
        <p className="text-sm text-muted-foreground">
          Manage your project settings and preferences
        </p>
      </div>

      <Separator />

      <div className="space-y-4">
        <FormInput
          label="Project Name"
          value="Backlog UI Pro"
          description="This is the display name of your project"
        />
        <FormInput
          label="Project Key"
          value="BUP"
          description="A unique identifier used in issue keys (e.g., BUP-123)"
        />
        <div className="space-y-2">
          <label className="text-sm font-medium">Description</label>
          <textarea
            placeholder="Enter project description..."
            className="w-full min-h-[100px] rounded-md border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none"
            defaultValue="A modern project management tool built with Next.js and shadcn/ui"
          />
        </div>
      </div>

      <Separator />

      <div className="space-y-4">
        <h3 className="text-sm font-semibold">Default Settings</h3>
        <div className="space-y-2">
          <label className="text-sm font-medium">Default Issue Type</label>
          <select className="w-full h-9 rounded-md border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring">
            <option>Task</option>
            <option>Bug</option>
            <option>Feature</option>
            <option>Improvement</option>
          </select>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Default Priority</label>
          <select className="w-full h-9 rounded-md border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring">
            <option>Normal</option>
            <option>High</option>
            <option>Low</option>
          </select>
        </div>
      </div>

      <div className="flex justify-end">
        <Button>
          <Save className="h-4 w-4 mr-2" />
          Save Changes
        </Button>
      </div>
    </div>
  );
}

// Profile Settings Section
function ProfileSettings() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Profile Settings</h2>
        <p className="text-sm text-muted-foreground">
          Manage your personal information and avatar
        </p>
      </div>

      <Separator />

      {/* Avatar */}
      <div className="flex items-center gap-4">
        <Avatar className="h-20 w-20">
          <AvatarFallback className="text-2xl">JD</AvatarFallback>
        </Avatar>
        <div className="space-y-2">
          <Button variant="outline" size="sm">
            <Upload className="h-4 w-4 mr-2" />
            Upload Photo
          </Button>
          <p className="text-xs text-muted-foreground">
            Recommended: Square image, at least 200x200 pixels
          </p>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <FormInput label="First Name" value="John" />
        <FormInput label="Last Name" value="Doe" />
      </div>

      <FormInput
        label="Email"
        type="email"
        value="john@example.com"
        description="Your email is used for notifications and login"
      />

      <FormInput
        label="Job Title"
        value="Senior Developer"
        placeholder="Enter your job title"
      />

      <div className="space-y-2">
        <label className="text-sm font-medium">Bio</label>
        <textarea
          placeholder="Tell us about yourself..."
          className="w-full min-h-[80px] rounded-md border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none"
        />
      </div>

      <div className="flex justify-end">
        <Button>
          <Save className="h-4 w-4 mr-2" />
          Save Profile
        </Button>
      </div>
    </div>
  );
}

// Notifications Settings Section
function NotificationsSettings() {
  const [emailNotifications, setEmailNotifications] = React.useState(true);
  const [pushNotifications, setPushNotifications] = React.useState(true);
  const [mentionNotifications, setMentionNotifications] = React.useState(true);
  const [assignmentNotifications, setAssignmentNotifications] = React.useState(true);
  const [statusNotifications, setStatusNotifications] = React.useState(false);
  const [weeklyDigest, setWeeklyDigest] = React.useState(true);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Notification Settings</h2>
        <p className="text-sm text-muted-foreground">
          Configure how and when you receive notifications
        </p>
      </div>

      <Separator />

      <div className="space-y-1">
        <h3 className="text-sm font-semibold">Delivery Methods</h3>
        <Toggle
          label="Email Notifications"
          description="Receive notifications via email"
          checked={emailNotifications}
          onChange={setEmailNotifications}
        />
        <Toggle
          label="Push Notifications"
          description="Receive browser push notifications"
          checked={pushNotifications}
          onChange={setPushNotifications}
        />
      </div>

      <Separator />

      <div className="space-y-1">
        <h3 className="text-sm font-semibold">Notification Types</h3>
        <Toggle
          label="Mentions"
          description="When someone mentions you in a comment"
          checked={mentionNotifications}
          onChange={setMentionNotifications}
        />
        <Toggle
          label="Assignments"
          description="When an issue is assigned to you"
          checked={assignmentNotifications}
          onChange={setAssignmentNotifications}
        />
        <Toggle
          label="Status Changes"
          description="When issues you're watching change status"
          checked={statusNotifications}
          onChange={setStatusNotifications}
        />
        <Toggle
          label="Weekly Digest"
          description="Receive a weekly summary of project activity"
          checked={weeklyDigest}
          onChange={setWeeklyDigest}
        />
      </div>

      <div className="flex justify-end">
        <Button>
          <Save className="h-4 w-4 mr-2" />
          Save Preferences
        </Button>
      </div>
    </div>
  );
}

// Security Settings Section
function SecuritySettings() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Security Settings</h2>
        <p className="text-sm text-muted-foreground">
          Manage your password and security preferences
        </p>
      </div>

      <Separator />

      <div className="space-y-4">
        <h3 className="text-sm font-semibold">Change Password</h3>
        <FormInput label="Current Password" type="password" placeholder="Enter current password" />
        <FormInput label="New Password" type="password" placeholder="Enter new password" />
        <FormInput label="Confirm Password" type="password" placeholder="Confirm new password" />
        <Button>Update Password</Button>
      </div>

      <Separator />

      <div className="space-y-4">
        <h3 className="text-sm font-semibold">Two-Factor Authentication</h3>
        <div className="flex items-center justify-between p-4 rounded-lg border">
          <div>
            <p className="font-medium">Two-Factor Authentication</p>
            <p className="text-sm text-muted-foreground">
              Add an extra layer of security to your account
            </p>
          </div>
          <Badge variant="secondary">Not enabled</Badge>
        </div>
        <Button variant="outline">
          <Key className="h-4 w-4 mr-2" />
          Enable 2FA
        </Button>
      </div>

      <Separator />

      <div className="space-y-4">
        <h3 className="text-sm font-semibold">Active Sessions</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 rounded-lg border">
            <div>
              <p className="text-sm font-medium">Chrome on Windows</p>
              <p className="text-xs text-muted-foreground">Current session • Tokyo, Japan</p>
            </div>
            <Badge variant="success">Active</Badge>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg border">
            <div>
              <p className="text-sm font-medium">Safari on macOS</p>
              <p className="text-xs text-muted-foreground">Last active 2 days ago • Tokyo, Japan</p>
            </div>
            <Button variant="ghost" size="sm">Revoke</Button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Appearance Settings Section
function AppearanceSettings() {
  const [theme, setTheme] = React.useState("system");
  const [compactMode, setCompactMode] = React.useState(false);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Appearance Settings</h2>
        <p className="text-sm text-muted-foreground">
          Customize the look and feel of the application
        </p>
      </div>

      <Separator />

      <div className="space-y-4">
        <h3 className="text-sm font-semibold">Theme</h3>
        <div className="grid grid-cols-3 gap-3">
          {["light", "dark", "system"].map((t) => (
            <button
              key={t}
              onClick={() => setTheme(t)}
              className={cn(
                "p-4 rounded-lg border-2 text-center capitalize transition-colors",
                theme === t ? "border-primary bg-primary/5" : "border-border hover:bg-muted"
              )}
            >
              <div className={cn(
                "w-full h-12 rounded-md mb-2",
                t === "light" && "bg-white border",
                t === "dark" && "bg-slate-900",
                t === "system" && "bg-gradient-to-r from-white to-slate-900"
              )} />
              <span className="text-sm font-medium">{t}</span>
            </button>
          ))}
        </div>
      </div>

      <Separator />

      <div className="space-y-1">
        <h3 className="text-sm font-semibold">Display</h3>
        <Toggle
          label="Compact Mode"
          description="Reduce spacing and padding for a denser layout"
          checked={compactMode}
          onChange={setCompactMode}
        />
      </div>

      <div className="flex justify-end">
        <Button>
          <Save className="h-4 w-4 mr-2" />
          Save Preferences
        </Button>
      </div>
    </div>
  );
}

// Integrations Settings Section
function IntegrationsSettings() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Integrations</h2>
        <p className="text-sm text-muted-foreground">
          Connect external services and tools
        </p>
      </div>

      <Separator />

      <div className="space-y-4">
        {[
          { name: "GitHub", description: "Sync issues with GitHub", connected: true },
          { name: "Slack", description: "Send notifications to Slack", connected: true },
          { name: "GitLab", description: "Sync issues with GitLab", connected: false },
          { name: "Jira", description: "Import issues from Jira", connected: false },
          { name: "Google Drive", description: "Attach files from Google Drive", connected: false },
        ].map((integration) => (
          <div
            key={integration.name}
            className="flex items-center justify-between p-4 rounded-lg border"
          >
            <div>
              <p className="font-medium">{integration.name}</p>
              <p className="text-sm text-muted-foreground">{integration.description}</p>
            </div>
            {integration.connected ? (
              <div className="flex items-center gap-2">
                <Badge variant="success">Connected</Badge>
                <Button variant="ghost" size="sm">Disconnect</Button>
              </div>
            ) : (
              <Button variant="outline" size="sm">Connect</Button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Main Settings Content
export function SettingsContent() {
  const [activeTab, setActiveTab] = React.useState("general");

  const renderContent = () => {
    switch (activeTab) {
      case "general":
        return <GeneralSettings />;
      case "profile":
        return <ProfileSettings />;
      case "notifications":
        return <NotificationsSettings />;
      case "security":
        return <SecuritySettings />;
      case "appearance":
        return <AppearanceSettings />;
      case "integrations":
        return <IntegrationsSettings />;
      default:
        return <GeneralSettings />;
    }
  };

  return (
    <div className="flex gap-6">
      {/* Sidebar Navigation */}
      <nav className="w-48 shrink-0 space-y-1">
        {settingsTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex items-center gap-3 w-full px-3 py-2 rounded-md text-sm transition-colors",
              activeTab === tab.id
                ? "bg-primary/10 text-primary font-medium"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}

        <Separator className="my-4" />

        <button className="flex items-center gap-3 w-full px-3 py-2 rounded-md text-sm text-red-500 hover:bg-red-50 transition-colors">
          <Trash2 className="h-4 w-4" />
          Delete Project
        </button>
      </nav>

      {/* Content Area */}
      <div className="flex-1 rounded-lg border bg-card p-6">{renderContent()}</div>
    </div>
  );
}
