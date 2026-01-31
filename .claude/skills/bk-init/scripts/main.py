#!/usr/bin/env python3
"""bk-init - BrseKit project setup wizard CLI."""

import argparse
import os
import shutil
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib"))

from wizard import SetupWizard
from validator import validate_backlog_connection, validate_config, validate_env_vars
from config_generator import generate_config, save_config, format_config_yaml
from env_setup import run_env_setup, check_env_exists


def print_quick_start(project_name: str = None):
    """Print quick start guide after setup."""
    proj_arg = f" {project_name}" if project_name else ""
    print("\n" + "=" * 50)
    print("           BrseKit Ready!")
    print("=" * 50)
    print(f"""
Quick Start Commands:
  /bk-track status{proj_arg}     Check project health
  /bk-track report{proj_arg}     Generate weekly report
  /bk-recall sync --project {project_name or 'PROJECT'}      Start syncing data
  /bk-morning{proj_arg}          Get morning brief
  /brsekit help            Full documentation

Common Workflows:
  1. Morning routine:  /bk-morning{proj_arg}
  2. Check progress:   /bk-track status{proj_arg} --lang ja
  3. Weekly report:    /bk-track report{proj_arg} --format pptx
  4. Parse email:      /bk-capture task "email content..."
  5. Search context:   /bk-recall search "keyword" --project {project_name or 'PROJECT'}
""")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="BrseKit project setup wizard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bk-init HB21373            Create project in projects/HB21373/
  bk-init                    Run interactive wizard (current directory)
  bk-init HB21373 --env-only Only setup .env for project HB21373
  bk-init --fresh            Reconfigure everything from scratch
  bk-init --output ./        Save config to current directory
  bk-init --validate         Validate existing config
  bk-init --check-env        Check environment variables
        """
    )

    parser.add_argument(
        "project",
        nargs="?",
        help="Project name (creates projects/PROJECT/ directory)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output directory for project-context.yaml and .env"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing project-context.yaml"
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Check required environment variables"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show config without saving"
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Force reconfigure everything (ignore existing .env and config)"
    )
    parser.add_argument(
        "--env-only",
        action="store_true",
        help="Only setup .env file, skip project configuration"
    )

    args = parser.parse_args()

    # Determine output directory
    project_name = args.project
    if project_name:
        # Create in projects/ directory
        output_dir = Path.cwd() / "projects" / project_name
    elif args.output:
        output_dir = Path(args.output)
    else:
        output_dir = Path.cwd()

    # Check environment variables
    if args.check_env:
        success, message = validate_env_vars()
        print(message)
        sys.exit(0 if success else 1)

    # Validate existing config
    if args.validate:
        config_path = output_dir / "project-context.yaml"
        if not config_path.exists():
            print(f"Config not found: {config_path}")
            sys.exit(1)

        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        success, message = validate_config(config)
        print(message)
        sys.exit(0 if success else 1)

    # Banner
    print("\n" + "=" * 50)
    print("       BrseKit Project Setup Wizard")
    print("=" * 50)

    # Step 0: Environment setup (credentials)
    print("\n[Phase 1] Environment Setup")
    success, credentials = run_env_setup(output_dir, force=args.fresh)

    if not success:
        print("\nSetup cancelled.")
        sys.exit(1)

    # Load credentials into environment
    from dotenv import load_dotenv
    env_path = output_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    # Exit early if env-only mode
    if args.env_only:
        print("\n.env setup complete!")
        print("\nNext: Run /bk-init again to complete project configuration.")
        sys.exit(0)

    # Step 1-5: Project configuration wizard
    print("\n[Phase 2] Project Configuration")
    wizard = SetupWizard()

    try:
        wizard_data = wizard.run()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)

    # Generate config
    config = generate_config(wizard_data)

    # Validate generated config
    valid, message = validate_config(config)
    if not valid:
        print(f"\n{message}")
        sys.exit(1)

    # Validate Backlog connection with project key
    space_url = os.getenv("BACKLOG_SPACE_URL")
    api_key = os.getenv("BACKLOG_API_KEY")

    if space_url and api_key:
        print("\n[Phase 3] Verification")
        print("-" * 40)
        print("Validating Backlog connection...")
        success, message = validate_backlog_connection(
            space_url,
            api_key,
            config["project"]["backlog_key"]
        )
        status = "OK" if success else "WARN"
        print(f"  Connection: {status} - {message}")

        if not success:
            print("  Continuing without Backlog validation.")

    # Output
    if args.dry_run:
        print("\n--- Generated Config ---\n")
        print(format_config_yaml(config))
        return

    output_path = output_dir / "project-context.yaml"
    saved_path = save_config(config, output_path)

    print(f"\nConfig saved to: {saved_path}")

    # Create vault directory for multi-project structure
    vault_dir = output_dir / "vault"
    vault_dir.mkdir(exist_ok=True)

    # Also create canonical context.yaml (copy from project-context.yaml)
    context_path = output_dir / "context.yaml"
    if not context_path.exists():
        shutil.copy(saved_path, context_path)

    # Quick start guide
    print_quick_start(project_name)

    # Summary
    print("Setup Summary:")
    print(f"  Output dir:           {output_dir}")
    print(f"  .env:                 {output_dir / '.env'}")
    print(f"  context.yaml:         {context_path}")
    print(f"  vault/:               {vault_dir}")
    print(f"  Project:              {config['project']['name']}")
    print(f"  Backlog:              {config['project']['backlog_key']}")
    print(f"  Type:                 {config['project']['type']}")
    print()


if __name__ == "__main__":
    main()
