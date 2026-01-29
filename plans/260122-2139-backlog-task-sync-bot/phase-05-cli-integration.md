# Phase 05: CLI Integration & Testing

## Context Links
- [Phase 01: Project Setup](phase-01-project-setup.md)
- [Phase 04: Task Mapper & Template](phase-04-task-mapper-template.md)

## Overview
- **Priority:** P1 (integration)
- **Status:** pending
- **Effort:** 2h
- **Description:** Integrate all components into CLI and test end-to-end

## Key Insights
- Commander.js for CLI parsing
- Orchestrate: fetch → translate → map → create → subtasks → attachments
- Progress feedback during long operations
- Dry-run mode for testing without creating tasks

## Requirements

### Functional
- Parse ticket ID from command line
- Execute full sync workflow
- Support `--with-subtasks` flag (force subtasks)
- Support `--no-translate` flag (skip translation)
- Support `--dry-run` flag (preview without creating)
- Display progress and result summary

### Non-Functional
- Clear error messages
- Exit codes for scripting (0=success, 1=error)
- Verbose mode for debugging

## Architecture

```
CLI (commander)
  │
  ├── parse args
  ├── validate env vars
  │
  └── SyncService
        ├── BacklogClient (KH) → fetch issue
        ├── Translator → translate description
        ├── TaskMapper → get assignee & subtask config
        ├── Template → build description
        ├── BacklogClient (Internal) → create issue
        ├── (optional) create subtasks
        └── (optional) sync attachments
```

## Related Code Files

### Create
- `experiments/backlog-sync-bot/src/sync-service.ts`

### Modify
- `experiments/backlog-sync-bot/src/index.ts` (full CLI implementation)

## Implementation Steps

