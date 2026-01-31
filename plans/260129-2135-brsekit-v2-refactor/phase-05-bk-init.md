# Phase 5: bk-init (Setup Wizard)

## Context Links
- [Original Plan - bk-init](c:/Users/duongbibo/brse-workspace/projects/solo-builder-12months/ship/BrseKit/260128-0933-brsekit-mvp-implementation/plan.md)
- [brsekit/master.yaml](c:/Users/duongbibo/brse-workspace/.claude/skills/brsekit/master.yaml)
- [PM-FRAMEWORK.md](c:/Users/duongbibo/brse-workspace/.claude/skills/brsekit/PM-FRAMEWORK.md)

## Overview
- **Priority:** P2
- **Status:** 100% complete (99 tests passing)
- **Effort:** 2h
- **Description:** Project setup wizard with PM mindset configuration

## Key Insights
- Generates project-context.yaml from user input
- Configures PM mindset based on project type (waterfall/agile/hybrid)
- One-time setup per project
- Validates Backlog API connectivity

## Requirements

### Functional
- `/bk-init` - Interactive setup wizard
- Generate `project-context.yaml`
- Validate Backlog API connection
- Copy/customize PM templates

### Non-Functional
- Complete setup in <5 minutes
- Clear prompts in Japanese/English
- Graceful error handling

## Architecture

```
.claude/skills/bk-init/
├── SKILL.md
├── requirements.txt
├── scripts/
│   ├── main.py              # CLI entry + wizard
│   ├── wizard.py            # Interactive prompts
│   ├── validator.py         # API + config validation
│   └── config_generator.py  # Generate YAML
├── templates/
│   ├── project-context.yaml.template
│   ├── waterfall.yaml
│   ├── agile.yaml
│   └── hybrid.yaml
└── tests/
    └── test_wizard.py
```

### project-context.yaml Structure
```yaml
project:
  name: "Project Name"
  backlog_key: "PROJ"
  type: "project-based"  # labor, hybrid
  methodology: "waterfall"  # agile, hybrid

customer:
  name: "Customer Corp"
  industry: "Finance"
  timezone: "JST"
  communication_style: "formal"

focus_areas:
  primary: [change_request_tracking, budget_monitoring]
  secondary: [documentation_quality]

warning_triggers:
  high: ["scope change", "追加要件", "budget", "delay"]
  medium: ["clarification", "確認"]

pm_checklist:
  weekly: ["Review CR status", "Check budget burn rate"]
  meeting: ["Confirm scope alignment", "Track action items"]

vault:
  enabled: true
  sources: [email, backlog]
  sync_schedule: "daily"
```

## Related Code Files

### Create
- `.claude/skills/bk-init/SKILL.md`
- `.claude/skills/bk-init/requirements.txt`
- `.claude/skills/bk-init/scripts/main.py`
- `.claude/skills/bk-init/scripts/wizard.py`
- `.claude/skills/bk-init/scripts/validator.py`
- `.claude/skills/bk-init/scripts/config_generator.py`
- `.claude/skills/bk-init/templates/project-context.yaml.template`
- `.claude/skills/bk-init/templates/waterfall.yaml`
- `.claude/skills/bk-init/templates/agile.yaml`
- `.claude/skills/bk-init/templates/hybrid.yaml`
- `.claude/skills/bk-init/tests/test_wizard.py`

### Reuse
- `.claude/skills/brsekit/PM-FRAMEWORK.md` (reference)
- `.claude/skills/common/backlog/client.py` (validation)

## Implementation Steps

1. **Create bk-init skill structure**
   - Create directories
   - Write SKILL.md with usage guide

2. **Create PM templates (preserve existing)**
   - waterfall.yaml: CR tracking, budget focus
   - agile.yaml: Sprint goals, quality focus
   - hybrid.yaml: Combined approach

3. **Implement wizard.py (80 lines)**
   - `SetupWizard` class
   - Step 1: Project name, Backlog key
   - Step 2: Project type selection
   - Step 3: Customer info
   - Step 4: PM focus areas
   - Step 5: Vault configuration

4. **Implement validator.py (50 lines)**
   - `validate_backlog_connection(space, key, project)` - Test API
   - `validate_config(config: dict)` - Schema validation
   - Return clear error messages

5. **Implement config_generator.py (60 lines)**
   - `generate_config(wizard_data: dict) -> str`
   - Merge user input with template
   - Format as YAML

6. **Implement main.py CLI (40 lines)**
   - Entry point: `/bk-init`
   - Run wizard
   - Validate
   - Save to project-context.yaml

7. **Write tests**
   - test_wizard.py: Mock input, verify output
   - test_validator.py: API mocking

## Todo List

- [ ] Create bk-init skill directory
- [ ] Write SKILL.md documentation
- [ ] Create PM template files
- [ ] Implement wizard.py
- [ ] Implement validator.py
- [ ] Implement config_generator.py
- [ ] Implement CLI (main.py)
- [ ] Write unit tests
- [ ] Integration test with Backlog API

## Success Criteria

- [ ] `/bk-init` runs interactive wizard
- [ ] Generated project-context.yaml is valid YAML
- [ ] Backlog API connection validated
- [ ] PM templates correctly applied
- [ ] Vault config section included

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Invalid user input | Medium | Validation + retry prompts |
| API connection fails | Low | Clear error message, retry |
| Template mismatch | Low | Schema validation |

## Security Considerations

- API key stored in .env, not project-context.yaml
- No secrets in generated config
- Validate input to prevent injection

## Next Steps

- Run bk-init as first step for new projects
- Other skills read project-context.yaml for context
