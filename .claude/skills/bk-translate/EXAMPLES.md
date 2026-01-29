# bk-translate Examples

Practical examples of using bk-translate for JA↔VI translation.

## Quick Start

### 1. Simple Translation

```bash
# Japanese → Vietnamese
python scripts/main.py --text "バグを修正しました" | claude -p

# Output from Claude:
# "Đã sửa lỗi"
```

### 2. File Translation

```bash
# Translate a file
python scripts/main.py --file bug-report.txt | claude -p
```

### 3. Custom Glossary

```bash
# Use project-specific glossary
python scripts/main.py --text "マイルストーンを達成" --glossary glossaries/project-x.json | claude -p
```

## Real-World Scenarios

### Scenario 1: Bug Report Translation

**Input (Japanese):**
```
バグを修正しました。

再現手順:
1. `npm install`を実行
2. テストを実施: `npm test`
3. エラーが発生

修正内容:
```javascript
function validateInput(data) {
  if (!data) throw new Error('Invalid input');
  return true;
}
```

詳細: https://github.com/team/repo/issues/123
```

**Command:**
```bash
python scripts/main.py --file bug-report.txt | claude -p
```

**Generated Prompt (before Claude):**
```
You are a professional Japanese↔Vietnamese translator for IT projects.

## Glossary (MUST use these exact translations):
バグ → lỗi
テスト → kiểm thử
修正 → sửa
エラー → lỗi

## Preserved Elements (DO NOT translate):
- 3 code block(s): [CODE_0], [CODE_1], [CODE_2]
- 1 URL(s): [URL_0]

## Instructions:
- Translate from Japanese to Vietnamese
- Use glossary terms exactly as specified
- Preserve all [CODE_N] and [URL_N] placeholders exactly as they appear
- Maintain the same formatting and structure

## Text to Translate:
バグを修正しました。

再現手順:
1. [CODE_0]を実行
2. テストを実施: [CODE_1]
3. エラーが発生

修正内容:
[CODE_2]

詳細: [URL_0]
```

**Claude Output (Vietnamese):**
```
Đã sửa lỗi.

Các bước tái hiện:
1. Chạy `npm install`
2. Thực hiện kiểm thử: `npm test`
3. Lỗi xảy ra

Nội dung sửa:
```javascript
function validateInput(data) {
  if (!data) throw new Error('Invalid input');
  return true;
}
```

Chi tiết: https://github.com/team/repo/issues/123
```

### Scenario 2: Release Notes Translation

**Input (Vietnamese):**
```
Phát hành v2.0.0

Thay đổi:
- Sửa lỗi xác thực
- Cải thiện hiệu năng API
- Thêm tài liệu tại https://docs.example.com
- Chạy `npm run build` để build

Chi tiết kỹ thuật:
```typescript
interface Config {
  apiKey: string;
  timeout: number;
}
```
```

**Command:**
```bash
python scripts/main.py --file release-notes.txt | claude -p
```

**Claude Output (Japanese):**
```
v2.0.0 リリース

変更内容:
- 認証のバグを修正
- APIのパフォーマンスを改善
- ドキュメントを追加: https://docs.example.com
- ビルドするには`npm run build`を実行

技術詳細:
```typescript
interface Config {
  apiKey: string;
  timeout: number;
}
```
```

### Scenario 3: Project-Specific Glossary

**Create glossary:** `glossaries/ecommerce.json`
```json
{
  "カート": "giỏ hàng",
  "チェックアウト": "thanh toán",
  "在庫": "tồn kho",
  "配送": "giao hàng",
  "決済": "thanh toán"
}
```

**Input:**
```
カートに商品を追加しました。
チェックアウト処理を実装中です。
在庫確認API: https://api.example.com/inventory
```

**Command:**
```bash
python scripts/main.py --text "カートに商品を追加しました。チェックアウト処理を実装中です。" --glossary glossaries/ecommerce.json | claude -p
```

**Output:**
```
Đã thêm sản phẩm vào giỏ hàng.
Đang triển khai quy trình thanh toán.
```

### Scenario 4: Code Review Comments

**Input (Japanese):**
```
レビューコメント:

1. `getUserData()`の実装を確認してください
2. エラーハンドリングが不足しています
3. テストケースを追加: https://docs.testing.com/guide

推奨コード:
```python
try:
    user = get_user_data(user_id)
except ValueError as e:
    logger.error(f"Error: {e}")
```
```

**Command:**
```bash
python scripts/main.py --file code-review.txt | claude -p
```

**Output (Vietnamese):**
```
Nhận xét đánh giá:

1. Vui lòng xác nhận triển khai của `getUserData()`
2. Thiếu xử lý lỗi
3. Thêm test case: https://docs.testing.com/guide

Code đề xuất:
```python
try:
    user = get_user_data(user_id)
except ValueError as e:
    logger.error(f"Error: {e}")
```
```

## Advanced Usage

### Batch Translation with Shell Script

**translate-batch.sh:**
```bash
#!/bin/bash

for file in docs/ja/*.md; do
  filename=$(basename "$file" .md)
  python scripts/main.py --file "$file" | claude -p > "docs/vi/${filename}.md"
  echo "Translated: $filename"
done
```

### Custom Workflow Integration

**In CI/CD Pipeline:**
```yaml
# .github/workflows/translate.yml
name: Auto-translate docs

on:
  push:
    paths:
      - 'docs/ja/**'

jobs:
  translate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Translate to Vietnamese
        run: |
          python .claude/skills/bk-translate/scripts/main.py \
            --file docs/ja/README.md | \
            claude -p > docs/vi/README.md
```

### Interactive Translation with Preview

```bash
# Preview translation prompt before sending to Claude
python scripts/main.py --text "テスト" > prompt.txt
cat prompt.txt  # Review prompt
cat prompt.txt | claude -p  # Send to Claude
```

## Tips & Best Practices

### 1. Preserve Technical Terms

Use glossary to ensure consistency:
```json
{
  "API": "API",
  "endpoint": "endpoint",
  "webhook": "webhook",
  "token": "token"
}
```

### 2. Handle Mixed Content

Input with Japanese, English, code, and URLs works seamlessly:
```
APIエンドポイント https://api.example.com/v1/users は
`GET /users/:id` で実装されています。
```

### 3. Maintain Formatting

Markdown, lists, and code blocks preserve structure:
```markdown
## バグ修正

- [x] エラーハンドリング追加
- [ ] テスト作成

コード:
```js
const fix = () => true;
```
```

### 4. Version Control Glossaries

Keep glossaries in git for team consistency:
```
glossaries/
├── default-it-terms.json     # General IT terms
├── project-backend.json      # Backend-specific terms
├── project-frontend.json     # Frontend-specific terms
└── client-domain.json        # Client business domain
```

## Troubleshooting

### Issue: Unicode Characters Not Displaying

**Solution:** Ensure terminal supports UTF-8:
```bash
# Windows PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Windows CMD
chcp 65001
```

### Issue: Glossary Not Loading

**Solution:** Check glossary path is relative to skill root:
```bash
# Correct
--glossary glossaries/my-terms.json

# Incorrect
--glossary /absolute/path/glossaries/my-terms.json
```

### Issue: Code Blocks Not Preserved

**Solution:** Use triple backticks or inline backticks:
```markdown
Correct: `npm test`
Correct:
```bash
npm test
```

Incorrect: npm test (without backticks)
```

## Performance Tips

1. **Large files:** Split into smaller chunks
2. **Batch processing:** Use shell loops with delays
3. **Glossary size:** Keep under 100 terms for optimal prompt size
4. **Caching:** Save translations to avoid re-translating same content