1. Create sync-service.ts
```typescript
import { BacklogClient } from "./backlog-client.js";
import { Translator } from "./translator.js";
import { TaskMapper, buildUserMapping } from "./task-mapper.js";
import { buildTaskDescription, buildSubtaskSummary } from "./template.js";
import type { Issue } from "./types/backlog-types.js";

export interface SyncOptions {
  withSubtasks?: boolean;
  skipTranslation?: boolean;
  dryRun?: boolean;
  verbose?: boolean;
}

export interface SyncResult {
  sourceIssue: Issue;
  createdIssue?: Issue;
  subtasks?: Issue[];
  attachmentsSynced: number;
}

export class SyncService {
  private khClient: BacklogClient;
  private internalClient: BacklogClient;
  private translator: Translator;
  private internalProjectKey: string;

  constructor(
    khSpace: string,
    khApiKey: string,
    internalSpace: string,
    internalApiKey: string,
    internalProjectKey: string,
    anthropicApiKey: string
  ) {
    this.khClient = new BacklogClient(khSpace, khApiKey);
    this.internalClient = new BacklogClient(internalSpace, internalApiKey);
    this.translator = new Translator(anthropicApiKey);
    this.internalProjectKey = internalProjectKey;
  }

  async sync(ticketId: string, options: SyncOptions = {}): Promise<SyncResult> {
    const log = options.verbose ? console.log : () => {};

    // 1. Fetch source issue
    log(`Fetching issue ${ticketId}...`);
    const sourceIssue = await this.khClient.getIssue(ticketId);
    log(`Found: ${sourceIssue.summary}`);

    // 2. Translate description
    let translatedDescription = sourceIssue.description || "";
    if (!options.skipTranslation && translatedDescription) {
      log("Translating description...");
      translatedDescription = await this.translator.translateToVietnamese(
        sourceIssue.description
      );
      log("Translation complete");
    }

    // 3. Get internal project metadata
    log("Fetching internal project metadata...");
    const internalProject = await this.internalClient.getProject(
      this.internalProjectKey
    );

    // 4. Build user mapping
    const userMapping = await buildUserMapping(
      this.internalClient,
      this.internalProjectKey,
      ["CuongNN", "Duongnh"]
    );

    // 5. Get task config
    const mapper = new TaskMapper(userMapping);
    const issueTypeName = sourceIssue.issueType.name;
    const assigneeId = mapper.getAssigneeId(issueTypeName);
    const shouldCreateSubtasks =
      options.withSubtasks || mapper.shouldCreateSubtasks(issueTypeName);

    log(`Issue type: ${issueTypeName}`);
    log(`Assignee ID: ${assigneeId}`);
    log(`Create subtasks: ${shouldCreateSubtasks}`);

    // 6. Build description
    const sourceUrl = `https://hblab.backlogtool.com/view/${ticketId}`;
    const description = buildTaskDescription(
      sourceIssue.description || "",
      translatedDescription,
      {
        sourceUrl,
        syncedAt: new Date(),
        originalAssignee: sourceIssue.assignee?.name,
      }
    );

    // 7. Find matching issue type in internal project
    const internalIssueType = internalProject.issueTypes.find(
      (t) => t.name === issueTypeName
    ) || internalProject.issueTypes[0];

    if (options.dryRun) {
      log("\n[DRY RUN] Would create issue:");
      log(`  Summary: ${sourceIssue.summary}`);
      log(`  Type: ${internalIssueType.name}`);
      log(`  Assignee ID: ${assigneeId}`);
      log(`  Subtasks: ${shouldCreateSubtasks ? mapper.getSubtaskNames().length : 0}`);
      return { sourceIssue, attachmentsSynced: 0 };
    }

    // 8. Create internal issue
    log("Creating internal issue...");
    const createdIssue = await this.internalClient.createIssue({
      projectId: internalProject.id,
      summary: sourceIssue.summary,
      issueTypeId: internalIssueType.id,
      priorityId: sourceIssue.priority.id,
      description,
      assigneeId,
    });
    log(`Created: ${createdIssue.issueKey}`);

    // 9. Create subtasks if needed
    const subtasks: Issue[] = [];
    if (shouldCreateSubtasks) {
      log("Creating subtasks...");
      for (const subtaskName of mapper.getSubtaskNames()) {
        const subtask = await this.internalClient.createIssue({
          projectId: internalProject.id,
          summary: buildSubtaskSummary(sourceIssue.summary, subtaskName),
          issueTypeId: internalIssueType.id,
          priorityId: sourceIssue.priority.id,
          parentIssueId: createdIssue.id,
          assigneeId,
        });
        subtasks.push(subtask);
        log(`  Created subtask: ${subtask.issueKey} - ${subtaskName}`);
      }
    }

    // 10. Sync attachments
    let attachmentsSynced = 0;
    if (sourceIssue.attachments.length > 0) {
      log(`Syncing ${sourceIssue.attachments.length} attachments...`);
      for (const attachment of sourceIssue.attachments) {
        try {
          const data = await this.khClient.downloadAttachment(
            sourceIssue.id,
            attachment.id
          );
          const uploaded = await this.internalClient.uploadAttachment(
            data,
            attachment.name
          );
          // Note: Would need to update issue with attachmentId
          // This is a limitation - attachments added after creation
          attachmentsSynced++;
          log(`  Synced: ${attachment.name}`);
        } catch (error) {
          log(`  Failed to sync: ${attachment.name} - ${error}`);
        }
      }
    }

    return {
      sourceIssue,
      createdIssue,
      subtasks,
      attachmentsSynced,
    };
  }
}
```

2. Update index.ts with full CLI
```typescript
#!/usr/bin/env node
import { Command } from "commander";
import dotenv from "dotenv";
import { SyncService } from "./sync-service.js";

dotenv.config();

function validateEnv(): void {
  const required = [
    "BACKLOG_KH_SPACE",
    "BACKLOG_KH_API_KEY",
    "BACKLOG_INTERNAL_SPACE",
    "BACKLOG_INTERNAL_API_KEY",
    "BACKLOG_INTERNAL_PROJECT_KEY",
    "ANTHROPIC_API_KEY",
  ];

  const missing = required.filter((key) => !process.env[key]);
  if (missing.length > 0) {
    console.error("Missing required environment variables:");
    missing.forEach((key) => console.error(`  - ${key}`));
    console.error("\nCopy .env.example to .env and fill in values.");
    process.exit(1);
  }
}

const program = new Command();

