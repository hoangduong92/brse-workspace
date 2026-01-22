# Phase 05: Main Skill Logic

**Context**: Parent plan [../plan.md](plan.md)

## Overview

**Date**: 2026-01-22
**Description**: Implement main skill orchestration logic integrating API client, translator, and templates
**Priority**: P1
**Status**: pending
**Effort**: 3h

## Context Links

- Depends on: [Phase 02](phase-02-nulab-api-client.md), [Phase 03](phase-03-claude-translation.md), [Phase 04](phase-04-template-system.md)
- Research: [../research/researcher-02-claude-skills.md](research/researcher-02-claude-skills.md)

## Key Insights

- Orchestrate all components in main flow
- Handle all error scenarios gracefully
- Provide clear user feedback
- Support dry-run mode for testing
- **[VALIDATED]** Single API key for MVP (same project source/destination)
- **[VALIDATED]** Copy priority from source issue (not template default)
- **[VALIDATED]** Copy attachments from source to destination
- **[VALIDATED]** No auto-rollback on failure (manual cleanup only)

## Requirements

### Functional
- Parse ticket ID from slash command
- **[VALIDATED]** Parse `--type` flag for manual task type override
- Fetch source issue from Nulab API
- Detect language and translate content
- Detect task type and apply template
- Create destination issue (same project for MVP)
- **[VALIDATED]** Copy attachments from source to destination
- **[VALIDATED]** Use source issue's priority (not template default)
- Create subtasks if applicable
- Return result to user

### Non-Functional
- Total execution time < 10 seconds
- Clear error messages for failures
- **[VALIDATED]** Manual cleanup on failure (no auto-rollback)

## Architecture

```python
# [VALIDATED] Add manual_type parameter
def main(ticket_id: str, dry_run: bool = False, manual_type: TaskType = None) -> Result:
    # 1. Parse ticket ID
    # 2. Fetch source issue
    # 3. Detect language
    # 4. Translate content
    # 5. Detect task type (with manual override)
    # 6. Load template
    # 7. Apply template
    # 8. Create destination issue (if not dry_run)
    # 9. Copy attachments (if not dry_run)
    # 10. Create subtasks (if not dry_run)
    # 11. Return result

class Result:
    success: bool
    source_issue: Issue
    destination_issue: Issue | None
    subtasks: list[Issue]
    attachments_copied: int  # [VALIDATED] Track attachments
    error: str | None
```

## Related Code Files

### Modify
- `.claude/skills/backlog/scripts/main.py`
- `.claude/skills/backlog/SKILL.md`

### Create
- `.claude/skills/backlog/tests/test_main_integration.py`

## Implementation Steps

1. **Update SKILL.md**
   ```markdown
   ---
   name: backlog
   description: Automate ticket creation from customer backlog to internal backlog with AI translation (JA ↔ VI) and dynamic task templates
   ---

   # Usage

   Trigger via slash command:
   `/backlog create-ticket HB21373-123`

   **[VALIDATED]** With manual type override:
   `/backlog create-ticket HB21373-123 --type=feature`

   Or invoke skill:
   "Copy ticket HB21373-123 from customer backlog"

   # Environment Variables

   See `.env.example` for required configuration.

   # Implementation

   Main workflow:
   1. Parse ticket ID
   2. Fetch source issue
   3. Translate content (JA ↔ VI)
   4. Apply template (by task type)
   5. Create destination issue
   6. Create subtasks (if dev task)
   ```

