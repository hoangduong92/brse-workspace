# Claude Code Skill Development Research

## Skill Structure & Format

### SKILL.md Schema
```yaml
---
name: skill-name              # Required: lowercase, hyphens
description: Under 200 chars # Required: specific use cases
license: MIT                 # Optional
version: 1.0.0             # Optional
---
```

### Directory Structure
```
skill-name/
├── SKILL.md (< 100 lines)
├── scripts/          # Executable code (Python/Node)
├── references/       # Documentation (< 100 lines each)
├── assets/          # Template files, images
└── .env.example      # Required environment variables
```

## Slash Command Patterns

### Command Definition
Skills are activated via metadata matching:
- `name` determines the command identifier
- `description` triggers skill activation when user query matches

### Parameter Handling
```markdown
# Primary workflow
ALWAYS execute scripts in this order:
node scripts/detect-topic.js "<user query>"
node scripts/fetch-docs.js "<user query>"
cat llms.txt | node scripts/analyze-llms-txt.js -
```

## Python Script Integration

### Environment Variable Priority
```python
# Order: process.env > skill/.env > skills/.env > project/.env
def get_api_key_or_exit():
    sources = [
        os.getenv('GEMINI_API_KEY'),
        # Check cascading .env files...
    ]
```

### Script Requirements
- Use virtual environment: `.claude/skills/.venv/Scripts/python.exe`
- Include `requirements.txt` for dependencies
- Write comprehensive tests
- Respect error handling patterns

## Error Handling Patterns

### Script Error Management
```javascript
// Node.js pattern
try {
    const result = await fetchDocs(query);
    return result;
} catch (error) {
    console.error('Fetch failed:', error.message);
    return fallbackStrategy(query);
}
```

### Cascading Fallbacks
1. Topic-specific search
2. General library search
3. Repository analysis
4. Error message with guidance

## Environment Management

### .env File Structure
```env
# API Keys
CONTEXT7_API_KEY=
GEMINI_API_KEY=
GITHUB_TOKEN=

# Configuration
OUTPUT_FORMAT=json
DEBUG=false
GEMINI_USE_VERTEX=true
VERTEX_PROJECT_ID=
```

### Multi-Environment Support
- AI Studio (default)
- Vertex AI (Google Cloud)
- Automatic client selection

## Best Practices

### Progressive Disclosure
- SKILL.md: < 100 lines, quick reference
- references/: Detailed docs, loaded on demand
- scripts/: Executable without context loading

### Writing Style
- Imperative form: "Execute scripts in this order"
- Third-person: "This skill should be used when..."
- Specific descriptions under 200 chars

### File Organization
- Split files > 100 lines
- Use grep patterns in SKILL.md for large files
- Separate assets from documentation

## Reference Skills

### Existing Skills as Examples
1. **docs-seeker** - Script-first workflow
   - Zero-token execution
   - Automatic URL construction
   - Agent distribution recommendations

2. **skill-creator** - Meta-skill guidance
   - Progressive disclosure principles
   - Package validation
   - Iteration workflow

3. **common/** - Shared utilities
   - Standardized API key handling
   - Multi-environment support
   - Error handling patterns

### Script Patterns
```javascript
// Detect + Fetch + Analyze workflow
const detect = detectTopic(query);
const docs = fetchDocs(detect);
const analysis = analyzeDocs(docs);
```

## Testing Requirements

### Test Coverage
- Unit tests for each script
- Integration tests for workflows
- Manual testing with real use cases

### Test Commands
```json
{
  "test": "node scripts/tests/run-tests.js",
  "test:detect": "node scripts/tests/test-detect-topic.js",
  "test:fetch": "node scripts/tests/test-fetch-docs.js"
}
```

## Package Management

### Dependencies
- Node.js: >= 14.0.0
- Python: Use virtual environment
- System tools: FFmpeg, ImageMagick (if needed)

### Distribution
- Package validation before distribution
- Zip file with proper directory structure
- Version control via package.json