program
  .name("sync-task")
  .description("Sync tasks from Backlog KH to Internal Backlog with translation")
  .version("1.0.0")
  .argument("<ticketId>", "Backlog ticket ID (e.g., HB21373-123)")
  .option("--with-subtasks", "Force create subtasks regardless of task type")
  .option("--no-translate", "Skip translation (keep original Japanese)")
  .option("--dry-run", "Preview sync without creating issues")
  .option("-v, --verbose", "Show detailed progress")
  .action(async (ticketId: string, options) => {
    try {
      validateEnv();

      const service = new SyncService(
        process.env.BACKLOG_KH_SPACE!,
        process.env.BACKLOG_KH_API_KEY!,
        process.env.BACKLOG_INTERNAL_SPACE!,
        process.env.BACKLOG_INTERNAL_API_KEY!,
        process.env.BACKLOG_INTERNAL_PROJECT_KEY!,
        process.env.ANTHROPIC_API_KEY!
      );

      console.log(`\nSyncing ${ticketId}...\n`);

      const result = await service.sync(ticketId, {
        withSubtasks: options.withSubtasks,
        skipTranslation: !options.translate,
        dryRun: options.dryRun,
        verbose: options.verbose,
      });

      // Summary
      console.log("\n--- Sync Complete ---");
      console.log(`Source: ${result.sourceIssue.issueKey}`);
      if (result.createdIssue) {
        console.log(`Created: ${result.createdIssue.issueKey}`);
        console.log(`Subtasks: ${result.subtasks?.length || 0}`);
        console.log(`Attachments: ${result.attachmentsSynced}`);
      } else if (options.dryRun) {
        console.log("[DRY RUN - No issues created]");
      }

      process.exit(0);
    } catch (error) {
      console.error("\nError:", error instanceof Error ? error.message : error);
      if (options.verbose && error instanceof Error) {
        console.error(error.stack);
      }
      process.exit(1);
    }
  });

program.parse();
```

3. Update package.json bin field
```json
{
  "bin": {
    "sync-task": "./dist/index.js"
  }
}
```

## Todo List
- [ ] Create SyncService class
- [ ] Implement full sync workflow
- [ ] Add dry-run support
- [ ] Add verbose logging
- [ ] Update CLI with all options
- [ ] Add environment validation
- [ ] Add summary output
- [ ] Handle attachment sync
- [ ] Test with --dry-run
- [ ] Test with real tickets
- [ ] Test error scenarios

## Success Criteria
- `npm run dev HB21373-123 --dry-run` shows preview
- `npm run dev HB21373-123 -v` shows progress
- `npm run dev HB21373-123` creates issue + subtasks (for Feature Request)
- Exit code 0 on success, 1 on error
- Clear error messages for missing env vars
- Attachments synced correctly

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Partial sync failure | Medium | Log progress, can retry |
| Issue type mismatch | Medium | Fall back to first issue type |
| User not found | Medium | Warn, continue without assignee |
| Attachment too large | Low | Skip with warning |

## Security Considerations
- Validate all env vars before starting
- No sensitive data in logs (unless verbose)
- API keys never exposed in output

## Testing Scenarios

1. **Happy path - Bug**
   - Input: Bug ticket
   - Expected: Issue created, CuongNN assigned, no subtasks

2. **Happy path - Feature Request**
   - Input: Feature Request ticket
   - Expected: Issue created, Duongnh assigned, 10 subtasks created

3. **Dry run**
   - Input: Any ticket with --dry-run
   - Expected: Preview shown, no issues created

4. **Skip translation**
   - Input: Ticket with --no-translate
   - Expected: Original JP text in both sections

5. **Force subtasks**
   - Input: Bug ticket with --with-subtasks
   - Expected: Bug issue with 10 subtasks

6. **Error: missing env**
   - Input: Missing ANTHROPIC_API_KEY
   - Expected: Clear error listing missing vars

7. **Error: invalid ticket**
   - Input: INVALID-999
   - Expected: Backlog API error message

## Next Steps
- User testing with real tickets
- Add `--update` flag to update existing synced issues
- Add webhook listener for automatic sync