2. **Implement main orchestration** (`main.py`)
   ```python
   import os
   import logging
   from dotenv import load_dotenv

   from nulab_client import BacklogAPI
   from translator import TranslationService, Language
   from templates import TemplateManager, TaskType
   from models import Issue

   load_dotenv()
   logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

   def create_ticket(ticket_id: str, dry_run: bool = False) -> dict:
       """
       Main workflow to copy ticket from source to destination backlog.

       Args:
           ticket_id: Source ticket ID (e.g., "HB21373-123")
           dry_run: If True, skip actual creation

       Returns:
           dict with success status and created issue details
       """
       try:
           # Initialize clients
           source_api = BacklogAPI(
               space_url=os.getenv("NULAB_SPACE_URL"),
               api_key=os.getenv("NULAB_SOURCE_API_KEY")
           )
           dest_api = BacklogAPI(
               space_url=os.getenv("NULAB_SPACE_URL"),
               api_key=os.getenv("NULAB_DEST_API_KEY")
           )
           translator = TranslationService(api_key=os.getenv("ANTHROPIC_API_KEY"))
           template_mgr = TemplateManager()

           # 1. Fetch source issue
           logging.info(f"Fetching issue {ticket_id}")
           source_issue = source_api.get_issue(ticket_id)

           # 2. Detect language and translate
           source_lang = translator.detector.detect(source_issue.summary)
           target_lang = Language.VIETNAMESE if source_lang == Language.JAPANESE else Language.JAPANESE

           logging.info(f"Translating from {source_lang.value} to {target_lang.value}")
           translated_summary = translator.translate(source_issue.summary, target_lang)
           translated_description = translator.translate(source_issue.description, target_lang)

           # 3. Detect task type and load template
           task_type = template_mgr.detect_task_type(source_issue)
           template = template_mgr.templates[task_type]

           logging.info(f"Detected task type: {task_type.value}")

           # 4. Apply template
           context = {
               "project_id": os.getenv("NULAB_SOURCE_PROJECT_ID"),
               "original_summary": source_issue.summary,
               "translated_summary": translated_summary,
               "original_description": source_issue.description,
               "translated_description": translated_description
           }

           issue_data = template_mgr.apply_template(template, context)
           issue_data["projectId"] = int(os.getenv("NULAB_DEST_PROJECT_ID"))

           # 5. Create destination issue
           if dry_run:
               logging.info("[DRY RUN] Would create issue:")
               logging.info(f"  Summary: {issue_data['summary']}")
               return {"success": True, "dry_run": True, "data": issue_data}

           logging.info("Creating destination issue")
           dest_issue = dest_api.create_issue(
               project_id=issue_data["projectId"],
               **{k: v for k, v in issue_data.items() if k != "projectId"}
           )

           # 6. Create subtasks if applicable
           subtasks = []
           if template.subtasks:
               logging.info(f"Creating {len(template.subtasks)} subtasks")
               subtask_data_list = template_mgr.generate_subtasks(
                   template, dest_issue.id, context
               )
               for subtask_data in subtask_data_list:
                   subtask = dest_api.create_subtask(
                       project_id=issue_data["projectId"],
                       parent_id=dest_issue.id,
                       **subtask_data
                   )
                   subtasks.append(subtask)

           return {
               "success": True,
               "source_issue": source_issue,
               "destination_issue": dest_issue,
               "subtasks": subtasks
           }

       except Exception as e:
           logging.error(f"Failed to create ticket: {e}")
           return {
               "success": False,
               "error": str(e)
           }

   if __name__ == "__main__":
       import sys
       if len(sys.argv) < 2:
           print("Usage: python main.py <ticket_id> [--dry-run]")
           sys.exit(1)

       ticket_id = sys.argv[1]
       dry_run = "--dry-run" in sys.argv

       result = create_ticket(ticket_id, dry_run)

       if result["success"]:
           if dry_run:
               print(f"[DRY RUN] Would create ticket from {ticket_id}")
           else:
               dest = result["destination_issue"]
               print(f"✅ Created ticket: {dest.id}")
               print(f"   Summary: {dest.summary}")
               if result["subtasks"]:
                   print(f"   Subtasks: {len(result['subtasks'])}")
       else:
           print(f"❌ Failed: {result['error']}")
           sys.exit(1)
   ```

3. **Add command-line interface**
   - Support `--dry-run` flag
   - **[VALIDATED]** Support `--type=feature|scenario|issue` flag
   - Support `--verbose` flag
   - Clean error messages

   ```python
   # Updated CLI parsing
   parser = argparse.ArgumentParser()
   parser.add_argument("ticket_id", help="Source ticket ID")
   parser.add_argument("--dry-run", action="store_true")
   parser.add_argument("--type", choices=["feature", "scenario", "issue"], help="Manual task type override")
   parser.add_argument("--verbose", action="store_true")
   args = parser.parse_args()

   # Convert type string to TaskType enum
   manual_type = None
   if args.type:
       type_map = {"feature": TaskType.FEATURE_DEV, "scenario": TaskType.UPLOAD_SCENARIO, "issue": TaskType.INVESTIGATE_ISSUE}
       manual_type = type_map[args.type]

   result = create_ticket(args.ticket_id, args.dry_run, manual_type)
   ```

4. **Add error handling**
   - Invalid ticket ID format
   - Ticket not found (404)
   - API authentication failures
   - Translation failures
   - Template errors

5. **Write integration tests**
   - Test full workflow with mocks
   - Test error scenarios
   - Test dry-run mode
   - Test all task types

## Todo List

- [ ] Update SKILL.md with usage instructions
- [ ] **[VALIDATED]** Simplify to single API client (same project)
- [ ] Implement main orchestration function
- [ ] **[VALIDATED]** Add `--type` flag parsing for manual override
- [ ] Add CLI argument parsing (dry-run, verbose)
- [ ] Integrate API client
- [ ] Integrate translation service
- [ ] Integrate template manager
- [ ] **[VALIDATED]** Use source priority instead of template default
- [ ] **[VALIDATED]** Add attachment copying step
- [ ] Add dry-run mode
- [ ] Add comprehensive error handling
- [ ] Add logging throughout
- [ ] Write integration tests
- [ ] Test with real Nulab API (use test ticket)

## Success Criteria

- [ ] End-to-end workflow executes successfully
- [ ] All components integrate correctly
- [ ] Error handling covers all failure modes
- [ ] Dry-run mode works without API calls
- [ ] **[VALIDATED]** `--type` flag correctly overrides auto-detection
- [ ] **[VALIDATED]** Attachments copied from source to destination
- [ ] **[VALIDATED]** Source priority preserved in new ticket
- [ ] Clear user feedback on success/failure
- [ ] Execution time < 10 seconds
- [ ] All integration tests passing

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Component integration issues | Medium | Integration tests, mock components |
| API failures during creation | Medium | **[VALIDATED]** Manual cleanup (no auto-rollback) |
| Translation quality issues | Low | Human review option in future |
| Template mismatches | Low | Validation on load |

## Security Considerations

- Validate ticket ID format before API call
- Sanitize all user inputs
- Never log sensitive data (API keys, full ticket content)
- Use environment variables for all credentials

## Next Steps

Proceed to [Phase 06: Testing & Validation](phase-06-testing-validation.md) after main logic is implemented.

---

**Dependencies**: Phases 02, 03, 04 must be complete
**Blocks**: Phase 06 (needs implemented skill for testing)
