# Phase 04: Template System

**Context**: Parent plan [../plan.md](plan.md)

## Overview

**Date**: 2026-01-22
**Description**: Implement dynamic task template system with JSON-based configuration for different task types
**Priority**: P1
**Status**: pending
**Effort**: 2h

## Context Links

- Brainstorming: [../reports/brainstorming-260122-2121-nulab-backlog-automation.md](../reports/brainstorming-260122-2121-nulab-backlog-automation.md)
- Depends on: [Phase 01: Project Setup](phase-01-project-setup.md)

## Key Insights

- JSON templates are easy to maintain without code changes
- Template variables: `{summary}`, `{description}`, `{original_summary}`, `{translated_summary}`, etc.
- Subtasks only for feature-dev type
- Task type detection via keyword matching
- **[VALIDATED]** Hybrid detection: keyword auto-detect with `--type` flag override
- **[VALIDATED]** Auto-assign by task type (configurable in templates)

## Requirements

### Functional
- Load templates from JSON files
- Detect task type from issue summary/description
- **[VALIDATED]** Support manual task type override via `--type` flag
- Apply template with variable substitution
- Generate subtasks from template
- **[VALIDATED]** Auto-assign by task type (assignee IDs in templates)
- Validate template structure on load

### Non-Functional
- Template loading < 100ms
- Validation errors on startup
- Easy to add new task types
- **[VALIDATED]** Easy to update assignee IDs without code changes

## Architecture

```python
class TaskType(Enum):
    FEATURE_DEV = "feature-dev"
    UPLOAD_SCENARIO = "upload-scenario"
    INVESTIGATE_ISSUE = "investigate-issue"

class Template:
    name: str
    summary_template: str
    description_template: str
    subtasks: list[SubtaskTemplate]
    default_assignee: int | None
    default_priority: str
    # [VALIDATED] Assignee mapping for subtasks
    assignee_mapping: dict[str, int]  # {"analysis": 12345, ...}

class SubtaskTemplate:
    subject_template: str
    estimated_hours: float
    default_assignee: int | None
    # [VALIDATED] Optional assignee key for mapping
    assignee_key: str | None  # e.g., "analysis", "implementation"

class TemplateManager:
    def load_templates() -> dict[TaskType, Template]
    # [VALIDATED] Override type for manual control
    def detect_task_type(issue: Issue, manual_type: TaskType = None) -> TaskType
    def apply_template(template: Template, context: dict) -> dict
    # [VALIDATED] Apply assignee mapping
    def generate_subtasks(template: Template, parent_id: int, context: dict) -> list[dict]
```

## Related Code Files

### Modify
- `.claude/skills/backlog/scripts/templates.py`
- `.claude/skills/backlog/templates/feature-dev.json`
- `.claude/skills/backlog/templates/upload-scenario.json`
- `.claude/skills/backlog/templates/investigate-issue.json`

### Create
- `.claude/skills/backlog/tests/test_templates.py`

## Implementation Steps

1. **Define template JSON schema**
   ```json
   {
     "name": "Feature Development",
     "summary_template": "[KH-{project_id}] {translated_summary}",
     "description_template": "## Original\n{original_summary}\n\n{original_description}\n\n---\n\n## Translation\n{translated_summary}\n\n{translated_description}",
     "subtasks": [
       {
         "subject_template": "Analysis: {translated_summary}",
         "estimated_hours": 2.0,
         "default_assignee": null
       },
       {
         "subject_template": "Implementation: {translated_summary}",
         "estimated_hours": 8.0,
         "default_assignee": null
       },
       {
         "subject_template": "Testing: {translated_summary}",
         "estimated_hours": 4.0,
         "default_assignee": null
       },
       {
         "subject_template": "Code Review: {translated_summary}",
         "estimated_hours": 2.0,
         "default_assignee": null
       }
     ],
     "default_assignee": null,
     "default_priority": "normal"
   }
   ```

   **[VALIDATED]** Add `assignee_mapping` section for auto-assign by task type:
   ```json
   {
     "name": "Feature Development",
     ...
     "default_assignee": null,
     "default_priority": "normal",
     "assignee_mapping": {
       "analysis": 12345,
       "implementation": 12346,
       "testing": 12347,
       "code_review": 12348
     }
   }
   ```

2. **Create feature-dev.json template**
   - Include analysis, implementation, testing, code review subtasks
   - Preserve original and translated content
   - Default priority: normal

3. **Create upload-scenario.json template**
   - No subtasks
   - Summary prefix: [Scenario]
   - Default priority: high

4. **Create investigate-issue.json template**
   - No subtasks
   - Summary prefix: [Investigate]
   - Description includes issue details section
   - Default priority: urgent

