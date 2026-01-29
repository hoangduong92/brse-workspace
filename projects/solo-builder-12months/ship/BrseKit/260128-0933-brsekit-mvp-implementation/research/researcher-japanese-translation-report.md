# Japanese Business Writing & IT Translation Research

**Report Date:** 2026-01-28
**Status:** Complete
**Language:** Vietnamese

---

## 1. Existing Infrastructure Analysis

### Backlog Skill Foundation
Codebase đã có **language detector + translation framework** sẵn:
- Language detector: Hiragana (3040-309F), Katakana (30A0-30FF), Kanji (4E00-9FBF)
- Vietnamese diacritics: àáạảã...đ (unique pattern)
- Translation rules: Preserve code blocks, URLs, technical terms, issue IDs, file paths
- Keigo levels được handle qua task type detection (feature/scenario/issue)

**Found in:** `.claude/skills/backlog/scripts/language_detector.py`

---

## 2. Japanese Business Writing Patterns (Keigo Levels)

### 2.1 Email Templates (Client Communication)

**敬語レベル (Keigo Levels):**
- **Casual (Plain)**: Team internal communication
- **Polite (丁寧)**: Regular client emails - add ます/ました endings
- **Honorific (敬語)**: Senior management, external partners

**Template Pattern:**
```
件名: [Issue/Feature] + ID (e.g., "新機能: ユーザー認証機能の実装について")
本文構成:
1. 冒頭挨拶 (3-4 words): お疲れ様です。
2. 本件説明 (3-5 lines): 主張、背景、目的
3. 対応予定 (2-3 items): 箇条書き
4. 確認依頼: ご確認よろしくお願いいたします。
```

### 2.2 Report Writing Conventions

**進捗報告 (Progress Report):**
- 数値重視: 完了率 XX%, 対象タスク YY件
- 結果先行: 最初に成功/失敗を述べる
- 経過説明: 具体的な数字・日付
- 課題提示: ボトルネック、リスク明確化
- 推奨アクション: 次のステップ

**Common Progress Phrases:**
- 完了いたしました (completed - honorific)
- 予定通り進んでおります (progressing as planned)
- 若干の遅延が予想されます (slight delay expected)
- 詳細は別途ご報告いたします (detailed report to follow)

### 2.3 Common IT Phrases

| Category | Japanese | Context |
|----------|----------|---------|
| **Status** | デプロイ完了 | Deployment done |
| | テスト中 | Testing in progress |
| | レビュー待ち | Awaiting review |
| **Issues** | バグが発生しました | Bug occurred |
| | パフォーマンス低下 | Performance degradation |
| | セキュリティ脆弱性 | Security vulnerability |
| **Features** | 実装予定 | Planned for implementation |
| | 要件定義中 | Requirements definition |
| | 仕様書作成 | Creating specification |

---

## 3. JA ↔ VI Translation for IT Context

### 3.1 Technical Terminology Handling

**Strategy:** Create **per-domain glossaries** to ensure consistency

**Core IT Terms (Always Preserve in Translation):**
```
API/REST/GraphQL → API/REST/GraphQL (unchanged)
Database/Schema → Database/Schema (preserve)
Authentication/Authorization → Authentication/Authorization
Feature/Bug/Epic → Feature/Bug/Epic
Deployment/Release → Deployment/Release
```

**Problem Terms (Need Context):**
- 実装 (implementation) → có thể là "implementation", "coding", "development"
- 対応 (handling) → "address", "handle", "support", "implement"
- 要件 (requirement) → "requirement", "specification", "constraint"

### 3.2 Project Glossary Structure

**Location:** `.claude/skills/backlog/glossaries/ja-vi-it-glossary.json`

**Format:**
```json
{
  "domain": "IT-Project",
  "version": "1.0",
  "entries": [
    {
      "japanese": "バックエンド開発",
      "vietnamese": "Phát triển Backend",
      "category": "feature",
      "context": "API implementation"
    },
    {
      "japanese": "デバッグ",
      "vietnamese": "Gỡ lỗi",
      "category": "activity",
      "synonyms": ["トラブルシューティング"]
    }
  ]
}
```

### 3.3 Translation Memory (TM) Best Practices

**Implementation Approach:**
1. **Segment-based**: Store sentence/phrase pairs, not entire documents
2. **Context tagging**: Mark technical vs. business vs. documentation
3. **Version control**: Track glossary changes with dates
4. **Quality metrics**: Fuzzy match (100%, 75-99%, <75%) to detect inconsistencies

**Tools Already Integrated:**
- Language detector → identifies JA/VI automatically
- Pattern preservation → URLs, file paths, code blocks untouched
- Template engine → task type-specific translation rules

---

## 4. Backlog Skill Translation Rules (Existing)

**Already implemented:**
- Preserve: code blocks, URLs, technical terms, issue IDs, file paths
- Natural translation (NOT word-by-word)
- Markdown formatting maintained
- Keyword-based task type detection (feature/scenario/issue)

**Recommended Extension:**
- Add glossary lookup before in-conversation translation
- Log all translations → build translation memory incrementally
- Add confidence scoring for fuzzy matches

---

## 5. Recommendations for PAA MVP

### 5.1 Business Writing Layer
Create template system:
```
/templates/ja-email-client.md → Honorific, external format
/templates/ja-email-internal.md → Polite, internal format
/templates/ja-report-progress.md → Status-focused format
```

### 5.2 Translation Enhancement
Extend backlog skill:
- Add glossary lookup (ja-vi-it-glossary.json)
- Implement TM logging for future consistency
- Add confidence scoring for untranslated terms

### 5.3 Documentation
Create project-specific glossary as living doc in `./docs/ja-vi-glossary.md`

---

## Unresolved Questions
- What is PAA MVP scope? (Personal AI Assistant use case?)
- Should glossary be shared across all Backlog projects or per-project?
- Translation memory - store in JSON or database?
