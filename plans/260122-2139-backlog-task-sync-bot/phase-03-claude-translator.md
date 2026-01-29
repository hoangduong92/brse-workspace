# Phase 03: Claude Translator

## Context Links
- [Claude Translation Research](research/researcher-claude-translation.md)
- [Phase 02: Backlog API Client](phase-02-backlog-api-client.md)

## Overview
- **Priority:** P1 (core functionality)
- **Status:** pending
- **Effort:** 1h
- **Description:** Implement Japanese-Vietnamese translation using Claude Sonnet 4.5

## Key Insights
- Claude Sonnet 4.5: best balance of quality/cost (~$0.055 per 500 words)
- Auto-detects source language; explicit target improves reliability
- Preserves code blocks, URLs, and technical terms automatically
- Use temp=0.2 for consistent translations
- Exponential backoff for rate limits

## Requirements

### Functional
- Translate Japanese to Vietnamese
- Translate Vietnamese to Japanese (if needed)
- Preserve markdown formatting
- Keep code snippets, URLs, emails unchanged

### Non-Functional
- Response time < 10s for typical task descriptions
- Retry on failure (max 3 attempts)
- Clear error messages

## Architecture

```typescript
// Translator class structure
class Translator {
  constructor(apiKey: string)

  translate(text: string, targetLang: "vi" | "ja"): Promise<string>
  translateToVietnamese(text: string): Promise<string>
  translateToJapanese(text: string): Promise<string>
}
```

## Related Code Files

### Create
- `experiments/backlog-sync-bot/src/translator.ts`

### Modify
- `experiments/backlog-sync-bot/src/index.ts` (import translator)

## Implementation Steps

1. Create translator.ts
```typescript
import Anthropic from "@anthropic-ai/sdk";

export class Translator {
  private client: Anthropic;
  private model = "claude-sonnet-4-5-20250514";

  constructor(apiKey: string) {
    this.client = new Anthropic({ apiKey });
  }

  private systemPrompt = `You are a professional translator specializing in Japanese and Vietnamese.
Rules:
- Translate accurately while preserving meaning and tone
- Keep code snippets, URLs, and technical terms unchanged
- Preserve markdown formatting (headers, lists, code blocks)
- Use formal business language
- Return ONLY the translated text, no explanations`;

  async translate(
    text: string,
    targetLang: "vi" | "ja"
  ): Promise<string> {
    const targetName = targetLang === "vi" ? "Vietnamese" : "Japanese";

    return this.translateWithRetry(text, targetName);
  }

  async translateToVietnamese(text: string): Promise<string> {
    return this.translate(text, "vi");
  }

  async translateToJapanese(text: string): Promise<string> {
    return this.translate(text, "ja");
  }

  private async translateWithRetry(
    text: string,
    targetLang: string,
    maxRetries = 3
  ): Promise<string> {
    // Skip empty or whitespace-only text
    if (!text.trim()) {
      return text;
    }

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const response = await this.client.messages.create({
          model: this.model,
          max_tokens: 4000,
          temperature: 0.2,
          system: this.systemPrompt,
          messages: [
            {
              role: "user",
              content: `Translate the following text to ${targetLang}:\n\n${text}`,
            },
          ],
        });

        const content = response.content[0];
        if (content.type !== "text") {
          throw new Error("Unexpected response type");
        }

        const translated = content.text.trim();
        if (!translated) {
          throw new Error("Empty translation received");
        }

        return translated;
      } catch (error) {
        console.error(`Translation attempt ${attempt} failed:`, error);

        if (attempt === maxRetries) {
          throw new Error(
            `Translation failed after ${maxRetries} attempts: ${error}`
          );
        }

        // Exponential backoff: 2s, 4s, 8s
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }

    throw new Error("Translation failed");
  }
}
```

2. Add convenience function for direct use
```typescript
// Add to translator.ts
export async function translateText(
  text: string,
  targetLang: "vi" | "ja"
): Promise<string> {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error("ANTHROPIC_API_KEY not set");
  }

  const translator = new Translator(apiKey);
  return translator.translate(text, targetLang);
}
```

3. Export from module
```typescript
export { Translator, translateText } from "./translator.js";
```

## Todo List
- [ ] Create Translator class
- [ ] Implement translate method with target language
- [ ] Add convenience methods (translateToVietnamese, translateToJapanese)
- [ ] Implement retry logic with exponential backoff
- [ ] Add input validation (skip empty text)
- [ ] Handle API errors gracefully
- [ ] Test with sample Japanese text
- [ ] Verify markdown preservation

## Success Criteria
- Translates Japanese text to Vietnamese accurately
- Preserves code blocks and URLs in translation
- Retries automatically on failure
- Handles empty input gracefully
- TypeScript compiles without errors
- Works with real Anthropic API

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limit | Medium | Exponential backoff |
| Poor translation quality | Medium | Use formal prompt, review output |
| API key invalid | High | Fail fast with clear error |
| Large text exceeds tokens | Low | 4000 max_tokens sufficient for tasks |

## Security Considerations
- API key from environment variable only
- Never log sensitive content
- Input sanitization (trim whitespace)

## Next Steps
→ Proceed to Phase 04: Task Mapper & Template
