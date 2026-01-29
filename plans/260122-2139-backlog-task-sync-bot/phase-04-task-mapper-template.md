# Phase 04: Task Mapper & Template

## Context Links
- [Brainstorm](../reports/brainstorm-260122-2139-backlog-task-sync-bot.md)
- [Phase 03: Claude Translator](phase-03-claude-translator.md)

## Overview
- **Priority:** P1 (business logic)
- **Status:** pending
- **Effort:** 1h
- **Description:** Implement task type mapping and template builder for synced tasks

## Key Insights
- Task type determines assignee and whether to create subtasks
- Template embeds original (JP) + translated (VI) content
- 10 predefined subtasks for Feature Request only
- Config-driven approach for easy modification

## Requirements

### Functional
- Map task type to assignee ID
- Determine if subtasks needed based on type
- Build task description from template
- Generate subtask list for Feature Requests

### Non-Functional
- Config files editable without code changes
- Clear type definitions

## Architecture

```
mapping.json → TaskMapper → { assigneeId, createSubtasks }
subtasks.json → SubtaskGenerator → string[]
template.ts → buildDescription(original, translated, meta) → string
```

## Related Code Files

### Create
- `experiments/backlog-sync-bot/src/task-mapper.ts`
- `experiments/backlog-sync-bot/src/template.ts`
- `experiments/backlog-sync-bot/src/types/config-types.ts`

### Reference
- `experiments/backlog-sync-bot/config/mapping.json`
- `experiments/backlog-sync-bot/config/subtasks.json`

## Implementation Steps

1. Create types/config-types.ts
```typescript
export interface TaskTypeConfig {
  assignee: string;
  createSubtasks: boolean;
}

export interface MappingConfig {
  taskTypeMapping: Record<string, TaskTypeConfig>;
  defaultAssignee: string;
}

export interface SubtasksConfig {
  subtasks: string[];
}

export interface UserMapping {
  [name: string]: number; // name → Backlog user ID
}
```

2. Create task-mapper.ts
```typescript
import { readFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import type {
  MappingConfig,
  SubtasksConfig,
  TaskTypeConfig,
  UserMapping,
} from "./types/config-types.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

export class TaskMapper {
  private mapping: MappingConfig;
  private subtasksConfig: SubtasksConfig;
  private userMapping: UserMapping;

  constructor(userMapping: UserMapping) {
    this.mapping = this.loadJson<MappingConfig>("../config/mapping.json");
    this.subtasksConfig = this.loadJson<SubtasksConfig>("../config/subtasks.json");
    this.userMapping = userMapping;
  }

  private loadJson<T>(relativePath: string): T {
    const fullPath = join(__dirname, relativePath);
    const content = readFileSync(fullPath, "utf-8");
    return JSON.parse(content) as T;
  }

  getTaskConfig(issueTypeName: string): TaskTypeConfig {
    const config = this.mapping.taskTypeMapping[issueTypeName];
    if (config) {
      return config;
    }

    // Default config
    return {
      assignee: this.mapping.defaultAssignee,
      createSubtasks: false,
    };
  }

  getAssigneeId(issueTypeName: string): number | undefined {
    const config = this.getTaskConfig(issueTypeName);
    return this.userMapping[config.assignee];
  }

  shouldCreateSubtasks(issueTypeName: string): boolean {
    return this.getTaskConfig(issueTypeName).createSubtasks;
  }

  getSubtaskNames(): string[] {
    return this.subtasksConfig.subtasks;
  }
}
```

3. Create template.ts
```typescript
export interface TemplateMeta {
  sourceUrl: string;
  syncedAt: Date;
  originalAssignee?: string;
}

export function buildTaskDescription(
  originalContent: string,
  translatedContent: string,
  meta: TemplateMeta
): string {
  const syncedDate = meta.syncedAt.toISOString().split("T")[0];
  const syncedTime = meta.syncedAt.toTimeString().split(" ")[0];

  const lines = [
    "## Original (JP)",
    "",
    originalContent,
    "",
    "---",
    "",
    "## Translation (VI)",
    "",
    translatedContent,
    "",
    "---",
    "",
    "## Internal Notes",
    `- Source: ${meta.sourceUrl}`,
    `- Synced: ${syncedDate} ${syncedTime}`,
  ];

  if (meta.originalAssignee) {
    lines.push(`- Original Assignee: ${meta.originalAssignee}`);
  }

  return lines.join("\n");
}

export function buildSubtaskSummary(
  parentSummary: string,
  subtaskName: string
): string {
  // Keep parent summary short, append subtask name
  const maxParentLength = 50;
  const truncatedParent =
    parentSummary.length > maxParentLength
      ? parentSummary.substring(0, maxParentLength) + "..."
      : parentSummary;

  return `[${subtaskName}] ${truncatedParent}`;
}
```

4. Create utility to fetch user mapping
```typescript
// Add to task-mapper.ts
import type { BacklogClient } from "./backlog-client.js";
import type { UserMapping } from "./types/config-types.js";

export async function buildUserMapping(
  client: BacklogClient,
  projectKey: string,
  requiredNames: string[]
): Promise<UserMapping> {
  const users = await client.getProjectUsers(projectKey);
  const mapping: UserMapping = {};

  for (const name of requiredNames) {
    const user = users.find(
      (u) =>
        u.name.toLowerCase() === name.toLowerCase() ||
        u.userId.toLowerCase() === name.toLowerCase()
    );
    if (user) {
      mapping[name] = user.id;
    } else {
      console.warn(`User "${name}" not found in project ${projectKey}`);
    }
  }

  return mapping;
}
```

## Todo List
- [ ] Create config-types.ts
- [ ] Create TaskMapper class
- [ ] Implement config loading from JSON
- [ ] Implement getTaskConfig method
- [ ] Implement getAssigneeId method
- [ ] Implement shouldCreateSubtasks method
- [ ] Create buildTaskDescription function
- [ ] Create buildSubtaskSummary function
- [ ] Create buildUserMapping utility
- [ ] Test with different task types

## Success Criteria
- Maps Bug → CuongNN (no subtasks)
- Maps Feature Request → Duongnh (with subtasks)
- Maps Investigation → CuongNN (no subtasks)
- Maps Scenario Upload → Duongnh (no subtasks)
- Unknown types use default assignee
- Template output matches expected format
- Subtask names match config

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Config file not found | High | Fail fast with clear path in error |
| User not found in project | Medium | Warn but continue (null assignee) |
| Invalid JSON format | High | JSON.parse will throw, catch and report |

## Security Considerations
- No sensitive data in config files
- User IDs fetched dynamically from API

## Next Steps
→ Proceed to Phase 05: CLI Integration