5. **Implement TemplateManager**
   ```python
   import json
   from pathlib import Path

   class TemplateManager:
       TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

       TASK_TYPE_PATTERNS = {
           TaskType.FEATURE_DEV: [
               r'feature|dev|implement|add new|create',
               r'機能|開発|実装|新規'
           ],
           TaskType.UPLOAD_SCENARIO: [
               r'scenario|upload|test case',
               r'シナリオ|アップロード|テスト'
           ],
           TaskType.INVESTIGATE_ISSUE: [
               r'investigate|bug|fix|issue|error',
               r'調査|バグ|修正|不具合|エラー'
           ]
       }

       def __init__(self):
           self.templates = self._load_templates()

       def _load_templates(self) -> dict[TaskType, Template]:
           templates = {}
           for task_type in TaskType:
               path = self.TEMPLATE_DIR / f"{task_type.value}.json"
               with open(path) as f:
                   data = json.load(f)
                   templates[task_type] = Template.from_dict(data)
           return templates

       # [VALIDATED] Support manual type override
       def detect_task_type(self, issue: Issue, manual_type: TaskType = None) -> TaskType:
           if manual_type:
               return manual_type

           text = f"{issue.summary} {issue.description}".lower()
           for task_type, patterns in self.TASK_TYPE_PATTERNS.items():
               if any(re.search(p, text) for p in patterns):
                   return task_type
           return TaskType.FEATURE_DEV  # Default

       def apply_template(self, template: Template, context: dict) -> dict:
           summary = template.summary_template.format(**context)
           description = template.description_template.format(**context)

           return {
               "summary": summary,
               "description": description,
               "priorityId": self._priority_to_id(template.default_priority),
               "assigneeId": template.default_assignee
           }

       # [VALIDATED] Apply assignee mapping from template
       def generate_subtasks(self, template: Template, parent_id: int, context: dict) -> list[dict]:
           subtasks = []
           for subtask_template in template.subtasks:
               subject = subtask_template.subject_template.format(**context)

               # Determine assignee: mapping > default > None
               assignee_id = subtask_template.default_assignee
               if subtask_template.assignee_key and template.assignee_mapping:
                   assignee_id = template.assignee_mapping.get(subtask_template.assignee_key, assignee_id)

               subtasks.append({
                   "parentIssueId": parent_id,
                   "summary": subject,
                   "estimatedHours": subtask_template.estimated_hours,
                   "assigneeId": assignee_id
               })
           return subtasks
   ```

7. **[VALIDATED] Add type flag support note for Phase 05**
   - Phase 05 will parse `--type=feature|scenario|issue` from CLI
   - Pass to `detect_task_type(issue, manual_type=TaskType.FEATURE_DEV)`

6. **Add template validation**
   ```python
   def _validate_template(data: dict) -> None:
       required = ["name", "summary_template", "description_template", "subtasks"]
       for field in required:
           if field not in data:
               raise ValueError(f"Missing required field: {field}")
   ```

7. **Write tests**
   - Test template loading from JSON
   - Test task type detection with various samples
   - Test variable substitution
   - Test subtask generation
   - Test validation errors

## Todo List

- [ ] Create Template dataclass (add **assignee_mapping** field)
- [ ] Create SubtaskTemplate dataclass (add **assignee_key** field)
- [ ] Define task type patterns (JA/VI keywords)
- [ ] Create feature-dev.json template
- [ ] Create upload-scenario.json template
- [ ] Create investigate-issue.json template
- [ ] **[VALIDATED] Add assignee_mapping to templates**
- [ ] Implement TemplateManager class
- [ ] Implement template loading with validation
- [ ] **[VALIDATED] Implement task type detection with manual override**
- [ ] Implement template application with variable substitution
- [ ] **[VALIDATED] Implement subtask generation with assignee mapping**
- [ ] Write unit tests for all functions

## Success Criteria

- [ ] All templates load without errors
- [ ] Task type detection > 90% accuracy
- [ ] **[VALIDATED] Manual --type flag overrides auto-detection**
- [ ] Variable substitution works for all template variables
- [ ] Subtasks generated correctly with proper assignee
- [ ] **[VALIDATED] Assignee mapping applies correctly**
- [ ] Validation catches malformed templates
- [ ] All unit tests passing

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Template syntax errors | Medium | Validation on load, clear error messages |
| Task type misclassification | Medium | Add more patterns, logging for review |
| Missing template variables | Low | Validation, default values |
| JSON parse errors | Low | Try-catch with helpful error messages |

## Security Considerations

- Validate template file paths (prevent directory traversal)
- Sanitize user input before template substitution
- Limit template size (prevent DoS)
- No code execution in templates

## Next Steps

Proceed to [Phase 05: Main Skill Logic](phase-05-main-skill-logic.md) after template tests pass.

---

**Dependencies**: Phase 01 must be complete
**Blocks**: Phase 05 (needs templates for ticket creation)
