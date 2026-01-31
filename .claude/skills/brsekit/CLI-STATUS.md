# BrseKit CLI - Implementation Status

_Last updated: 2026-01-31_

## Overview

BrseKit CLI (`bk`) là công cụ command-line để bootstrap và update BrseKit projects, theo mô hình Freemium giống ClaudeKit.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  PUBLIC                                                     │
│  brsekit-cli (npm)                                          │
│  - CLI tool để download/install                             │
│  - Commands: bk init, bk doctor, bk version                 │
│  - Ai cũng có thể cài                                       │
└─────────────────────────────┬───────────────────────────────┘
                              │ cần access để download
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  PRIVATE                                                    │
│  brsekit-starter (GitHub)                                   │
│  - Skills: bk-track, bk-capture, bk-spec, bk-recall, etc.   │
│  - Chỉ ai được invite mới access được                       │
│  - Download từ GitHub releases                              │
└─────────────────────────────────────────────────────────────┘
```

## Distribution

| Resource | Type | URL | Status |
|----------|------|-----|--------|
| npm package | Public | https://www.npmjs.com/package/brsekit-cli | ✅ Published v1.0.0 |
| brsekit-cli | Public | https://github.com/brsekit/brsekit-cli | ✅ Created |
| brsekit-starter | Private | https://github.com/brsekit/brsekit-starter | ✅ Created |

**Releases:**
- npm: brsekit-cli@1.0.0
- GitHub: https://github.com/brsekit/brsekit-starter/releases/tag/v1.0.0

## CLI Commands

| Command | Description | Status |
|---------|-------------|--------|
| `bk init` | Install/update BrseKit | ✅ Working |
| `bk doctor` | Health check | ✅ Working |
| `bk version` | Show versions | ✅ Working |
| `bk --help` | Help | ✅ Working |

### `bk init` Options

```
bk init [options]
  --dir <dir>              Target directory (default: current)
  -r, --release <version>  Use specific version (e.g., latest, v1.0.0)
  -g, --global             Install to ~/.claude (user-level)
  --fresh                  Clean reinstall
  -y, --yes                Non-interactive mode
  --beta                   Show beta versions
  -v, --verbose            Enable verbose logging
```

### `bk init` Phases

1. **Options resolution** - Validate CLI args
2. **Authentication** - Check GitHub access (gh CLI)
3. **Selection** - Choose version (interactive or --release)
4. **Download** - Fetch from GitHub releases
5. **Extract** - Unzip to temp directory
6. **Merge** - Copy to `.claude/skills/`, preserve customizations
7. **Post-install** - Generate .env, run install scripts

## Local Development

Source code: `experiments/brsekit-cli/`

```bash
# Build
cd experiments/brsekit-cli
npm install
npm run build

# Link globally
npm link

# Test
bk --help
bk doctor
bk init --release v1.0.0 -y
```

## Skills Included (v1.0.0)

| Skill | Description |
|-------|-------------|
| bk-track | Project tracking, weekly reports (PPTX) |
| bk-capture | Task & meeting parsing |
| bk-spec | Requirement analysis, test docs |
| bk-recall | Memory layer, semantic search |
| bk-convert | JA↔VI translation |
| bk-init | Setup wizard |
| bk-morning | Morning brief |
| bk-write | Japanese documents |
| brsekit | Help & documentation |

## Usage Flow

```bash
# 1. Install CLI (public, anyone can do)
npm install -g brsekit-cli

# 2. Init BrseKit (requires GitHub access)
bk init

# 3. Configure credentials
# Edit .claude/skills/.env

# 4. Verify
bk doctor
```

## TODO / Future Work

- [x] Publish to npm (`npm publish`) ✅ Done 2026-01-31
- [ ] Setup GitHub Actions for auto-release
- [ ] Add `bk update` command to update CLI itself
- [ ] Add `bk sync` for config sync
- [ ] Support offline installation (`--archive`)
- [ ] Add telemetry/analytics

## Technical Notes

### Windows ESM Compatibility

`bin/bk.js` uses `pathToFileURL()` to convert Windows paths to file:// URLs for ESM import compatibility.

### Authentication Flow

```
1. Check `gh auth status`
   ↓ (if authenticated)
   Use gh CLI token
   ↓ (if not)
2. Check GITHUB_TOKEN env var
   ↓ (if set)
   Use env token
   ↓ (if not)
3. Prompt user to run `gh auth login`
```

### Protected Files

Files not overwritten during updates:
- `.env`, `.env.local`
- `*.key`, `*.pem`
- `node_modules/`, `.git/`
- `__pycache__/`, `.pytest_cache/`

## References

- ClaudeKit CLI (inspiration): https://github.com/mrgoonie/claudekit-cli
- npm package: claudekit-cli
- Architecture: Phase-based execution with context pattern
