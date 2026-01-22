# Phase 01: Project Setup

**Context**: Parent plan [../plan.md](plan.md)

## Overview

**Date**: 2026-01-22
**Description**: Initialize Claude Code skill structure with Python virtual environment, dependencies, and configuration files
**Priority**: P1
**Status**: pending
**Effort**: 2h

## Key Insights

- Python 3.10+ required for async operations
- Use virtual environment for dependency isolation
- Keep configuration in JSON for template maintainability
- Follow Claude Code skill conventions

## Requirements

### Functional
- Create skill directory structure under `.claude/skills/backlog/`
- Setup Python virtual environment with required packages
- Create `.env` and `.env.example` for API keys
- Create `SKILL.md` following skill conventions

### Non-Functional
- Follow YAGNI-KISS-DRY principles
- Keep files < 200 lines where possible
- Use kebab-case naming

## Architecture

```
.claude/skills/backlog/
├── SKILL.md                  # Skill definition (< 100 lines)
├── scripts/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── nulab_client.py      # Nulab API wrapper
│   ├── translator.py        # Claude translation
│   └── templates.py         # Template loader
├── templates/
│   ├── feature-dev.json
│   ├── upload-scenario.json
│   └── investigate-issue.json
├── tests/
│   └── test_setup.py
├── .env.example
└── requirements.txt

.claude/skills/.venv/         # Virtual environment
```

## Related Code Files

### Create
- `.claude/skills/backlog/SKILL.md`
- `.claude/skills/backlog/scripts/__init__.py`
- `.claude/skills/backlog/scripts/main.py` (stub)
- `.claude/skills/backlog/scripts/nulab_client.py` (stub)
- `.claude/skills/backlog/scripts/translator.py` (stub)
- `.claude/skills/backlog/scripts/templates.py` (stub)
- `.claude/skills/backlog/templates/feature-dev.json`
- `.claude/skills/backlog/templates/upload-scenario.json`
- `.claude/skills/backlog/templates/investigate-issue.json`
- `.claude/skills/backlog/tests/test_setup.py`
- `.claude/skills/backlog/.env.example`
- `.claude/skills/backlog/requirements.txt`

### Modify
- `.gitignore` (add `.env`)

## Implementation Steps

1. **Create directory structure**
   ```bash
   mkdir -p .claude/skills/backlog/{scripts,templates,tests}
   ```

2. **Create SKILL.md**
   - Define skill name: `backlog`
   - Description: "Automate ticket creation from customer backlog to internal backlog with AI translation"
   - Usage instructions
   - Keep < 100 lines

3. **Create requirements.txt**
   ```
   requests>=2.31.0
   python-dotenv>=1.0.0
   anthropic>=0.18.0
   pytest>=7.4.0
   pytest-asyncio>=0.21.0
   ```

4. **Setup virtual environment**
   ```bash
   cd .claude/skills
   python -m venv .venv
   # Windows
   .venv\Scripts\pip install -r backlog/requirements.txt
   # Linux/Mac
   .venv/bin/pip install -r backlog/requirements.txt
   ```

5. **Create .env.example**
   ```env
   # Nulab API Configuration
   NULAB_SPACE_URL=hblab.backlogtool.com
   NULAB_SOURCE_API_KEY=your_source_api_key_here
   NULAB_DEST_API_KEY=your_dest_api_key_here
   NULAB_SOURCE_PROJECT_ID=HB21373
   NULAB_DEST_PROJECT_ID=your_dest_project_id

   # Claude API Configuration
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   CLAUDE_MODEL=claude-3-5-haiku-20241022

   # Skill Configuration
   DEFAULT_ASSIGNEE_ID=
   LOG_LEVEL=INFO
   ```

6. **Create stub files** with docstrings and basic structure

7. **Update .gitignore** to exclude `.env`

## Todo List

- [ ] Create directory structure
- [ ] Create SKILL.md with skill definition
- [ ] Create requirements.txt with dependencies
- [ ] Setup Python virtual environment
- [ ] Create .env.example with all config variables
- [ ] Create stub Python files with docstrings
- [ ] Create template JSON files with structure
- [ ] Update .gitignore for .env
- [ ] Run initial setup test

## Success Criteria

- [ ] Directory structure created
- [ ] Virtual environment activated and packages installed
- [ ] All stub files created with proper docstrings
- [ ] `.env.example` contains all required variables
- [ ] `.env` in `.gitignore`
- [ ] Can run `python -c "import scripts.main"` without errors

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Python version mismatch | Low | Document Python 3.10+ requirement |
| Virtual env path issues | Medium | Use absolute paths in docs |
| Package conflicts | Low | Pin versions in requirements.txt |

## Security Considerations

- Never commit `.env` file
- Use `.env.example` as template
- Document API key generation process
- Add `.env` to `.gitignore` before first run

## Next Steps

Proceed to [Phase 02: Nulab API Client](phase-02-nulab-api-client.md) after completing setup validation.

---

**Dependencies**: None (first phase)
