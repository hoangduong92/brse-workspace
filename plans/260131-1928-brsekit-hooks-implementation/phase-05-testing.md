# Phase 5: Test Multi-Project Setup

## Context Links

- [Phase 1-4](./plan.md) - All implementation phases
- [Brainstorm Success Metrics](../reports/brainstorm-260131-1928-brsekit-hooks-implementation.md)

## Overview

| Priority | Status | Effort |
|----------|--------|--------|
| P2 | pending | 1h |

End-to-end testing of hooks with different project configurations. Verify output format, token count, and error handling.

## Key Insights

1. Test all 3 scenarios: 0, 1, N projects
2. Verify JSON format for subagent hook
3. Measure execution time (< 100ms target)
4. Test with Claude Code restart

## Requirements

**Test Scenarios:**
1. No projects/ directory
2. Empty projects/ directory
3. Single project in projects/
4. Multiple projects in projects/
5. Missing env vars
6. All env vars present

## Implementation Steps

### 1. Prepare Test Environment

```bash
# Backup current projects if any
mv projects projects.bak 2>/dev/null || true
```

### 2. Test Scenario: No projects/

```bash
# Remove projects dir
rm -rf projects

# Restart Claude Code, verify output:
# "BrseKit: ⚠️ No projects in projects/"
```

### 3. Test Scenario: Single project

```bash
# Create single project
mkdir -p projects/HB21373/vault
echo '{}' > projects/HB21373/glossary.json

# Restart Claude Code, verify output:
# "BrseKit: Project HB21373 (auto-selected)"
```

### 4. Test Scenario: Multiple projects

```bash
# Add more projects
mkdir -p projects/HB21456/vault
mkdir -p projects/HB21789/vault

# Restart Claude Code, verify output contains:
# "3 projects available"
# "⚠️ Use --project <name> with skills"
```

### 5. Test Subagent Hook Directly

```bash
# Test with mock payload
echo '{"agent_type":"researcher","cwd":"'$(pwd)'"}' | \
  node .claude/hooks/brsekit-subagent-init.cjs

# Verify JSON output with hookSpecificOutput wrapper
```

### 6. Test Env Var Display

```bash
# Set some env vars
export BACKLOG_API_KEY="test"
unset GEMINI_API_KEY

# Restart, verify:
# "Env: API_KEY ✓ | GEMINI_KEY ✗"
```

### 7. Performance Test

```bash
# Measure execution time
time (echo '{"source":"startup"}' | node .claude/hooks/brsekit-session-init.cjs)
# Should be < 100ms
```

### 8. Restore Environment

```bash
# Restore original projects
rm -rf projects
mv projects.bak projects 2>/dev/null || true
```

## Todo List

- [ ] Test no projects/ directory
- [ ] Test empty projects/ directory
- [ ] Test single project (auto-select)
- [ ] Test multiple projects (list + warning)
- [ ] Test subagent hook JSON output
- [ ] Test env var status display
- [ ] Measure execution time
- [ ] Test with Claude Code restart
- [ ] Verify no errors in console

## Success Criteria

1. All 6 scenarios produce expected output
2. Subagent hook returns valid JSON
3. Execution time < 100ms
4. Claude Code startup not blocked by errors
5. Token count: session < 100, subagent < 40

## Verification Checklist

| Check | Expected | Pass? |
|-------|----------|-------|
| No projects output | Warning + /bk-init hint | |
| Single project output | Auto-selected message | |
| Multiple projects output | List + warning | |
| Subagent JSON valid | hookSpecificOutput wrapper | |
| Env vars displayed | ✓/✗ symbols | |
| Execution time | < 100ms | |
| Claude startup | No errors | |
