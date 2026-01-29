# Phase 01: Project Setup

## Context Links
- [Brainstorm](../reports/brainstorm-260122-2139-backlog-task-sync-bot.md)
- [Backlog API Research](research/researcher-backlog-api.md)
- [Claude Translation Research](research/researcher-claude-translation.md)

## Overview
- **Priority:** P1 (prerequisite for all phases)
- **Status:** pending
- **Effort:** 0.5h
- **Description:** Initialize project structure, install dependencies, configure environment

## Key Insights
- Use TypeScript for type safety with Backlog API responses
- Store API keys in `.env` (never commit)
- Keep config files separate for easy modification

## Requirements

### Functional
- Project initialized with package.json
- TypeScript configured with strict mode
- Environment variables loaded from `.env`

### Non-Functional
- Build output to `dist/` folder
- ESM modules support

## Architecture

```
experiments/backlog-sync-bot/
├── src/
│   ├── index.ts           # CLI entry point
│   ├── backlog-client.ts  # Backlog API wrapper
│   ├── translator.ts      # Claude translation
│   ├── task-mapper.ts     # Type → Assignee mapping
│   └── template.ts        # Task template builder
├── config/
│   ├── mapping.json       # Type-to-assignee config
│   └── subtasks.json      # Subtask definitions
├── .env.example           # Environment template
├── .gitignore
├── package.json
└── tsconfig.json
```

## Related Code Files

### Create
- `experiments/backlog-sync-bot/package.json`
- `experiments/backlog-sync-bot/tsconfig.json`
- `experiments/backlog-sync-bot/.env.example`
- `experiments/backlog-sync-bot/.gitignore`
- `experiments/backlog-sync-bot/src/index.ts` (placeholder)
- `experiments/backlog-sync-bot/config/mapping.json`
- `experiments/backlog-sync-bot/config/subtasks.json`

## Implementation Steps

1. Create project directory
```bash
mkdir -p experiments/backlog-sync-bot/src experiments/backlog-sync-bot/config
```

2. Initialize package.json
```bash
cd experiments/backlog-sync-bot && npm init -y
```

3. Install dependencies
```bash
npm install @anthropic-ai/sdk commander dotenv
npm install -D typescript @types/node tsx
```

4. Create tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

5. Create .env.example
```env
# Backlog KH (Customer)
BACKLOG_KH_SPACE=hblab
BACKLOG_KH_API_KEY=your_kh_api_key_here

# Backlog Internal
BACKLOG_INTERNAL_SPACE=your_internal_space
BACKLOG_INTERNAL_API_KEY=your_internal_api_key_here
BACKLOG_INTERNAL_PROJECT_KEY=INTERNAL

# Claude AI
ANTHROPIC_API_KEY=your_anthropic_key_here
```

6. Create .gitignore
```
node_modules/
dist/
.env
*.log
```

7. Create config/mapping.json
```json
{
  "taskTypeMapping": {
    "Bug": { "assignee": "CuongNN", "createSubtasks": false },
    "Feature Request": { "assignee": "Duongnh", "createSubtasks": true },
    "Scenario Upload": { "assignee": "Duongnh", "createSubtasks": false },
    "Investigation": { "assignee": "CuongNN", "createSubtasks": false }
  },
  "defaultAssignee": "Duongnh"
}
```

8. Create config/subtasks.json
```json
{
  "subtasks": [
    "Hearing",
    "Create spec file",
    "Review spec file",
    "Design",
    "Coding",
    "Create test case",
    "Do the test case",
    "UAT",
    "Create manual file",
    "Release"
  ]
}
```

9. Create placeholder src/index.ts
```typescript
#!/usr/bin/env node
import { Command } from "commander";
import dotenv from "dotenv";

dotenv.config();

const program = new Command();
program
  .name("sync-task")
  .description("Sync tasks from Backlog KH to Internal Backlog")
  .version("1.0.0")
  .argument("<ticketId>", "Backlog ticket ID (e.g., HB21373-123)")
  .option("--with-subtasks", "Force create subtasks")
  .option("--no-translate", "Skip translation")
  .action(async (ticketId, options) => {
    console.log(`TODO: Sync ticket ${ticketId}`, options);
  });

program.parse();
```

10. Update package.json scripts
```json
{
  "type": "module",
  "scripts": {
    "build": "tsc",
    "dev": "tsx src/index.ts",
    "start": "node dist/index.js"
  }
}
```

## Todo List
- [ ] Create project directory structure
- [ ] Initialize npm project
- [ ] Install production dependencies
- [ ] Install dev dependencies
- [ ] Configure TypeScript
- [ ] Create environment template
- [ ] Create gitignore
- [ ] Create mapping config
- [ ] Create subtasks config
- [ ] Create CLI placeholder
- [ ] Verify build works

## Success Criteria
- `npm run build` compiles without errors
- `npm run dev HB21373-123` outputs placeholder message
- All config files created and valid JSON
- `.env.example` documents all required variables

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing dependency | Low | Use explicit versions in package.json |
| TypeScript config issues | Low | Use proven config template |

## Security Considerations
- `.env` added to `.gitignore`
- `.env.example` contains only placeholder values
- No hardcoded API keys

## Next Steps
→ Proceed to Phase 02: Backlog API Client
