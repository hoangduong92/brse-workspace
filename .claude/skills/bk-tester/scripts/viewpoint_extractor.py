"""
ViewpointExtractor: Extract test viewpoints from requirement documents.
"""

CATEGORIES = {
    "functional": "機能テスト",
    "boundary": "境界値テスト",
    "error": "異常系テスト",
    "security": "セキュリティテスト",
    "performance": "性能テスト"
}


def build_extraction_prompt(requirements: str) -> str:
    """
    Build a prompt for extracting test viewpoints from requirements.

    Args:
        requirements: The requirement document content

    Returns:
        A prompt string for claude -p
    """
    prompt = f"""以下の要件定義書を分析し、テスト観点を抽出してください。

# 要件定義書

{requirements}

# 指示

以下のカテゴリに分けてテスト観点を抽出してください：

1. **機能テスト**: 仕様通りに動作するか確認する観点
2. **境界値テスト**: 入力値の境界値を確認する観点
3. **異常系テスト**: エラーハンドリングを確認する観点
4. **セキュリティテスト**: セキュリティ上の問題を確認する観点
5. **性能テスト**: パフォーマンスを確認する観点

# 出力形式

各観点について、以下の形式で出力してください：

```
## [カテゴリ名]

### [観点ID]: [観点名]
- **目的**: [テストの目的]
- **確認項目**: [具体的な確認内容]
- **優先度**: [高/中/低]
```

明確で具体的なテスト観点を抽出してください。
"""
    return prompt


def parse_viewpoints(output: str) -> list:
    """
    Parse viewpoints from Claude's output.

    Args:
        output: The raw output from Claude

    Returns:
        List of viewpoint dictionaries
    """
    viewpoints = []
    lines = output.split('\n')
    current_category = None
    current_viewpoint = None

    for line in lines:
        line = line.strip()

        # Category header
        if line.startswith('## '):
            current_category = line[3:].strip()

        # Viewpoint header
        elif line.startswith('### '):
            if current_viewpoint:
                viewpoints.append(current_viewpoint)

            # Parse "### [ID]: [Title]"
            header = line[4:].strip()
            parts = header.split(':', 1)
            viewpoint_id = parts[0].strip()
            title = parts[1].strip() if len(parts) > 1 else ""

            current_viewpoint = {
                'id': viewpoint_id,
                'category': current_category or "その他",
                'title': title,
                'purpose': "",
                'items': "",
                'priority': ""
            }

        # Viewpoint details
        elif current_viewpoint and line.startswith('- **'):
            if '目的' in line:
                current_viewpoint['purpose'] = line.split(':', 1)[1].strip() if ':' in line else ""
            elif '確認項目' in line:
                current_viewpoint['items'] = line.split(':', 1)[1].strip() if ':' in line else ""
            elif '優先度' in line:
                current_viewpoint['priority'] = line.split(':', 1)[1].strip() if ':' in line else ""

    # Add last viewpoint
    if current_viewpoint:
        viewpoints.append(current_viewpoint)

    return viewpoints


def extract_viewpoints(requirements: str) -> str:
    """
    Generate a prompt for extracting viewpoints.

    Args:
        requirements: The requirement document content

    Returns:
        Prompt string ready for `claude -p`
    """
    return build_extraction_prompt(requirements)
