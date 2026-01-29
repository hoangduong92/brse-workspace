"""
TestCaseGenerator: Generate test cases from requirements and viewpoints.
"""


def build_test_case_prompt(requirements: str, viewpoints: str = None) -> str:
    """
    Build a prompt for generating test cases.

    Args:
        requirements: The requirement document content
        viewpoints: Optional viewpoints document (if already extracted)

    Returns:
        A prompt string for claude -p
    """
    viewpoint_section = ""
    if viewpoints:
        viewpoint_section = f"""
# テスト観点

{viewpoints}
"""

    prompt = f"""以下の要件定義書を基に、詳細なテストケース一覧を生成してください。

# 要件定義書

{requirements}
{viewpoint_section}
# 指示

各機能について、以下の観点を含むテストケースを作成してください：
- 機能テスト（正常系）
- 境界値テスト
- 異常系テスト
- セキュリティテスト

# 出力形式

以下のMarkdownテーブル形式で出力してください：

```
| テストケースID | 分類 | テスト項目 | 前提条件 | テスト手順 | 期待結果 | 優先度 |
|----------------|------|------------|----------|------------|----------|--------|
| TC-001 | 機能テスト | ログイン成功 | ユーザー登録済み | 1. メールアドレス入力<br>2. パスワード入力<br>3. ログインボタン押下 | ダッシュボード画面に遷移 | 高 |
```

**重要な注意事項:**
- テストケースIDは連番で採番（TC-001, TC-002...）
- 分類は「機能テスト」「境界値テスト」「異常系テスト」「セキュリティテスト」のいずれか
- テスト手順は具体的に記述（「〜を確認」ではなく「〜を入力」「〜を押下」など）
- 期待結果は明確に記述
- 優先度は「高」「中」「低」のいずれか
"""
    return prompt


def generate_test_cases(requirements: str, viewpoints: str = None) -> str:
    """
    Generate a prompt for creating test cases.

    Args:
        requirements: The requirement document content
        viewpoints: Optional viewpoints document

    Returns:
        Prompt string ready for `claude -p`
    """
    return build_test_case_prompt(requirements, viewpoints)
