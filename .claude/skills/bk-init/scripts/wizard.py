"""Interactive setup wizard for BrseKit project configuration."""

import sys
from typing import Dict, List, Any


class SetupWizard:
    """Interactive wizard for project setup."""

    def __init__(self):
        self.data: Dict[str, Any] = {}

    def run(self) -> Dict[str, Any]:
        """Run the complete wizard workflow."""
        print("\n=== BrseKit Project Setup Wizard ===\n")

        self._step1_project_info()
        self._step2_project_type()
        self._step3_customer_info()
        self._step4_focus_areas()
        self._step5_vault_config()

        print("\n✓ Setup complete!")
        return self.data

    def _step1_project_info(self):
        """Step 1: Project name and Backlog key."""
        print("Step 1: Project Information")
        print("-" * 40)

        self.data["project_name"] = self._prompt("Project name")
        self.data["backlog_key"] = self._prompt("Backlog project key (e.g., PROJ)")
        print()

    def _step2_project_type(self):
        """Step 2: Project type and methodology."""
        print("Step 2: Project Type & Methodology")
        print("-" * 40)

        print("Project type:")
        print("  1. Project-based (fixed scope, fixed price)")
        print("  2. Labor-based (time & materials)")
        print("  3. Hybrid (combination)")
        project_type = self._choice(["project-based", "labor-based", "hybrid"])
        self.data["project_type"] = project_type

        print("\nMethodology:")
        print("  1. Waterfall (phases, milestones, change requests)")
        print("  2. Agile (sprints, iterations, velocity)")
        print("  3. Hybrid (waterfall phases + agile sprints)")
        methodology = self._choice(["waterfall", "agile", "hybrid"])
        self.data["methodology"] = methodology
        print()

    def _step3_customer_info(self):
        """Step 3: Customer profile."""
        print("Step 3: Customer Profile")
        print("-" * 40)

        self.data["customer_name"] = self._prompt("Customer name")
        self.data["industry"] = self._prompt("Industry (e.g., Finance, Healthcare)")

        print("Timezone:")
        print("  1. JST (Asia/Tokyo)")
        print("  2. PST (America/Los_Angeles)")
        print("  3. EST (America/New_York)")
        print("  4. UTC")
        timezone = self._choice(["JST", "PST", "EST", "UTC"])
        self.data["timezone"] = timezone

        print("\nCommunication style:")
        print("  1. Formal (敬語, detailed reports)")
        print("  2. Casual (友達口調, brief updates)")
        print("  3. Collaborative (mix)")
        comm_style = self._choice(["formal", "casual", "collaborative"])
        self.data["communication_style"] = comm_style
        print()

    def _step4_focus_areas(self):
        """Step 4: PM focus areas and triggers."""
        print("Step 4: PM Focus Areas")
        print("-" * 40)

        print("Select primary focus (comma-separated, e.g., 1,2):")
        options = [
            "change_request_tracking",
            "budget_monitoring",
            "sprint_goal_alignment",
            "quality_metrics",
            "documentation_quality"
        ]
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt.replace('_', ' ').title()}")

        primary = self._multi_choice(options, "Primary focus")
        self.data["primary_focus"] = primary

        print("\nSelect secondary focus (comma-separated, optional):")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt.replace('_', ' ').title()}")

        secondary = self._multi_choice(options, "Secondary focus", allow_empty=True)
        self.data["secondary_focus"] = secondary
        print()

    def _step5_vault_config(self):
        """Step 5: Vault configuration."""
        print("Step 5: Vault Configuration")
        print("-" * 40)

        print("Enable vault for email/Backlog archiving?")
        print("  1. Yes")
        print("  2. No")
        vault_enabled = self._choice(["yes", "no"]) == "yes"
        self.data["vault_enabled"] = vault_enabled

        if vault_enabled:
            print("\nSelect vault sources (comma-separated):")
            print("  1. email")
            print("  2. backlog")
            sources = self._multi_choice(["email", "backlog"], "Vault sources")
            self.data["vault_sources"] = sources

            print("\nSync schedule:")
            print("  1. daily")
            print("  2. weekly")
            print("  3. manual")
            schedule = self._choice(["daily", "weekly", "manual"])
            self.data["sync_schedule"] = schedule
        else:
            self.data["vault_sources"] = []
            self.data["sync_schedule"] = "manual"
        print()

    def _prompt(self, message: str) -> str:
        """Prompt for text input."""
        while True:
            value = input(f"{message}: ").strip()
            if value:
                return value
            print("  ⚠ This field is required.")

    def _choice(self, options: List[str]) -> str:
        """Prompt for single choice."""
        while True:
            try:
                choice = input("Choice: ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                print(f"  ⚠ Invalid choice. Enter 1-{len(options)}.")
            except ValueError:
                print(f"  ⚠ Invalid input. Enter 1-{len(options)}.")

    def _multi_choice(self, options: List[str], label: str, allow_empty: bool = False) -> List[str]:
        """Prompt for multiple choices."""
        while True:
            try:
                choice = input(f"{label} (comma-separated): ").strip()
                if not choice and allow_empty:
                    return []

                indices = [int(c.strip()) - 1 for c in choice.split(",")]
                selected = [options[i] for i in indices if 0 <= i < len(options)]

                if selected or allow_empty:
                    return selected
                print("  ⚠ At least one option required.")
            except (ValueError, IndexError):
                print(f"  ⚠ Invalid input. Enter numbers 1-{len(options)} separated by commas.")
