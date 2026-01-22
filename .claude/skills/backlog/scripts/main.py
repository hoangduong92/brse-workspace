"""Main orchestration for Backlog Automation Skill.

Workflow:
1. Parse ticket ID and flags
2. Fetch source issue from Nulab API
3. Detect language and translate content
4. Detect task type and load template
5. Apply template with variable substitution
6. Create destination issue (same project for MVP)
7. Copy attachments from source
8. Create subtasks if applicable
9. Return result
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from models import TaskType, Result, Language
from nulab_client import BacklogAPI, BacklogAPIError
from translator import TranslationService
from templates import TemplateManager, TemplateError

# Load environment variables from skill directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_task_type(type_str: Optional[str]) -> Optional[TaskType]:
    """Convert CLI type string to TaskType enum.

    Args:
        type_str: Type string from CLI (feature, scenario, issue)

    Returns:
        TaskType enum or None
    """
    if not type_str:
        return None

    type_map = {
        "feature": TaskType.FEATURE_DEV,
        "scenario": TaskType.UPLOAD_SCENARIO,
        "issue": TaskType.INVESTIGATE_ISSUE
    }

    return type_map.get(type_str.lower())


def create_ticket(
    ticket_id: str,
    dry_run: bool = False,
    manual_type: Optional[TaskType] = None,
    verbose: bool = False
) -> Result:
    """Main workflow to copy ticket from source to destination backlog.

    Args:
        ticket_id: Source ticket ID (e.g., "HB21373-123")
        dry_run: If True, skip actual creation
        manual_type: Optional manual task type override
        verbose: Enable verbose logging

    Returns:
        Result object with success status and created issue details
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Validate environment
        space_url = os.getenv("NULAB_SPACE_URL")
        api_key = os.getenv("NULAB_API_KEY")
        project_id = os.getenv("NULAB_PROJECT_ID")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if not all([space_url, api_key, project_id, anthropic_key]):
            missing = []
            if not space_url:
                missing.append("NULAB_SPACE_URL")
            if not api_key:
                missing.append("NULAB_API_KEY")
            if not project_id:
                missing.append("NULAB_PROJECT_ID")
            if not anthropic_key:
                missing.append("ANTHROPIC_API_KEY")
            return Result(
                success=False,
                error=f"Missing environment variables: {', '.join(missing)}"
            )

        # Initialize clients
        logger.info("Initializing API clients...")
        api = BacklogAPI(space_url=space_url, api_key=api_key)
        translator = TranslationService(
            api_key=anthropic_key,
            model=os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-20241022")
        )
        template_mgr = TemplateManager()

        # 1. Fetch source issue
        logger.info(f"Fetching issue {ticket_id}")
        source_issue = api.get_issue(ticket_id)
        logger.info(f"Found: {source_issue.summary}")

        # 2. Detect language and translate
        logger.info("Detecting language and translating...")
        source_lang = translator.detector.detect(source_issue.summary)
        target_lang = translator.detector.get_target_language(source_lang)

        translated_summary = translator.translate(source_issue.summary, target_lang)
        translated_description = translator.translate(
            source_issue.description or "",
            target_lang
        )

        logger.info(f"Translated from {source_lang.value} to {target_lang.value}")

        # 3. Detect task type and load template
        task_type = template_mgr.detect_task_type(source_issue, manual_type)
        template = template_mgr.get_template(task_type)

        if not template:
            return Result(
                success=False,
                source_issue=source_issue,
                error=f"Template not found for task type: {task_type.value}"
            )

        logger.info(f"Using template: {template.name} ({task_type.value})")

        # 4. Build context for template substitution
        context = {
            "project_id": project_id,
            "source_ticket_id": ticket_id,
            "original_summary": source_issue.summary,
            "translated_summary": translated_summary,
            "original_description": source_issue.description or "",
            "translated_description": translated_description
        }

        # 5. Apply template
        issue_data = template_mgr.apply_template(template, context)

        # Use source issue's priority instead of template default
        issue_data["priorityId"] = source_issue.priority_id

        # 6. Handle dry run
        if dry_run:
            logger.info("[DRY RUN] Would create issue:")
            logger.info(f"  Summary: {issue_data['summary']}")
            logger.info(f"  Priority ID: {issue_data['priorityId']}")
            if template.subtasks:
                logger.info(f"  Subtasks: {len(template.subtasks)}")
            return Result(
                success=True,
                source_issue=source_issue,
                dry_run=True,
                data=issue_data
            )

        # 7. Get project info for issue type
        project = api.get_project(project_id)

        # Get first issue type ID (assuming standard setup)
        # In production, this should be configurable
        issue_type_id = source_issue.issue_type_id

        # 8. Create destination issue
        logger.info("Creating destination issue...")
        dest_issue = api.create_issue(
            project_id=project.id,
            summary=issue_data["summary"],
            description=issue_data["description"],
            issueTypeId=issue_type_id,
            priorityId=issue_data["priorityId"]
        )
        logger.info(f"Created issue: {dest_issue.key_id}")

        # 9. Copy attachments
        attachments_copied = 0
        if source_issue.attachments:
            logger.info(f"Copying {len(source_issue.attachments)} attachments...")
            copied = api.copy_attachments(ticket_id, dest_issue.key_id)
            attachments_copied = len(copied)
            logger.info(f"Copied {attachments_copied} attachments")

        # 10. Create subtasks if applicable
        subtasks = []
        if template.subtasks:
            logger.info(f"Creating {len(template.subtasks)} subtasks...")
            subtask_data_list = template_mgr.generate_subtasks(
                template, dest_issue.id, context
            )

            for subtask_data in subtask_data_list:
                subtask = api.create_subtask(
                    project_id=project.id,
                    parent_id=dest_issue.id,
                    summary=subtask_data["summary"],
                    issueTypeId=issue_type_id,
                    priorityId=issue_data["priorityId"]
                )
                subtasks.append(subtask)
                logger.info(f"  Created subtask: {subtask.summary[:50]}...")

        # 11. Add reference comment to source issue
        comment = f"Copied to internal backlog: {dest_issue.key_id}"
        try:
            api.add_comment(ticket_id, comment)
            logger.info("Added reference comment to source issue")
        except BacklogAPIError as e:
            logger.warning(f"Could not add comment to source: {e}")

        return Result(
            success=True,
            source_issue=source_issue,
            destination_issue=dest_issue,
            subtasks=subtasks,
            attachments_copied=attachments_copied
        )

    except BacklogAPIError as e:
        logger.error(f"Backlog API error: {e}")
        return Result(success=False, error=f"API error: {e}")
    except TemplateError as e:
        logger.error(f"Template error: {e}")
        return Result(success=False, error=f"Template error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return Result(success=False, error=str(e))


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Copy ticket from customer backlog to internal backlog with translation"
    )
    parser.add_argument(
        "ticket_id",
        help="Source ticket ID (e.g., HB21373-123)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without creating ticket"
    )
    parser.add_argument(
        "--type",
        choices=["feature", "scenario", "issue"],
        help="Manual task type override (default: auto-detect)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Convert type string to enum
    manual_type = parse_task_type(args.type)

    # Execute workflow
    result = create_ticket(
        ticket_id=args.ticket_id,
        dry_run=args.dry_run,
        manual_type=manual_type,
        verbose=args.verbose
    )

    # Output result
    if result.success:
        if result.dry_run:
            print(f"\n[DRY RUN] Would create ticket from {args.ticket_id}")
            print(f"  Summary: {result.data['summary']}")
            print(f"  Priority ID: {result.data['priorityId']}")
        else:
            dest = result.destination_issue
            print(f"\n Created ticket: {dest.key_id}")
            print(f"  Summary: {dest.summary}")
            if result.subtasks:
                print(f"  Subtasks: {len(result.subtasks)}")
            if result.attachments_copied > 0:
                print(f"  Attachments copied: {result.attachments_copied}")
            print(f"\n  URL: https://{os.getenv('NULAB_SPACE_URL')}/view/{dest.key_id}")
    else:
        print(f"\n Failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
