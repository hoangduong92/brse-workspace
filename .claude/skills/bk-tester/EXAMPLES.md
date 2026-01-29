# bk-tester Usage Examples

## Quick Start

### 1. View All Commands

```bash
cd .claude/skills/bk-tester
python scripts/main.py --input tests/fixtures/sample_requirements.md --type all
```

This will display all available generation commands.

## Generate Test Documents

### 2. Generate Test Viewpoints

```bash
# Generate prompt and view it
python scripts/main.py --input requirements.md --type viewpoint

# Generate with Claude
python scripts/main.py --input requirements.md --type viewpoint | claude -p > viewpoints.md
```

### 3. Generate Test Plan

```bash
# With default project name
python scripts/main.py --input requirements.md --type plan | claude -p > test_plan.md

# With custom project name
python scripts/main.py --input requirements.md --type plan --project "ECサイト" | claude -p > test_plan.md
```

### 4. Generate Test Cases

```bash
# Without viewpoints
python scripts/main.py --input requirements.md --type cases | claude -p > test_cases.md

# With viewpoints
python scripts/main.py --input requirements.md --type cases --viewpoints viewpoints.md | claude -p > test_cases.md
```

### 5. Generate Test Report

```bash
# Without test results
python scripts/main.py --input requirements.md --type report | claude -p > test_report.md

# With test results
python scripts/main.py --input requirements.md --type report --results results.txt | claude -p > test_report.md

# With custom project name
python scripts/main.py --input requirements.md --type report --project "認証システム" | claude -p > test_report.md
```

## Complete Workflow

### Step-by-step test documentation generation:

```bash
# 1. Generate test plan
python scripts/main.py --input requirements.md --type plan --project "My Project" | claude -p > test_plan.md

# 2. Extract test viewpoints
python scripts/main.py --input requirements.md --type viewpoint | claude -p > viewpoints.md

# 3. Generate test cases based on viewpoints
python scripts/main.py --input requirements.md --type cases --viewpoints viewpoints.md | claude -p > test_cases.md

# 4. After testing, generate report
python scripts/main.py --input requirements.md --type report --results results.txt --project "My Project" | claude -p > test_report.md
```

## Sample Input

### requirements.md

```markdown
# ユーザー認証機能 要件定義

## REQ-001: ログイン機能

### 概要
ユーザーがメールアドレスとパスワードを使用してシステムにログインできる機能を提供する。

### 機能要件
1. ユーザーはメールアドレスとパスワードを入力してログインできる
2. パスワードは8文字以上の英数字を含む必要がある
3. ログインに3回失敗した場合、アカウントを30分間ロックする
4. ログイン成功時、セッショントークンを発行する
5. セッションの有効期限は24時間とする

### 非機能要件
1. ログイン処理は3秒以内に完了すること
2. パスワードはハッシュ化して保存すること
3. ログイン試行はログに記録すること
```

### results.txt (optional, for test report)

```markdown
# テスト実施結果

## 実施状況
- 実施期間: 2024/01/15 - 2024/01/20
- 総テストケース数: 50
- 実施完了: 48
- 合格: 45
- 不合格: 3

## 不具合
- BUG-001: ログイン3回失敗時のロック機能が動作しない（優先度：高）
- BUG-002: パスワードリセットメール送信が遅い（優先度：中）
- BUG-003: セッション有効期限が24時間より短い（優先度：中）
```

## Sample Output Structure

### Viewpoints Output (viewpoints.md)

```markdown
## 機能テスト

### FT-001: ログイン成功確認
- **目的**: 正しい認証情報でログインできることを確認
- **確認項目**: メールアドレスとパスワードでログイン可能
- **優先度**: 高

### FT-002: セッション発行確認
- **目的**: ログイン成功時にセッションが発行されることを確認
- **確認項目**: セッショントークンの発行と有効期限
- **優先度**: 高

## 境界値テスト

### BT-001: パスワード最小文字数
- **目的**: パスワードの最小文字数制約を確認
- **確認項目**: 8文字未満のパスワードが拒否されること
- **優先度**: 中

## 異常系テスト

### ET-001: ログイン失敗ロック
- **目的**: 3回失敗時のアカウントロック機能を確認
- **確認項目**: 3回連続失敗で30分間ロック
- **優先度**: 高
```

### Test Cases Output (test_cases.md)

```markdown
| テストケースID | 分類 | テスト項目 | 前提条件 | テスト手順 | 期待結果 | 優先度 |
|----------------|------|------------|----------|------------|----------|--------|
| TC-001 | 機能テスト | ログイン成功 | ユーザー登録済み | 1. メールアドレス入力<br>2. パスワード入力<br>3. ログインボタン押下 | ダッシュボード画面に遷移 | 高 |
| TC-002 | 境界値テスト | パスワード7文字 | - | 1. メールアドレス入力<br>2. 7文字のパスワード入力<br>3. ログインボタン押下 | エラーメッセージ表示 | 中 |
| TC-003 | 異常系テスト | 3回失敗ロック | ユーザー登録済み | 1. 誤ったパスワードで3回ログイン試行<br>2. 正しいパスワードでログイン試行 | ロックメッセージ表示 | 高 |
```

## Tips

1. **Use descriptive project names** to generate context-specific documentation
2. **Generate viewpoints first** before test cases for better coverage
3. **Include test results** when generating reports for accurate metrics
4. **Review and edit** the AI-generated output to match your project needs
5. **Save intermediate outputs** (viewpoints) for reuse in test case generation

## Troubleshooting

### UTF-8 Encoding Issues on Windows

If you see encoding errors, make sure you're running the script directly (not importing it in Python REPL):

```bash
# Correct
python scripts/main.py --input req.md --type plan

# May have issues
python
>>> import main
```

### Empty Output

If the output is empty, check that:
- Input file exists and has content
- File encoding is UTF-8
- Requirements are in Japanese or have clear structure

### Test Results Not Included

When generating reports, make sure:
- The `--results` parameter points to an existing file
- Results file has UTF-8 encoding
- Results file contains Japanese text in expected format