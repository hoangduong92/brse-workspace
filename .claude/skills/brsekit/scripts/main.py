#!/usr/bin/env python3
"""BrseKit CLI - Multi-project management."""
import argparse
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib"))

try:
    from project_manager import ProjectManager
except ImportError:
    ProjectManager = None


def cmd_list(args):
    """List all projects."""
    if not ProjectManager:
        print("Error: ProjectManager not available")
        return

    pm = ProjectManager()
    projects = pm.list_projects()

    if not projects:
        print("No projects found.")
        print("Create one with: /bk-init PROJECT_NAME")
        return

    print(f"## Projects ({len(projects)})\n")
    for name in sorted(projects):
        context = pm.get_context(name)
        if context:
            project_info = context.get("project", {})
            desc = project_info.get("description", "")
            backlog = project_info.get("backlog_key", "")
            print(f"- **{name}** ({backlog})")
            if desc:
                print(f"  {desc[:60]}...")
        else:
            print(f"- **{name}** (no context.yaml)")


def cmd_info(args):
    """Show project info."""
    if not ProjectManager:
        print("Error: ProjectManager not available")
        return

    pm = ProjectManager()
    name = args.project

    if not pm.project_exists(name):
        print(f"Project '{name}' not found")
        print(f"Create with: /bk-init {name}")
        return

    context = pm.get_context(name) or {}
    project = context.get("project", {})

    print(f"## {name}\n")
    print(f"**Path:** {pm.get_project_path(name)}")
    print(f"**Backlog Key:** {project.get('backlog_key', 'N/A')}")
    print(f"**Type:** {project.get('type', 'N/A')}")
    print(f"**Description:** {project.get('description', 'N/A')}")

    # Check files
    path = pm.get_project_path(name)
    print("\n**Files:**")
    print(f"  context.yaml: {'[ok]' if (path / 'context.yaml').exists() else '[missing]'}")
    print(f"  .env: {'[ok]' if (path / '.env').exists() else '[missing]'}")
    print(f"  vault/: {'[ok]' if (path / 'vault').is_dir() else '[missing]'}")
    print(f"  glossary.json: {'[ok]' if (path / 'glossary.json').exists() else '[optional]'}")


def cmd_help(args):
    """Show help."""
    print("""
## BrseKit v1.1 - Multi-Project Toolkit

### Project Management
  /brsekit list              List all projects
  /brsekit info PROJECT      Show project details
  /bk-init PROJECT           Create new project

### Daily Workflow
  /bk-track status PROJECT   Project status report
  /bk-morning PROJECT        Morning brief
  /bk-recall search "..."    Search project memory

### Task Management
  /bk-capture task "..."     Capture tasks from text
  /bk-spec refine "..."      Refine requirements

### Translation
  /bk-convert file.xlsx      Translate Excel
  /bk-write "email"          Japanese business writing

### Memory (User-level)
  /cc-memory search "..."    Search all memories
  /cc-memory recent          Recent sessions

### Examples
  /bk-track status HB21373 --lang ja
  /bk-recall search "deadline" --project HB21373
  /bk-init NEW_PROJECT
""")


def cmd_version(args):
    """Show version."""
    print("BrseKit v1.1.0")
    print("Multi-project architecture")


def main():
    parser = argparse.ArgumentParser(
        description="BrseKit - Multi-project toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command")

    # list
    subparsers.add_parser("list", help="List all projects")

    # info
    info_p = subparsers.add_parser("info", help="Show project info")
    info_p.add_argument("project", help="Project name")

    # help
    subparsers.add_parser("help", help="Show help")

    # version
    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()

    handlers = {
        "list": cmd_list,
        "info": cmd_info,
        "help": cmd_help,
        "version": cmd_version,
    }

    if not args.command:
        cmd_help(args)
        return

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
